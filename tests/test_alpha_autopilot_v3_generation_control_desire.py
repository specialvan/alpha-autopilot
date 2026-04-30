from __future__ import annotations

from alpha_autopilot_v3.decomposition.models import ChapterDecompositionRecord
from alpha_autopilot_v3.generation_control.policy import build_generation_control_plan
from alpha_autopilot_v3.retention.models import RetentionDesireVector


def _sample_record() -> ChapterDecompositionRecord:
    return ChapterDecompositionRecord(
        chapter_number=9,
        title="Conflict Pulse",
        scope="single",
        genre="xuanhuan",
        stage="middle",
        stage_inferred=False,
        primary_function="conflict-escalation",
        structure={"opening_hook": "A rival enters the hall."},
        style_dna={"pace": "brisk"},
        checkpoints=[],
    )


def test_generation_control_maps_primal_desire_to_hook_strategy() -> None:
    plan = build_generation_control_plan(
        _sample_record(),
        desire_vector=RetentionDesireVector.with_auto_dominant(
            primal_desire=0.9,
            value_recognition=0.3,
            knowledge_curiosity=0.2,
            information_gap=0.1,
        ),
    )

    assert plan.decision_tags["desire_dominant"] == "primal_desire"
    assert plan.hook_strategy == "escalate-power-survival-and-reward-hook"


def test_generation_control_maps_value_recognition_to_hook_strategy() -> None:
    plan = build_generation_control_plan(
        _sample_record(),
        desire_vector=RetentionDesireVector.with_auto_dominant(
            primal_desire=0.2,
            value_recognition=0.9,
            knowledge_curiosity=0.3,
            information_gap=0.1,
        ),
    )

    assert plan.decision_tags["desire_dominant"] == "value_recognition"
    assert plan.hook_strategy == "highlight-proof-recognition-and-status-reversal-hook"


def test_generation_control_maps_knowledge_curiosity_to_hook_strategy() -> None:
    plan = build_generation_control_plan(
        _sample_record(),
        desire_vector=RetentionDesireVector.with_auto_dominant(
            primal_desire=0.1,
            value_recognition=0.3,
            knowledge_curiosity=0.9,
            information_gap=0.2,
        ),
    )

    assert plan.decision_tags["desire_dominant"] == "knowledge_curiosity"
    assert plan.hook_strategy == "strengthen-rule-discovery-and-causal-payoff-hook"


def test_generation_control_maps_information_gap_to_hook_strategy() -> None:
    plan = build_generation_control_plan(
        _sample_record(),
        desire_vector=RetentionDesireVector.with_auto_dominant(
            primal_desire=0.2,
            value_recognition=0.4,
            knowledge_curiosity=0.2,
            information_gap=0.95,
        ),
    )

    assert plan.decision_tags["desire_dominant"] == "information_gap"
    assert plan.hook_strategy == "expand-information-gap-with-controlled-reveal-hook"


def test_generation_control_adjusts_macro_hook_weight_by_macro_structure() -> None:
    hub = build_generation_control_plan(
        _sample_record(),
        macro_structure="hub_and_spoke",
    )
    anthology = build_generation_control_plan(
        _sample_record(),
        macro_structure="anthology",
    )

    assert hub.decision_tags["macro_structure"] == "hub_and_spoke"
    assert hub.decision_tags["macro_hook_weight"] == 1.2
    assert anthology.decision_tags["macro_structure"] == "anthology"
    assert anthology.decision_tags["macro_hook_weight"] == 0.8
