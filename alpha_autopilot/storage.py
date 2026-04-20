from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactStore:
    root: Path

    @property
    def artifacts_dir(self) -> Path:
        return self.root / "artifacts"

    @property
    def training_log_path(self) -> Path:
        return self.artifacts_dir / "training" / "training_log.json"

    @property
    def value_metrics_path(self) -> Path:
        return self.artifacts_dir / "metrics" / "recommendation_value_metrics.json"

    @property
    def history_snapshots_path(self) -> Path:
        return self.artifacts_dir / "history" / "history_snapshots.json"

    @property
    def sqlite_path(self) -> Path:
        return self.artifacts_dir / "db" / "history.sqlite3"

    @classmethod
    def default(cls) -> "ArtifactStore":
        return cls(root=Path(__file__).resolve().parents[1])
