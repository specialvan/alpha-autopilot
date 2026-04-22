from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, List

from .storage import ArtifactStore


@dataclass
class TrainingLogEntry:
    timestamp: str
    stage: str
    action: str
    predicted: float
    target: float
    feedback: float
    notes: str = ""
    version: str = ""


class TrainingLogger:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[1])
        self.store = ArtifactStore(root=self.root)
        self.log_path = self.store.training_log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        return json.loads(self.log_path.read_text(encoding="utf-8"))

    def record(
        self,
        stage: str,
        action: str,
        predicted: float,
        target: float,
        feedback: float,
        notes: str = "",
        version: str = "",
        timestamp: str | None = None,
    ) -> None:
        entry = TrainingLogEntry(
            timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
            stage=stage,
            action=action,
            predicted=predicted,
            target=target,
            feedback=feedback,
            notes=notes,
            version=version,
        )
        self.entries.append(asdict(entry))
        self.log_path.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def history(self) -> List[Dict[str, Any]]:
        return list(self.entries)
