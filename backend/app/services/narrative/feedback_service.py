from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from alpha_autopilot import (
    ArtifactStore,
    FeatureMatrix,
    HistoryRepository,
    RecommendationMetricRecord,
    TrainingLogger,
    VersionManager,
    create_history_repository,
)
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
    def __init__(self, repository: HistoryRepository | None = None, store: ArtifactStore | None = None) -> None:
        self.versioner = VersionManager()
        self.store = store or ArtifactStore.default()
        self.logger = TrainingLogger(self.store.root)
        self.matrix = FeatureMatrix()
        self.repository = repository or create_history_repository(self.store)
        self.writer = NarrativeWriteService(self.repository)

    def record_feedback(self, action: str, target: float, predicted: float, feedback: float, notes: str = "") -> FeedbackResult:
        timestamp = datetime.now(timezone.utc).isoformat()
        note_text = notes or "feedback recorded from api"
        version = None
        if abs(target - predicted) > 0.12 or feedback < 0.8:
            snapshot = self.versioner.create_version(self.matrix.weights, self.matrix.bias, 0, notes="feedback correction")
            version = snapshot.version
        payload = {
            "timestamp": timestamp,
            "stage": "feedback",
            "action": action,
            "predicted": predicted,
            "target": target,
            "feedback": feedback,
            "notes": note_text,
            "version": version or "",
        }
        self.logger.record(
            stage=payload["stage"],
            action=payload["action"],
            predicted=payload["predicted"],
            target=payload["target"],
            feedback=payload["feedback"],
            notes=payload["notes"],
            version=payload["version"],
            timestamp=payload["timestamp"],
        )
        training_result = self.writer.persist_training(payload)
        metric_result = self.writer.persist_value_metric(
            RecommendationMetricRecord(
                action=action,
                score=predicted,
                accepted=feedback >= 0.8,
                chapter_quality=feedback,
                followup_writeability=max(0.0, min(1.0, feedback * 0.9 + 0.05)),
                continuity_delta=max(-1.0, min(1.0, target - predicted)),
                notes=note_text,
            )
        )
        if not training_result.ok:
            return FeedbackResult(False, None, training_result.message)
        if not metric_result.ok:
            return FeedbackResult(False, None, metric_result.message)
        metrics = self.repository.read_value_metrics()
        summary = metrics.summary()
        top_actions = metrics.top_actions()
        return FeedbackResult(True, version, "feedback accepted", summary, top_actions)
