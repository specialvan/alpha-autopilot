from __future__ import annotations

from alpha_autopilot_v3.decomposition.models import (
    ChapterDecompositionRecord,
    CheckpointResult,
    EvidenceSpan,
)
from alpha_autopilot_v3.decomposition.taxonomy import (
    CHAPTER_FUNCTIONS,
    CHECKPOINTS,
    STYLE_DNA_AXES,
)


def test_v3_taxonomy_and_models_expose_frozen_decomposition_contract() -> None:
    assert "conflict-escalation" in CHAPTER_FUNCTIONS
    assert "chapter-function-fit" in CHECKPOINTS
    assert "pace" in STYLE_DNA_AXES

    record = ChapterDecompositionRecord(
        chapter_number=8,
        title="Pressure Rises in the Midpoint",
        scope="single",
        genre="xuanhuan",
        stage="middle",
        stage_inferred=False,
        primary_function="conflict-escalation",
        secondary_functions=["foreshadow-plant"],
        structure={
            "goal": "Drive the protagonist into open conflict.",
            "opening_hook": "The creditor arrives before dawn.",
            "escalations": ["debt threat", "public humiliation"],
            "reversal_or_reveal": "The creditor serves another faction.",
            "payoff": "The protagonist refuses to kneel.",
            "ending_hook": "A stronger enemy notices the scene.",
        },
        style_dna={
            "pace": "brisk",
            "dialogue_reliance": "medium",
            "emotional_directness": "explicit",
        },
        evidence_spans=[
            EvidenceSpan(
                label="opening_hook",
                text="The creditor arrived before dawn.",
                paragraph_index=0,
                confidence="direct",
            )
        ],
        checkpoints=[
            CheckpointResult(
                name="chapter-function-fit",
                status="pass",
                evidence="The chapter cleanly escalates the debt conflict.",
                implication="Safe for approved pool.",
            )
        ],
        admission="approved",
        workbench_context={
            "recommended_stage": "middle",
            "narrative_signals": {"conflict_intensity": 0.76, "payoff_pressure": 0.31},
            "notes": "Conflict spike without payoff release.",
        },
    )

    assert record.primary_function == "conflict-escalation"
    assert record.checkpoints[0].status == "pass"
