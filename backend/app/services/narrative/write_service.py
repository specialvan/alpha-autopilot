from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from alpha_autopilot import ArtifactStore, DbHistoryRepository, RecommendationMetricRecord, TrainingLogger


@dataclass
class WriteResult:
    ok: bool
    message: str
    persisted: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "message": self.message,
            "persisted": self.persisted,
        }


class NarrativeWriteService:
    def __init__(self, repository: DbHistoryRepository | None = None) -> None:
        self.store = ArtifactStore.default()
        self.logger = TrainingLogger()
        self.repository = repository

    def attach_repository(self, repository: DbHistoryRepository) -> None:
        self.repository = repository

    def persist_training(self, entry: Dict[str, Any]) -> WriteResult:
        if self.repository is None:
            return WriteResult(False, "repository unavailable", False)
        self.repository.insert_training_log(entry)
        return WriteResult(True, "training log persisted", True)

    def persist_value_metric(self, record: RecommendationMetricRecord) -> WriteResult:
        if self.repository is None:
            return WriteResult(False, "repository unavailable", False)
        self.repository.insert_value_metric(record)
        return WriteResult(True, "value metric persisted", True)
