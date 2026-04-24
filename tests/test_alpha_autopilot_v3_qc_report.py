from __future__ import annotations

from datetime import datetime, timezone

from alpha_autopilot_v3.decomposition.models import ChapterDecompositionRecord, CheckpointResult
from alpha_autopilot_v3.decomposition.qc import build_projection_qc_report


def _record(
    *,
    chapter_number: int,
    title: str,
    stage: str,
    primary_function: str,
    admission: str,
    checkpoint_statuses: list[str],
) -> ChapterDecompositionRecord:
    return ChapterDecompositionRecord(
        chapter_number=chapter_number,
        title=title,
        scope="single",
        genre="xuanhuan",
        stage=stage,
        stage_inferred=False,
        primary_function=primary_function,
        checkpoints=[
            CheckpointResult(
                name=f"checkpoint-{index}",
                status=status,
                evidence=f"evidence-{index}",
                implication=f"implication-{index}",
            )
            for index, status in enumerate(checkpoint_statuses, start=1)
        ],
        admission=admission,
    )


def test_build_projection_qc_report_emits_deterministic_core_stats() -> None:
    generated_at = datetime(2026, 4, 24, 8, 30, tzinfo=timezone.utc)
    records = [
        _record(
            chapter_number=1,
            title="Opening Clash",
            stage="opening",
            primary_function="conflict-escalation",
            admission="approved",
            checkpoint_statuses=["pass", "pass"],
        ),
        _record(
            chapter_number=2,
            title="New Clue",
            stage="middle",
            primary_function="information-reveal",
            admission="provisional",
            checkpoint_statuses=["mixed", "pass"],
        ),
        _record(
            chapter_number=3,
            title="Broken Continuity",
            stage="late",
            primary_function="payoff-delivery",
            admission="rejected",
            checkpoint_statuses=["fail"],
        ),
    ]
    projections = [
        {
            "recommended_stage": "opening",
            "primary_function": "conflict-escalation",
            "narrative_signals": {
                "conflict_intensity": 0.6,
                "payoff_pressure": 0.2,
            },
        },
        {
            "recommended_stage": "middle",
            "primary_function": "information-reveal",
            "narrative_signals": {
                "conflict_intensity": "0.4",
            },
        },
        {
            "recommended_stage": "opening",
            "primary_function": "conflict-escalation",
            "narrative_signals": "invalid",
        },
    ]

    report = build_projection_qc_report(records, projections, generated_at=generated_at)

    assert report == {
        "generated_at": "2026-04-24T08:30:00+00:00",
        "schema_version": "1.0",
        "record_count": 3,
        "projection_count": 3,
        "admission_distribution": {
            "approved": 1,
            "provisional": 1,
            "rejected": 1,
        },
        "checkpoint_status_distribution": {
            "fail": 1,
            "mixed": 1,
            "pass": 3,
        },
        "stage_distribution": {
            "middle": 1,
            "opening": 2,
        },
        "primary_function_distribution": {
            "conflict-escalation": 2,
            "information-reveal": 1,
        },
        "avg_conflict_intensity": 0.5,
        "avg_payoff_pressure": 0.2,
        "missing_signal_count": 1,
    }
