from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
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

MIN_CORRIDOR_SAMPLES = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class V7BenchmarkStore:
    def __init__(self, *, path: Path) -> None:
        self.path = path
        self._lock = RLock()

    def ingest(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        channel = _normalize_label(payload.channel)
        genre_track = _normalize_label(payload.genre_track)

        if not payload.sample_payload:
            return BenchmarkIngestResponse(
                accepted=False,
                version=self._version_tag([]),
                recalibrated=False,
                message="empty_sample_payload",
            )

        with self._lock:
            rows = self._read_rows()
            if any(str(row.get("book_id", "")).strip() == payload.book_id for row in rows):
                return BenchmarkIngestResponse(
                    accepted=False,
                    version=self._version_tag(rows),
                    recalibrated=False,
                    message="duplicate_book_id",
                )

            row = {
                "book_id": payload.book_id,
                "channel": channel,
                "genre_track": genre_track,
                "sample_payload": payload.sample_payload,
                "active": True,
                "created_at": _now_iso(),
                "nqm_mean": self._extract_mean(payload.sample_payload),
            }
            rows.append(row)
            self._write_rows(rows)
            return BenchmarkIngestResponse(
                accepted=True,
                version=self._version_tag(rows),
                recalibrated=True,
                message="accepted",
            )

    def retract(self, book_id: str) -> bool:
        with self._lock:
            rows = self._read_rows()
            changed = False
            for row in rows:
                if str(row.get("book_id", "")).strip() == book_id and bool(row.get("active", True)):
                    row["active"] = False
                    row["retracted_at"] = _now_iso()
                    changed = True
            if changed:
                self._write_rows(rows)
            return changed

    def query(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        channel = _normalize_label(payload.channel)
        genre_track = _normalize_label(payload.genre_track)
        with self._lock:
            rows = self._read_rows()

        active_rows = [row for row in rows if bool(row.get("active", True))]
        exact = [
            row
            for row in active_rows
            if str(row.get("channel", "unknown")) == channel
            and str(row.get("genre_track", "unknown")) == genre_track
        ]

        source_rows = exact
        warnings: list[str] = []

        if not source_rows:
            source_rows = [row for row in active_rows if str(row.get("channel", "unknown")) == channel]
            if source_rows:
                warnings.append("genre_fallback_to_channel")

        if not source_rows:
            fallback = BenchmarkParameterSet(channel=channel, genre_track=genre_track)
            return BenchmarkQueryResponse(
                benchmark=fallback,
                source_count=0,
                corridor_ready=False,
                warnings=["no_benchmark_samples"],
            )

        means = [float(row.get("nqm_mean", 0.62)) for row in source_rows]
        mean_value = sum(means) / len(means)
        variance = sum((item - mean_value) ** 2 for item in means) / max(1, len(means))
        std_value = max(0.01, variance ** 0.5)

        corridor_ready = len(source_rows) >= MIN_CORRIDOR_SAMPLES
        if not corridor_ready:
            warnings.append("insufficient_samples_for_corridor")

        benchmark = BenchmarkParameterSet(
            channel=channel,
            genre_track=genre_track,
            sample_count=len(source_rows),
            nqm_mean=clamp(mean_value),
            nqm_std=clamp(std_value, low=0.01, high=0.5),
            high_threshold=clamp(mean_value + 0.16),
            low_threshold=clamp(mean_value - 0.10),
            opening_gate_t8=0.60,
        )
        return BenchmarkQueryResponse(
            benchmark=benchmark,
            source_count=len(source_rows),
            corridor_ready=corridor_ready,
            warnings=warnings,
        )

    def _version_tag(self, rows: list[dict[str, object]]) -> str:
        active_count = sum(1 for row in rows if bool(row.get("active", True)))
        return f"v7-benchmark-{len(rows):05d}-a{active_count:05d}"

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

        with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(self.path.parent)) as tmp_file:
            for row in rows:
                tmp_file.write(json.dumps(row, ensure_ascii=False))
                tmp_file.write("\n")
            tmp_name = tmp_file.name

        Path(tmp_name).replace(self.path)


def create_default_v7_benchmark_store(root: Path | None = None) -> V7BenchmarkStore:
    artifact_store = ArtifactStore.default()
    base = root or (artifact_store.artifacts_dir / "history")
    return V7BenchmarkStore(path=base / "v7_benchmark_store.jsonl")


def _normalize_label(value: str) -> str:
    text = str(value or "unknown").strip().lower()
    return text or "unknown"
