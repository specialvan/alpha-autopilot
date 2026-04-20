from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from alpha_autopilot import FeatureMatrix, TrainingLogger, VersionManager


@dataclass
class FeedbackResult:
    accepted: bool
    version: str | None
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "version": self.version,
            "message": self.message,
        }


class NarrativeFeedbackService:
    def __init__(self) -> None:
        self.versioner = VersionManager()
        self.logger = TrainingLogger()
        self.matrix = FeatureMatrix()

    def record_feedback(self, action: str, target: float, predicted: float, feedback: float, notes: str = "") -> FeedbackResult:
        self.logger.record(
            stage="feedback",
            action=action,
            predicted=predicted,
            target=target,
            feedback=feedback,
            notes=notes or "feedback recorded from api",
        )
        version = None
        if abs(target - predicted) > 0.12 or feedback < 0.8:
            snapshot = self.versioner.create_version(self.matrix.weights, self.matrix.bias, 0, notes="feedback correction")
            version = snapshot.version
        return FeedbackResult(True, version, "feedback accepted")
