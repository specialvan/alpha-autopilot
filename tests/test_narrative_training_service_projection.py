from __future__ import annotations

import json
from pathlib import Path

from alpha_autopilot import ArtifactStore, FileHistoryRepository
from backend.app.services.narrative.training_service import NarrativeTrainingService


def test_training_service_uses_v3_matrix_projection_samples(tmp_path: Path) -> None:
    projection_path = tmp_path / "matrix_projection.json"
    projection_path.write_text(
        json.dumps(
            [
                {
                    "chapter_number": 21,
                    "genre": "xuanhuan",
                    "primary_function": "payoff-delivery",
                    "admission": "approved",
                    "recommended_stage": "mid_late",
                    "narrative_signals": {"conflict_intensity": 0.69, "payoff_pressure": 0.75},
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    service = NarrativeTrainingService(
        store=ArtifactStore(root=tmp_path),
        projection_paths=[projection_path],
    )

    result = service.train()

    assert result.sample_count == 5
    assert result.projection_sample_count == 1
    assert result.projection_source == str(projection_path)
    assert (tmp_path / "artifacts" / "registry.json").exists()


def test_training_service_avoids_duplicate_file_training_log_writes(tmp_path: Path) -> None:
    store = ArtifactStore(root=tmp_path)
    service = NarrativeTrainingService(
        repository=FileHistoryRepository(store),
        store=store,
        projection_paths=[],
    )

    result = service.train()
    training_logs = service.repository.read_training_logs()

    assert len(training_logs) == len(result.history)
