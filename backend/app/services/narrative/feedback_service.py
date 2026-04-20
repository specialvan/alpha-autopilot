from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import sqlite3

from alpha_autopilot import ArtifactStore, DbHistoryRepository, FeatureMatrix, TrainingLogger, VersionManager
from .write_service import NarrativeWriteService


@dataclass
class FeedbackResult:
    accepted: bool
    version: str | None
    message: str
    value_summary: Dict[str, float] | None = None
    top_actions: list[Dict[str, float]] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "version": self.version,
            "message": self.message,
            "value_summary": self.value_summary,
            "top_actions": self.top_actions,
        }


class NarrativeFeedbackService:
    def __init__(self) -> None:
        self.versioner = VersionManager()
        self.logger = TrainingLogger()
        self.matrix = FeatureMatrix()
        self.store = ArtifactStore.default()
        self._db = self._open_db()
        self.repository = DbHistoryRepository(self._db)
        self.writer = NarrativeWriteService(self.repository)

    def _open_db(self) -> sqlite3.Connection:
        self.store.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.store.sqlite_path)

    def record_feedback(self, action: str, target: float, predicted: float, feedback: float, notes: str = "") -> FeedbackResult:
        payload = {
            "timestamp": self.logger.entries[-1]["timestamp"] if self.logger.entries else "",
            "stage": "feedback",
            "action": action,
            "predicted": predicted,
            "target": target,
            "feedback": feedback,
            "notes": notes or "feedback recorded from api",
        }
        self.logger.record(
            stage=payload["stage"],
            action=payload["action"],
            predicted=payload["predicted"],
            target=payload["target"],
            feedback=payload["feedback"],
            notes=payload["notes"],
        )
        self.writer.persist_training(payload)
        self.writer.persist_value_metric(
            {
                "action": action,
                "score": predicted,
                "accepted": feedback >= 0.8,
                "chapter_quality": feedback,
                "followup_writeability": max(0.0, min(1.0, feedback * 0.9 + 0.05)),
                "continuity_delta": max(-1.0, min(1.0, target - predicted)),
                "notes": notes or "feedback recorded from api",
            }
        )
        version = None
        if abs(target - predicted) > 0.12 or feedback < 0.8:
            snapshot = self.versioner.create_version(self.matrix.weights, self.matrix.bias, 0, notes="feedback correction")
            version = snapshot.version
        metrics = self.repository.read_value_metrics()
        summary = metrics.summary()
        top_actions = metrics.top_actions()
        return FeedbackResult(True, version, "feedback accepted", summary, top_actions)
