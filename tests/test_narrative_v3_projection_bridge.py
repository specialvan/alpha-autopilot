from __future__ import annotations

import json
from pathlib import Path

from backend.app.services.narrative.v3_projection_bridge import (
    build_training_samples_from_projection,
    load_matrix_projection,
)


def test_load_matrix_projection_picks_first_existing_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    existing = tmp_path / "matrix_projection.json"
    existing.write_text(
        json.dumps(
            [
                {
                    "chapter_number": 7,
                    "genre": "xuanhuan",
                    "primary_function": "conflict-escalation",
                    "admission": "approved",
                    "recommended_stage": "middle",
                    "narrative_signals": {"conflict_intensity": 0.74, "payoff_pressure": 0.38},
                }
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    records, found = load_matrix_projection([missing, existing])

    assert found == existing
    assert len(records) == 1


def test_build_training_samples_from_projection_maps_function_and_signals() -> None:
    samples = build_training_samples_from_projection(
        [
            {
                "chapter_number": 11,
                "genre": "xuanhuan",
                "primary_function": "conflict-escalation",
                "admission": "approved",
                "recommended_stage": "middle",
                "narrative_signals": {"conflict_intensity": 0.72, "payoff_pressure": 0.37},
            }
        ]
    )

    assert len(samples) == 1
    sample = samples[0]
    assert sample.target_action == "push_conflict"
    assert sample.state.stage == "middle"
    assert sample.state.conflict_intensity == 0.72
    assert "v3_projection" in sample.state.tags
