from __future__ import annotations

from alpha_autopilot_v2.domain import NarrativeAction, RuleCheck, SearchResult, StoryState

from backend.app.services.narrative_v2.evaluation_service import (
    NarrativeV2EvaluationService,
    _build_priority_weights,
)


def _state(macro_structure: str) -> StoryState:
    return StoryState(
        chapter_index=8,
        stage="middle",
        mainline_progress=0.45,
        sideplot_progress=0.22,
        conflict_intensity=0.64,
        emotional_temperature=0.58,
        pacing_speed=0.50,
        foreshadowing_load=0.38,
        payoff_pressure=0.32,
        tags=["power"],
        macro_structure=macro_structure,
    )


def test_macro_structure_changes_priority_weights_for_hook_signals() -> None:
    progressive = _build_priority_weights(
        ["hook-strength", "conflict-drive", "chapter-attraction"],
        stage="middle",
        macro_structure="progressive",
    )
    hub = _build_priority_weights(
        ["hook-strength", "conflict-drive", "chapter-attraction"],
        stage="middle",
        macro_structure="hub_and_spoke",
    )
    anthology = _build_priority_weights(
        ["hook-strength", "conflict-drive", "chapter-attraction"],
        stage="middle",
        macro_structure="anthology",
    )

    assert hub["hook-strength"] > progressive["hook-strength"]
    assert anthology["hook-strength"] < progressive["hook-strength"]


def test_retention_driver_includes_macro_structure_in_decision_tags() -> None:
    service = NarrativeV2EvaluationService()
    recommendation = SearchResult(
        action=NarrativeAction(
            action="push_conflict",
            delta={"conflict_intensity": 0.16},
            explanation="Raise direct confrontation.",
        ),
        rule_check=RuleCheck(action="push_conflict", status="legal"),
        score=0.8,
        details={
            "structure_value": 0.82,
            "continuity_safety": 0.71,
            "foreshadow_balance": 0.62,
            "stage_fit": 1.0,
            "feasibility": 1.0,
        },
    )

    driver = service.build_retention_driver(recommendation, _state("anthology"))

    assert driver is not None
    assert driver["decision_tags"]["macro_structure"] == "anthology"
