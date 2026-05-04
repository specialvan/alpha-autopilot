from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from alpha_autopilot import ArtifactStore


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _safe_int(value: object, default: int | None = None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default


@dataclass
class V4MemoryStore:
    relationship_path: Path
    feedback_path: Path
    runtime_metrics_path: Path | None = None

    def read_relationship_rows(self, *, limit: int = 500) -> list[dict[str, object]]:
        rows = self._read_jsonl(self.relationship_path)
        if limit <= 0:
            return []
        return rows[-limit:]

    def read_feedback_rows(self, *, limit: int = 500) -> list[dict[str, object]]:
        rows = self._read_jsonl(self.feedback_path)
        if limit <= 0:
            return []
        return rows[-limit:]

    def read_runtime_metric_rows(self, *, limit: int = 500) -> list[dict[str, object]]:
        rows = self._read_jsonl(self._resolve_runtime_metrics_path())
        if limit <= 0:
            return []
        return rows[-limit:]

    def read_relationship_history(self, context_id: str, *, limit: int = 50) -> list[dict[str, object]]:
        rows = [
            row
            for row in self._read_jsonl(self.relationship_path)
            if str(row.get("context_id", "")) == context_id
        ]
        history = [
            {
                "source_character": str(row.get("source_character", "")),
                "target_character": str(row.get("target_character", "")),
                "tension_score": _safe_float(row.get("tension_score"), 0.0),
                "dominant_gap": str(row.get("dominant_gap", "status")),
                "chapter_index": _safe_int(row.get("chapter_index"), None),
            }
            for row in rows[-limit:]
            if str(row.get("source_character", "")) and str(row.get("target_character", ""))
        ]
        return history

    def read_feedback_history(self, context_id: str, *, limit: int = 50) -> list[dict[str, object]]:
        rows = [
            row
            for row in self._read_jsonl(self.feedback_path)
            if str(row.get("context_id", "")) == context_id
        ]
        return [
            {
                "accepted": bool(row.get("accepted", False)),
                "retention_delta": _safe_float(row.get("retention_delta"), 0.0),
                "abandonment_delta": _safe_float(row.get("abandonment_delta"), 0.0),
                "chapter_index": _safe_int(row.get("chapter_index"), None),
            }
            for row in rows[-limit:]
        ]

    def read_feedback_history_by_genre(
        self,
        genre: str,
        *,
        limit: int = 200,
    ) -> list[dict[str, object]]:
        normalized_genre = _normalize_genre(genre)
        if not normalized_genre:
            return []
        rows = [
            row
            for row in self._read_jsonl(self.feedback_path)
            if _normalize_genre(row.get("genre", "")) == normalized_genre
        ]
        return [
            {
                "accepted": bool(row.get("accepted", False)),
                "retention_delta": _safe_float(row.get("retention_delta"), 0.0),
                "abandonment_delta": _safe_float(row.get("abandonment_delta"), 0.0),
                "chapter_index": _safe_int(row.get("chapter_index"), None),
                "context_id": str(row.get("context_id", "")),
                "genre": normalized_genre,
            }
            for row in rows[-limit:]
        ]

    def append_feedback_history(
        self,
        context_id: str,
        feedback_items: list[dict[str, object]],
        *,
        source: str,
        chapter_index: int | None = None,
        genre: str | None = None,
    ) -> None:
        if not feedback_items:
            return
        normalized_genre = _normalize_genre(genre or "")
        for item in feedback_items:
            if not isinstance(item, dict):
                continue
            self._append_jsonl(
                self.feedback_path,
                {
                    "timestamp": _now_iso(),
                    "context_id": context_id,
                    "source": source,
                    "accepted": bool(item.get("accepted", False)),
                    "retention_delta": _safe_float(item.get("retention_delta"), 0.0),
                    "abandonment_delta": _safe_float(item.get("abandonment_delta"), 0.0),
                    "chapter_index": _safe_int(item.get("chapter_index"), chapter_index),
                    "genre": normalized_genre,
                },
            )

    def append_relationship_snapshot(
        self,
        context_id: str,
        *,
        chapter_index: int | None,
        payload: dict[str, object],
    ) -> None:
        displacements = payload.get("relationship_displacements", [])
        if isinstance(displacements, list) and displacements:
            for item in displacements:
                if not isinstance(item, dict):
                    continue
                source_character = str(item.get("source_character", ""))
                target_character = str(item.get("target_character", ""))
                if not source_character or not target_character:
                    continue
                self._append_jsonl(
                    self.relationship_path,
                    {
                        "timestamp": _now_iso(),
                        "context_id": context_id,
                        "chapter_index": _safe_int(item.get("chapter_index"), chapter_index),
                        "source_character": source_character,
                        "target_character": target_character,
                        "tension_score": _safe_float(item.get("current_tension"), 0.0),
                        "dominant_gap": str(item.get("current_dominant_gap", "status")),
                    },
                )
            return

        relationship_graph = payload.get("relationship_graph", {})
        if not isinstance(relationship_graph, dict):
            return
        high_tension_edges = relationship_graph.get("high_tension_edges", [])
        if not isinstance(high_tension_edges, list):
            return
        for edge in high_tension_edges[:3]:
            if not isinstance(edge, dict):
                continue
            source_character = str(edge.get("source_character", ""))
            target_character = str(edge.get("target_character", ""))
            if not source_character or not target_character:
                continue
            self._append_jsonl(
                self.relationship_path,
                {
                    "timestamp": _now_iso(),
                    "context_id": context_id,
                    "chapter_index": chapter_index,
                    "source_character": source_character,
                    "target_character": target_character,
                    "tension_score": _safe_float(edge.get("tension_score"), 0.0),
                    "dominant_gap": str(edge.get("dominant_gap", "status")),
                },
            )

    def append_runtime_metric(
        self,
        *,
        route: str,
        status: str,
        latency_ms: float,
        fallback_reason: str | None = None,
        error_type: str | None = None,
        context_id: str | None = None,
        http_status: int | None = None,
    ) -> None:
        normalized_status = str(status).strip().lower() or "unknown"
        normalized_route = str(route).strip() or "unknown"
        self._append_jsonl(
            self._resolve_runtime_metrics_path(),
            {
                "timestamp": _now_iso(),
                "route": normalized_route,
                "status": normalized_status,
                "latency_ms": round(max(0.0, _safe_float(latency_ms, 0.0)), 3),
                "fallback_reason": str(fallback_reason).strip() if fallback_reason else "",
                "error_type": str(error_type).strip() if error_type else "",
                "context_id": str(context_id).strip() if context_id else "",
                "http_status": _safe_int(http_status, None),
            },
        )

    def _read_jsonl(self, path: Path) -> list[dict[str, object]]:
        if not path.exists():
            return []
        rows: list[dict[str, object]] = []
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    def _append_jsonl(self, path: Path, row: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")

    def _resolve_runtime_metrics_path(self) -> Path:
        if self.runtime_metrics_path is not None:
            return self.runtime_metrics_path
        return self.relationship_path.with_name("v4_runtime_metrics.jsonl")


def create_default_v4_memory_store(root: Path | None = None) -> V4MemoryStore:
    store = ArtifactStore.default()
    base = root or store.artifacts_dir / "history"
    return V4MemoryStore(
        relationship_path=base / "v4_relationship_memory.jsonl",
        feedback_path=base / "v4_feedback_memory.jsonl",
        runtime_metrics_path=base / "v4_runtime_metrics.jsonl",
    )


def _normalize_genre(value: object) -> str:
    return str(value).strip().lower()
