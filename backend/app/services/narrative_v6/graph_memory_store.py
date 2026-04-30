from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from threading import RLock

from alpha_autopilot import ArtifactStore

from ...core.config import settings
from .schemas import GraphMemoryRecord, GraphRAGHit


_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{1,6}")
_DEFAULT_SOURCE_WEIGHTS = {
    "/api/narrative/v6/graph/retrieve": 1.15,
    "/api/narrative/v6/simulations/parallel": 1.05,
    "/api/narrative/v6/characters/{character_id}/interview": 1.0,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class PersistentGraphMemoryStore:
    path: Path
    audit_path: Path | None = None
    max_in_memory_rows: int = 5000
    max_age_hours: int | None = 168
    chapter_window: int = 20
    min_token_overlap: float = 0.2
    compaction_max_rows: int = 5000
    audit_max_rows: int = 500
    audit_expired_rate_threshold: float = 0.25
    audit_duplicate_groups_threshold: int = 10
    audit_active_drop_rate_threshold: float = 0.5
    source_weights: dict[str, float] = field(default_factory=dict)
    _rows: list[GraphMemoryRecord] = field(default_factory=list, init=False)
    _lock: RLock = field(default_factory=RLock, init=False)

    def __post_init__(self) -> None:
        self._rows = self._load_from_disk()

    def append_hits(
        self,
        *,
        query: str,
        hits: list[GraphRAGHit],
        source_route: str,
        chapter_index: int | None = None,
        simulation_id: str | None = None,
    ) -> None:
        query_text = query.strip()
        if not query_text or not hits:
            return
        query_tokens = self._tokens(query_text)
        created_at = _now_iso()

        with self._lock:
            for index, hit in enumerate(hits):
                record = GraphMemoryRecord(
                    record_id=f"gm-{created_at}-{index}",
                    query=query_text,
                    query_tokens=query_tokens,
                    source_route=source_route,
                    chapter_index=chapter_index,
                    simulation_id=simulation_id,
                    node_id=hit.node_id,
                    node_type=hit.node_type,
                    summary=hit.summary,
                    evidence=hit.evidence,
                    score=round(max(0.0, min(1.0, hit.score)), 4),
                    confidence=round(max(0.0, min(1.0, hit.confidence)), 4),
                    hidden=hit.hidden,
                    created_at_utc=created_at,
                )
                self._rows.append(record)
                self._append_row(record)
            self._trim_in_memory()

    def search_hits(
        self,
        *,
        query: str,
        top_k: int = 4,
        include_hidden: bool = False,
        chapter_index: int | None = None,
    ) -> list[GraphRAGHit]:
        query_text = query.strip()
        if not query_text:
            return []
        query_tokens = self._tokens(query_text)
        if not query_tokens:
            return []

        with self._lock:
            snapshot = list(self._rows)

        scored: list[tuple[float, GraphMemoryRecord]] = []
        total = len(snapshot)
        for reverse_index, record in enumerate(reversed(snapshot), start=1):
            if record.hidden and not include_hidden:
                continue
            if self._is_expired(record):
                continue
            if chapter_index is not None and record.chapter_index is not None:
                if abs(chapter_index - record.chapter_index) > max(0, self.chapter_window):
                    continue
            overlap = self._token_overlap(query_tokens, record)
            if overlap < self._min_token_overlap():
                continue

            recency = 1.0 - min(0.8, reverse_index / max(1, total))
            source_weight = self._resolve_source_weight(record.source_route)
            source_weight_bonus = (source_weight - 1.0) * 0.15
            score = 0.15 + overlap * 0.5 + record.confidence * 0.25 + recency * 0.1 + source_weight_bonus
            scored.append((round(max(0.0, min(1.0, score)), 4), record))

        if not scored:
            return []

        dedup: dict[str, GraphRAGHit] = {}
        for score, record in sorted(scored, key=lambda item: item[0], reverse=True):
            key = record.summary.strip().lower()
            if key in dedup:
                continue
            dedup[key] = GraphRAGHit(
                node_id=f"history::{record.node_id}",
                node_type="history_memory",
                summary=record.summary,
                score=score,
                confidence=record.confidence,
                evidence=f"{record.evidence} | source={record.source_route}",
                hidden=record.hidden,
            )
            if len(dedup) >= max(1, top_k):
                break

        return list(dedup.values())

    def compact(self) -> dict[str, int]:
        with self._lock:
            original_count = len(self._rows)
            retained: list[GraphMemoryRecord] = []
            seen: set[tuple[str, str, bool]] = set()

            for record in reversed(self._rows):
                if self._is_expired(record):
                    continue
                key = (
                    record.summary.strip().lower(),
                    record.source_route,
                    record.hidden,
                )
                if key in seen:
                    continue
                seen.add(key)
                retained.append(record)
                if self.compaction_max_rows > 0 and len(retained) >= self.compaction_max_rows:
                    break

            retained.reverse()
            self._rows = retained
            self._rewrite_rows(retained)
            return {
                "before": original_count,
                "after": len(retained),
                "removed": max(0, original_count - len(retained)),
            }

    def audit_snapshot(self, *, limit: int = 20) -> dict[str, object]:
        with self._lock:
            snapshot = list(self._rows)

        by_source: dict[str, int] = {}
        by_node_type: dict[str, int] = {}
        chapter_indexes: list[int] = []
        duplicate_keys: set[tuple[str, str, bool]] = set()
        seen_keys: set[tuple[str, str, bool]] = set()
        hidden_count = 0
        expired_count = 0

        for record in snapshot:
            by_source[record.source_route] = by_source.get(record.source_route, 0) + 1
            by_node_type[record.node_type] = by_node_type.get(record.node_type, 0) + 1
            if record.chapter_index is not None:
                chapter_indexes.append(record.chapter_index)
            if record.hidden:
                hidden_count += 1
            if self._is_expired(record):
                expired_count += 1

            key = (record.summary.strip().lower(), record.source_route, record.hidden)
            if key in seen_keys:
                duplicate_keys.add(key)
            seen_keys.add(key)

        latest_records = [
            {
                "record_id": record.record_id,
                "source_route": record.source_route,
                "node_type": record.node_type,
                "summary": record.summary,
                "hidden": record.hidden,
                "chapter_index": record.chapter_index,
                "created_at_utc": record.created_at_utc,
            }
            for record in reversed(snapshot[-max(1, limit) :])
        ]

        return {
            "path": str(self.path),
            "audit_path": str(self._audit_path()),
            "created_at_utc": _now_iso(),
            "total_rows": len(snapshot),
            "active_rows": max(0, len(snapshot) - expired_count),
            "expired_rows": expired_count,
            "hidden_rows": hidden_count,
            "duplicate_groups": len(duplicate_keys),
            "chapter_min": min(chapter_indexes) if chapter_indexes else None,
            "chapter_max": max(chapter_indexes) if chapter_indexes else None,
            "by_source_route": dict(sorted(by_source.items())),
            "by_node_type": dict(sorted(by_node_type.items())),
            "policy": {
                "max_age_hours": self.max_age_hours,
                "chapter_window": self.chapter_window,
                "min_token_overlap": self._min_token_overlap(),
                "compaction_max_rows": self.compaction_max_rows,
            },
            "latest_records": latest_records,
        }

    def persist_audit_snapshot(self, *, limit: int = 20) -> dict[str, object]:
        snapshot = self.audit_snapshot(limit=limit)
        audit_path = self._audit_path()
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, ensure_ascii=False))
            handle.write("\n")
        self._trim_audit_history()
        return snapshot

    def audit_history(self, *, limit: int = 20) -> list[dict[str, object]]:
        audit_path = self._audit_path()
        if not audit_path.exists():
            return []

        rows: list[dict[str, object]] = []
        for raw in audit_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return list(reversed(rows[-max(1, limit) :]))

    def audit_trend_alerts(self, *, limit: int = 20) -> dict[str, object]:
        history = self.audit_history(limit=limit)
        latest = history[0] if history else self.audit_snapshot(limit=1)
        previous = history[1] if len(history) > 1 else None

        total_rows = self._as_float(latest.get("total_rows"))
        expired_rows = self._as_float(latest.get("expired_rows"))
        duplicate_groups = self._as_float(latest.get("duplicate_groups"))
        active_rows = self._as_float(latest.get("active_rows"))
        expired_rate = expired_rows / max(1.0, total_rows)

        alerts: list[dict[str, object]] = []
        if expired_rate > self.audit_expired_rate_threshold:
            alerts.append(
                {
                    "code": "graph_memory_expired_rate_high",
                    "severity": "warning",
                    "value": round(expired_rate, 4),
                    "threshold": self.audit_expired_rate_threshold,
                    "message": "expired graph memory rows exceed threshold",
                }
            )

        if duplicate_groups > self.audit_duplicate_groups_threshold:
            alerts.append(
                {
                    "code": "graph_memory_duplicate_groups_high",
                    "severity": "warning",
                    "value": int(duplicate_groups),
                    "threshold": self.audit_duplicate_groups_threshold,
                    "message": "duplicate graph memory groups exceed threshold",
                }
            )

        active_drop_rate = 0.0
        if previous is not None:
            previous_active = self._as_float(previous.get("active_rows"))
            active_drop_rate = max(0.0, (previous_active - active_rows) / max(1.0, previous_active))
            if active_drop_rate > self.audit_active_drop_rate_threshold:
                alerts.append(
                    {
                        "code": "graph_memory_active_rows_drop",
                        "severity": "warning",
                        "value": round(active_drop_rate, 4),
                        "threshold": self.audit_active_drop_rate_threshold,
                        "message": "active graph memory rows dropped sharply between snapshots",
                    }
                )

        return {
            "enabled": True,
            "history_count": len(history),
            "latest_created_at_utc": latest.get("created_at_utc"),
            "previous_created_at_utc": previous.get("created_at_utc") if previous else None,
            "expired_rate": round(expired_rate, 4),
            "active_drop_rate": round(active_drop_rate, 4),
            "duplicate_groups": int(duplicate_groups),
            "thresholds": {
                "expired_rate": self.audit_expired_rate_threshold,
                "duplicate_groups": self.audit_duplicate_groups_threshold,
                "active_drop_rate": self.audit_active_drop_rate_threshold,
            },
            "alerts": alerts,
        }

    def _load_from_disk(self) -> list[GraphMemoryRecord]:
        if not self.path.exists():
            return []
        rows: list[GraphMemoryRecord] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if not isinstance(payload, dict):
                continue
            try:
                rows.append(GraphMemoryRecord.model_validate(payload))
            except Exception:
                continue
        if self.max_in_memory_rows > 0 and len(rows) > self.max_in_memory_rows:
            rows = rows[-self.max_in_memory_rows :]
        return rows

    def _append_row(self, row: GraphMemoryRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _rewrite_rows(self, rows: list[GraphMemoryRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False))
                handle.write("\n")

    def _audit_path(self) -> Path:
        return self.audit_path or self.path.with_name("v6_graph_memory_audit.jsonl")

    def _trim_audit_history(self) -> None:
        if self.audit_max_rows <= 0:
            return
        audit_path = self._audit_path()
        if not audit_path.exists():
            return
        lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) <= self.audit_max_rows:
            return
        audit_path.write_text("\n".join(lines[-self.audit_max_rows :]) + "\n", encoding="utf-8")

    def _trim_in_memory(self) -> None:
        if self.max_in_memory_rows <= 0:
            return
        if len(self._rows) <= self.max_in_memory_rows:
            return
        self._rows = self._rows[-self.max_in_memory_rows :]

    def _tokens(self, text: str) -> list[str]:
        tokens = [item.lower() for item in _TOKEN_PATTERN.findall(text)]
        return [item for item in tokens if item.strip()]

    def _token_overlap(self, query_tokens: list[str], record: GraphMemoryRecord) -> float:
        record_tokens = set(record.query_tokens)
        record_tokens.update(self._tokens(record.summary))
        overlap = sum(1 for token in query_tokens if token in record_tokens)
        return overlap / max(1, len(query_tokens))

    def _min_token_overlap(self) -> float:
        try:
            parsed = float(self.min_token_overlap)
        except Exception:
            return 0.0
        return max(0.0, min(1.0, parsed))

    def _is_expired(self, record: GraphMemoryRecord) -> bool:
        if self.max_age_hours is None or self.max_age_hours <= 0:
            return False
        created = self._parse_iso_utc(record.created_at_utc)
        if created is None:
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(hours=float(self.max_age_hours))
        return created < cutoff

    def _parse_iso_utc(self, value: str) -> datetime | None:
        text = (value or "").strip()
        if not text:
            return None
        try:
            normalized = text.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except Exception:
            return None

    def _resolve_source_weight(self, route: str) -> float:
        raw_weight = self.source_weights.get(route, 1.0)
        try:
            parsed = float(raw_weight)
        except Exception:
            return 1.0
        return max(0.5, min(1.5, parsed))

    def _as_float(self, value: object) -> float:
        try:
            return float(value)  # type: ignore[arg-type]
        except Exception:
            return 0.0


def create_default_v6_graph_memory_store(root: Path | None = None) -> PersistentGraphMemoryStore:
    store = ArtifactStore.default()
    base = root or (store.artifacts_dir / "history")
    source_weights = dict(_DEFAULT_SOURCE_WEIGHTS)
    override_json = (settings.v6_graph_memory_source_weights_json or "").strip()
    if override_json:
        try:
            parsed = json.loads(override_json)
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    if not isinstance(key, str):
                        continue
                    source_weights[key] = float(value)
        except Exception:
            # Keep deterministic default weights if override parsing fails.
            source_weights = dict(_DEFAULT_SOURCE_WEIGHTS)
    return PersistentGraphMemoryStore(
        path=base / "v6_graph_memory.jsonl",
        audit_path=base / "v6_graph_memory_audit.jsonl",
        max_in_memory_rows=max(100, int(settings.v6_graph_memory_max_in_memory_rows)),
        max_age_hours=int(settings.v6_graph_memory_max_age_hours),
        chapter_window=max(0, int(settings.v6_graph_memory_chapter_window)),
        min_token_overlap=max(0.0, min(1.0, float(settings.v6_graph_memory_min_token_overlap))),
        compaction_max_rows=max(100, int(settings.v6_graph_memory_compaction_max_rows)),
        audit_max_rows=max(10, int(settings.v6_graph_memory_audit_max_rows)),
        audit_expired_rate_threshold=max(0.0, min(1.0, float(settings.v6_graph_memory_audit_expired_rate_threshold))),
        audit_duplicate_groups_threshold=max(0, int(settings.v6_graph_memory_audit_duplicate_groups_threshold)),
        audit_active_drop_rate_threshold=max(
            0.0,
            min(1.0, float(settings.v6_graph_memory_audit_active_drop_rate_threshold)),
        ),
        source_weights=source_weights,
    )
