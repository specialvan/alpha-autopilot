from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from alpha_autopilot import (
    ArtifactStore,
    HistoryRepository,
    Trainer,
    TrainingSample,
    StoryState,
    VersionManager,
    create_history_repository,
)
from .v3_projection_bridge import (
    build_training_samples_from_projection,
    default_projection_paths,
    load_matrix_projection,
)
from .write_service import NarrativeWriteService


@dataclass
class TrainingResult:
    version: str
    sample_count: int
    bias: float
    weights: Dict[str, float]
    summary: Dict[str, float]
    history: List[Dict[str, Any]]
    value_metrics: Dict[str, float]
    top_actions: List[Dict[str, float]]
    projection_sample_count: int = 0
    projection_source: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NarrativeTrainingService:
    def __init__(
        self,
        repository: HistoryRepository | None = None,
        store: ArtifactStore | None = None,
        projection_paths: list[Path] | None = None,
    ) -> None:
        self.store = store or ArtifactStore.default()
        self.versioner = VersionManager(root=self.store.root)
        self.repository = repository or create_history_repository(self.store)
        self.writer = NarrativeWriteService(self.repository)
        self.projection_paths = list(projection_paths or default_projection_paths(self.store.artifacts_dir))

    def _default_samples(self) -> list[TrainingSample]:
        raw = [
            {
                "chapter_index": 1,
                "stage": "opening",
                "mainline_progress": 0.12,
                "sideplot_progress": 0.02,
                "conflict_intensity": 0.58,
                "emotional_temperature": 0.42,
                "pacing_speed": 0.63,
                "foreshadowing_load": 0.18,
                "payoff_pressure": 0.14,
                "target_action": "push_conflict",
                "target_score": 0.92,
                "feedback": 0.88,
                "tags": ["opening", "fast_pace", "conflict"],
            },
            {
                "chapter_index": 12,
                "stage": "middle",
                "mainline_progress": 0.54,
                "sideplot_progress": 0.33,
                "conflict_intensity": 0.61,
                "emotional_temperature": 0.49,
                "pacing_speed": 0.47,
                "foreshadowing_load": 0.41,
                "payoff_pressure": 0.29,
                "target_action": "plant_foreshadow",
                "target_score": 0.84,
                "feedback": 0.81,
                "tags": ["middle", "foreshadow"],
            },
            {
                "chapter_index": 26,
                "stage": "mid_late",
                "mainline_progress": 0.73,
                "sideplot_progress": 0.52,
                "conflict_intensity": 0.67,
                "emotional_temperature": 0.56,
                "pacing_speed": 0.52,
                "foreshadowing_load": 0.46,
                "payoff_pressure": 0.49,
                "target_action": "deliver_payoff",
                "target_score": 0.95,
                "feedback": 0.93,
                "tags": ["mid_late", "payoff"],
            },
            {
                "chapter_index": 33,
                "stage": "late",
                "mainline_progress": 0.86,
                "sideplot_progress": 0.61,
                "conflict_intensity": 0.78,
                "emotional_temperature": 0.66,
                "pacing_speed": 0.55,
                "foreshadowing_load": 0.51,
                "payoff_pressure": 0.66,
                "target_action": "stabilize_continuity",
                "target_score": 0.74,
                "feedback": 0.71,
                "tags": ["late", "continuity"],
            },
        ]
        samples: list[TrainingSample] = []
        for item in raw:
            state = StoryState(
                chapter_index=item["chapter_index"],
                stage=item["stage"],
                mainline_progress=item["mainline_progress"],
                sideplot_progress=item["sideplot_progress"],
                conflict_intensity=item["conflict_intensity"],
                emotional_temperature=item["emotional_temperature"],
                pacing_speed=item["pacing_speed"],
                foreshadowing_load=item["foreshadowing_load"],
                payoff_pressure=item["payoff_pressure"],
                tags=item["tags"],
            )
            samples.append(
                TrainingSample(
                    state=state,
                    target_action=item["target_action"],
                    target_score=item["target_score"],
                    feedback=item["feedback"],
                )
            )
        return samples

    def _projection_samples(self) -> tuple[list[TrainingSample], str | None]:
        records, found_path = load_matrix_projection(self.projection_paths)
        if found_path is None or not records:
            return [], None
        samples = build_training_samples_from_projection(records)
        if not samples:
            return [], None
        return samples, str(found_path)

    def train(self) -> TrainingResult:
        trainer = Trainer()
        base_samples = self._default_samples()
        projection_samples, projection_source = self._projection_samples()
        samples = [*base_samples, *projection_samples]
        notes = (
            f"fastapi training run ({len(base_samples)} base + {len(projection_samples)} projection)"
            if projection_samples
            else "fastapi training run"
        )
        matrix = trainer.fit(samples)
        snapshot = self.versioner.create_version(matrix.weights, matrix.bias, len(samples), notes=notes)
        for entry in trainer.history:
            timestamp = datetime.now(timezone.utc).isoformat()
            payload = {
                "timestamp": timestamp,
                "stage": "train",
                "action": entry["action"],
                "predicted": entry["predicted"],
                "target": entry["target"],
                "feedback": entry.get("feedback", 0.0),
                "notes": notes,
                "version": snapshot.version,
            }
            self.writer.persist_training(payload)

        for record in trainer.value_metrics.records:
            self.writer.persist_value_metric(record)

        metrics = self.repository.read_value_metrics()
        value_metrics_summary = metrics.summary()
        top_actions = metrics.top_actions()

        return TrainingResult(
            version=snapshot.version,
            sample_count=len(samples),
            bias=matrix.bias,
            weights=matrix.weights,
            summary=trainer.summary(),
            history=list(trainer.history),
            value_metrics=value_metrics_summary,
            top_actions=top_actions,
            projection_sample_count=len(projection_samples),
            projection_source=projection_source,
        )
