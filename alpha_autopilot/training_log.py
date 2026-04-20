from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, List


@dataclass
class TrainingLogEntry:
    timestamp: str
    stage: str
    action: str
    predicted: float
    target: float
    feedback: float
    notes: str = ""


class TrainingLogger:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[1])
        self.store_dir = self.root / "artifacts"
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.store_dir / "training_log.json"
        self.entries: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        return json.loads(self.log_path.read_text(encoding="utf-8"))

    def record(self, stage: str, action: str, predicted: float, target: float, feedback: float, notes: str = "") -> None:
        entry = TrainingLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            stage=stage,
            action=action,
            predicted=predicted,
            target=target,
            feedback=feedback,
            notes=notes,
        )
        self.entries.append(asdict(entry))
        self.log_path.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def history(self) -> List[Dict[str, Any]]:
        return list(self.entries)
