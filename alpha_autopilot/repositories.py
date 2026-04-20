from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
import json
import sqlite3

from .metrics import RecommendationMetricRecord, RecommendationValueMetrics
from .storage import ArtifactStore


class HistoryRepository(ABC):
    @abstractmethod
    def read_training_logs(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def read_value_metrics(self) -> RecommendationValueMetrics:
        raise NotImplementedError

    def insert_training_log(self, entry: Dict[str, Any]) -> None:
        raise NotImplementedError

    def insert_value_metric(self, record: RecommendationMetricRecord) -> None:
        raise NotImplementedError


class FileHistoryRepository(HistoryRepository):
    def __init__(self, store: ArtifactStore | None = None) -> None:
        self.store = store or ArtifactStore.default()

    def _read_json(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def read_training_logs(self) -> List[Dict[str, Any]]:
        return self._read_json(self.store.training_log_path)

    def read_value_metrics(self) -> RecommendationValueMetrics:
        return RecommendationValueMetrics.load(self.store.value_metrics_path)

    def insert_training_log(self, entry: Dict[str, Any]) -> None:
        logs = self.read_training_logs()
        logs.append(entry)
        self.store.training_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.store.training_log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")

    def insert_value_metric(self, record: RecommendationMetricRecord) -> None:
        metrics = self.read_value_metrics()
        metrics.add_record(record)
        metrics.save(self.store.value_metrics_path)


class DbHistoryRepository(HistoryRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS training_logs (
                timestamp TEXT NOT NULL,
                stage TEXT NOT NULL,
                action TEXT NOT NULL,
                predicted REAL NOT NULL,
                target REAL NOT NULL,
                feedback REAL NOT NULL,
                notes TEXT DEFAULT ''
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendation_value_metrics (
                action TEXT NOT NULL,
                score REAL NOT NULL,
                accepted INTEGER NOT NULL,
                chapter_quality REAL NOT NULL,
                followup_writeability REAL NOT NULL,
                continuity_delta REAL NOT NULL,
                notes TEXT DEFAULT ''
            )
            """
        )
        self.connection.commit()

    def insert_training_log(self, entry: Dict[str, Any]) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO training_logs (timestamp, stage, action, predicted, target, feedback, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.get("timestamp", ""),
                entry.get("stage", ""),
                entry.get("action", ""),
                float(entry.get("predicted", 0.0)),
                float(entry.get("target", 0.0)),
                float(entry.get("feedback", 0.0)),
                entry.get("notes", ""),
            ),
        )
        self.connection.commit()

    def insert_value_metric(self, record: RecommendationMetricRecord) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO recommendation_value_metrics (
                action, score, accepted, chapter_quality, followup_writeability, continuity_delta, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.action,
                record.score,
                1 if record.accepted else 0,
                record.chapter_quality,
                record.followup_writeability,
                record.continuity_delta,
                record.notes,
            ),
        )
        self.connection.commit()

    def read_training_logs(self) -> List[Dict[str, Any]]:
        cursor = self.connection.cursor()
        rows = cursor.execute(
            "SELECT timestamp, stage, action, predicted, target, feedback, notes FROM training_logs ORDER BY timestamp ASC"
        ).fetchall()
        return [
            {
                "timestamp": row[0],
                "stage": row[1],
                "action": row[2],
                "predicted": row[3],
                "target": row[4],
                "feedback": row[5],
                "notes": row[6],
            }
            for row in rows
        ]

    def read_value_metrics(self) -> RecommendationValueMetrics:
        cursor = self.connection.cursor()
        rows = cursor.execute(
            "SELECT action, score, accepted, chapter_quality, followup_writeability, continuity_delta, notes FROM recommendation_value_metrics"
        ).fetchall()
        metrics = RecommendationValueMetrics()
        for row in rows:
            metrics.add_record(
                RecommendationMetricRecord(
                    action=row[0],
                    score=row[1],
                    accepted=bool(row[2]),
                    chapter_quality=row[3],
                    followup_writeability=row[4],
                    continuity_delta=row[5],
                    notes=row[6] or "",
                )
            )
        return metrics


class FallbackHistoryRepository(HistoryRepository):
    def __init__(self, db_repo: DbHistoryRepository | None = None, file_repo: FileHistoryRepository | None = None) -> None:
        self.db_repo = db_repo
        self.file_repo = file_repo or FileHistoryRepository()

    def read_training_logs(self) -> List[Dict[str, Any]]:
        if self.db_repo is not None:
            try:
                rows = self.db_repo.read_training_logs()
                if rows:
                    return rows
            except Exception:
                pass
        return self.file_repo.read_training_logs()

    def read_value_metrics(self) -> RecommendationValueMetrics:
        if self.db_repo is not None:
            try:
                metrics = self.db_repo.read_value_metrics()
                if metrics.records:
                    return metrics
            except Exception:
                pass
        return self.file_repo.read_value_metrics()

    def insert_training_log(self, entry: Dict[str, Any]) -> None:
        if self.db_repo is not None:
            try:
                self.db_repo.insert_training_log(entry)
            except Exception:
                self.file_repo.insert_training_log(entry)
        else:
            self.file_repo.insert_training_log(entry)

    def insert_value_metric(self, record: RecommendationMetricRecord) -> None:
        if self.db_repo is not None:
            try:
                self.db_repo.insert_value_metric(record)
            except Exception:
                self.file_repo.insert_value_metric(record)
        else:
            self.file_repo.insert_value_metric(record)


def create_history_repository(store: ArtifactStore | None = None) -> HistoryRepository:
    store = store or ArtifactStore.default()
    try:
        connection = sqlite3.connect(store.sqlite_path)
        return FallbackHistoryRepository(DbHistoryRepository(connection), FileHistoryRepository(store))
    except Exception:
        return FileHistoryRepository(store)
