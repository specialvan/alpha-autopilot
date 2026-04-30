from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock
from typing import Iterable

from alpha_autopilot import ArtifactStore

from ...core.config import settings
from .schemas import ParallelPlotSimulationResult


@dataclass
class InMemorySimulationStore:
    _rows: dict[str, ParallelPlotSimulationResult] = field(default_factory=dict)
    _lock: RLock = field(default_factory=RLock)

    def save(self, result: ParallelPlotSimulationResult) -> None:
        with self._lock:
            self._rows[result.simulation_id] = result

    def get(self, simulation_id: str) -> ParallelPlotSimulationResult | None:
        with self._lock:
            return self._rows.get(simulation_id)

    def list_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._rows)


@dataclass
class PersistentSimulationStore:
    path: Path
    max_rows_per_file: int = 500
    max_bytes_per_file: int = 2_000_000
    archive_root: Path | None = None
    archive_bucket_format: str = "%Y%m%d"
    _rows: dict[str, ParallelPlotSimulationResult] = field(default_factory=dict, init=False)
    _lock: RLock = field(default_factory=RLock, init=False)
    _current_file_row_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.archive_root is None:
            self.archive_root = self.path.parent / "v6_simulation_archive"
        self._rows = self._load_from_disk()
        self._current_file_row_count = self._count_rows(self.path)

    def save(self, result: ParallelPlotSimulationResult) -> None:
        with self._lock:
            self._rows[result.simulation_id] = result
            self._append_row(result)

    def get(self, simulation_id: str) -> ParallelPlotSimulationResult | None:
        with self._lock:
            return self._rows.get(simulation_id)

    def list_ids(self) -> list[str]:
        with self._lock:
            return sorted(self._rows)

    def list_storage_files(self) -> list[Path]:
        with self._lock:
            return list(self._iter_storage_files())

    def _load_from_disk(self) -> dict[str, ParallelPlotSimulationResult]:
        rows: dict[str, ParallelPlotSimulationResult] = {}
        for file_path in self._iter_storage_files():
            for raw in file_path.read_text(encoding="utf-8").splitlines():
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
                    simulation = ParallelPlotSimulationResult.model_validate(payload)
                except Exception:
                    continue
                rows[simulation.simulation_id] = simulation
        return rows

    def _append_row(self, result: ParallelPlotSimulationResult) -> None:
        self._rotate_if_needed()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")
        self._current_file_row_count += 1

    def _rotate_if_needed(self) -> None:
        if not self.path.exists():
            return

        should_rotate_by_rows = self.max_rows_per_file > 0 and self._current_file_row_count >= self.max_rows_per_file
        current_size = self.path.stat().st_size
        should_rotate_by_bytes = self.max_bytes_per_file > 0 and current_size >= self.max_bytes_per_file
        if not should_rotate_by_rows and not should_rotate_by_bytes:
            return

        archive_root = self.archive_root or (self.path.parent / "v6_simulation_archive")
        bucket = datetime.now(timezone.utc).strftime(self.archive_bucket_format)
        archive_dir = archive_root / bucket
        archive_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = archive_dir / f"{self.path.stem}-{ts}.jsonl"
        suffix = 1
        while target.exists():
            target = archive_dir / f"{self.path.stem}-{ts}-{suffix}.jsonl"
            suffix += 1

        self.path.replace(target)
        self._current_file_row_count = 0

    def _iter_storage_files(self) -> Iterable[Path]:
        files: list[Path] = []
        archive_root = self.archive_root or (self.path.parent / "v6_simulation_archive")
        pattern = f"{self.path.stem}-*.jsonl"

        if self.path.parent.exists():
            files.extend(sorted(self.path.parent.glob(pattern), key=lambda p: str(p)))
        if archive_root.exists():
            files.extend(sorted(archive_root.rglob(pattern), key=lambda p: str(p)))
        if self.path.exists():
            files.append(self.path)

        dedup: dict[str, Path] = {}
        for file_path in files:
            dedup[str(file_path)] = file_path
        return list(dedup.values())

    @staticmethod
    def _count_rows(path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip())


def create_default_v6_simulation_store(root: Path | None = None) -> PersistentSimulationStore:
    store = ArtifactStore.default()
    base = root or (store.artifacts_dir / "history")
    return PersistentSimulationStore(
        path=base / "v6_simulation_results.jsonl",
        max_rows_per_file=max(0, int(settings.v6_simulation_store_max_rows_per_file)),
        max_bytes_per_file=max(0, int(settings.v6_simulation_store_max_bytes_per_file)),
        archive_root=base / "v6_simulation_archive",
    )
