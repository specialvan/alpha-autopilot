from __future__ import annotations

from alpha_autopilot_v3.decomposition.models import ChapterDecompositionRecord
from alpha_autopilot_v3.retention.metrics import build_retention_metrics


def test_build_retention_metrics_handles_missing_checkpoints() -> None:
    record = ChapterDecompositionRecord(
        chapter_number=1,
        title="Sparse Record",
        scope="single",
        genre="xuanhuan",
        stage="opening",
        stage_inferred=False,
        primary_function="transition-breathing",
        structure={},
        style_dna={},
        checkpoints=[],
    )

    metrics = build_retention_metrics(record)

    assert metrics.chapter_attraction_score >= 0.0
    assert metrics.continue_reading_intent >= 0.0
    assert metrics.evidence["conflict_progression"] == "unknown"
    assert metrics.evidence["read_through_drive"] == "unknown"
    assert metrics.evidence["continuity_stability"] == "unknown"
