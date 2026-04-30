from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock

from alpha_autopilot import ArtifactStore

from .common import clamp
from .schemas import (
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class V7BenchmarkStore:
    path: Path
    _lock: RLock = field(default_factory=RLock, init=False)

    def ingest(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        with self._lock:
            rows = self._read_rows()
            if any(row.get("book_id") == payload.book_id and bool(row.get("active", True)) for row in rows):
                return BenchmarkIngestResponse(accepted=False, version=self._version_tag(rows), recalibrated=False)

            row = {
                "book_id": payload.book_id,
                "channel": payload.channel,
                "genre_track": payload.genre_track,
                "sample_payload": payload.sample_payload,
                "active": True,
                "created_at": _now_iso(),
                "nqm_mean": self._extract_mean(payload.sample_payload),
            }
            rows.append(row)
            self._write_rows(rows)
            return BenchmarkIngestResponse(accepted=True, version=self._version_tag(rows), recalibrated=True)

    def retract(self, book_id: str) -> bool:
        with self._lock:
            rows = self._read_rows()
            changed = False
            for row in rows:
                if row.get("book_id") == book_id and bool(row.get("active", True)):
                    row["active"] = False
                    row["retracted_at"] = _now_iso()
                    changed = True
            if changed:
                self._write_rows(rows)
            return changed

    def query(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        with self._lock:
            rows = self._read_rows()

        filtered = [
            row
            for row in rows
            if bool(row.get("active", True))
            and str(row.get("channel", "unknown")) == payload.channel
            and str(row.get("genre_track", "unknown")) == payload.genre_track
        ]

        if not filtered:
            fallback = BenchmarkParameterSet(channel=payload.channel, genre_track=payload.genre_track)
            return BenchmarkQueryResponse(benchmark=fallback, source_count=0)

        means = [float(row.get("nqm_mean", 0.62)) for row in filtered]
        mean_value = sum(means) / len(means)
        variance = sum((item - mean_value) ** 2 for item in means) / max(1, len(means))
        std_value = max(0.01, variance ** 0.5)

        benchmark = BenchmarkParameterSet(
            channel=payload.channel,
            genre_track=payload.genre_track,
            sample_count=len(filtered),
            nqm_mean=clamp(mean_value),
            nqm_std=clamp(std_value, low=0.01, high=0.5),
            high_threshold=clamp(mean_value + 0.16),
            low_threshold=clamp(mean_value - 0.10),
            opening_gate_t8=0.60,
        )
        return BenchmarkQueryResponse(benchmark=benchmark, source_count=len(filtered))

    def _version_tag(self, rows: list[dict[str, object]]) -> str:
        return f"v7-benchmark-{len(rows):05d}"

    def _extract_mean(self, payload: dict[str, object]) -> float:
        if isinstance(payload.get("nqm_mean"), (int, float)):
            return clamp(float(payload["nqm_mean"]))
        if isinstance(payload.get("composite"), (int, float)):
            return clamp(float(payload["composite"]))
        return 0.62

    def _read_rows(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, object]] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
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

    def _write_rows(self, rows: list[dict[str, object]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False))
                handle.write("\n")


def create_default_v7_benchmark_store(root: Path | None = None) -> V7BenchmarkStore:
    artifact_store = ArtifactStore.default()
    base = root or (artifact_store.artifacts_dir / "history")
    return V7BenchmarkStore(path=base / "v7_benchmark_store.jsonl")
