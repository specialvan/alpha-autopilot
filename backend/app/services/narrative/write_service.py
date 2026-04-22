from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from alpha_autopilot import HistoryRepository, RecommendationMetricRecord, create_history_repository


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
    def __init__(self, repository: HistoryRepository | None = None) -> None:
        self.repository = repository or create_history_repository()

    def attach_repository(self, repository: HistoryRepository) -> None:
        self.repository = repository

    def persist_training(self, entry: Dict[str, Any]) -> WriteResult:
        if self.repository is None:
            return WriteResult(False, "repository unavailable", False)
        try:
            self.repository.insert_training_log(entry)
        except Exception as exc:
            return WriteResult(False, f"training log persistence failed: {exc}", False)
        return WriteResult(True, "training log persisted", True)

    def persist_value_metric(self, record: RecommendationMetricRecord) -> WriteResult:
        if self.repository is None:
            return WriteResult(False, "repository unavailable", False)
        try:
            self.repository.insert_value_metric(record)
        except Exception as exc:
            return WriteResult(False, f"value metric persistence failed: {exc}", False)
        return WriteResult(True, "value metric persisted", True)
