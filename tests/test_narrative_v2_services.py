import pytest

from backend.app.services.narrative_v2.evaluation_service import NarrativeV2EvaluationService
from backend.app.services.narrative_v2.rule_service import NarrativeV2RuleService
from backend.app.services.narrative_v2.search_service import NarrativeV2SearchService
from backend.app.services.narrative_v2.state_builder import NarrativeV2StateBuilder
from backend.app.services.narrative_v2.validation_service import NarrativeV2ValidationService


def test_backend_narrative_v2_adapters_import_cleanly() -> None:
    payload = {
        "chapter_index": 5,
        "stage": "middle",
        "mainline_progress": 0.42,
        "sideplot_progress": 0.2,
        "conflict_intensity": 0.61,
        "emotional_temperature": 0.58,
        "pacing_speed": 0.47,
        "foreshadowing_load": 0.34,
        "payoff_pressure": 0.29,
        "tags": ["power"],
        "characters": {
            "hero": {
                "name": "hero",
                "presence": 0.8,
                "consistency_risk": 0.1,
                "relationship_tension": 0.5,
                "arc_progress": 0.25,
            }
        },
    }
    state = NarrativeV2StateBuilder().build(payload)
    checks = NarrativeV2RuleService().evaluate(state)
    results = NarrativeV2SearchService().search(state, checks)
    scored = NarrativeV2EvaluationService().rank(results)
    score = NarrativeV2EvaluationService().score_details({"structure_value": 0.4, "stage_fit": 0.2})
    record = NarrativeV2ValidationService().record(
        case_id="case-001",
        accepted_actions=["push_conflict"],
        blocked_actions=["deliver_payoff"],
        top_action="push_conflict",
        notes="baseline",
    )

    assert state.characters["hero"].name == "hero"
    assert len(checks) == 5
    assert {item.action: item.status for item in checks}["push_conflict"] == "legal"
    assert {item.action: item.status for item in checks}["deliver_payoff"] == "blocked"
    assert results
    assert all(item.rule_check.status == "legal" for item in results)
    assert scored[0].score >= scored[-1].score
    assert score == pytest.approx(0.34)
    assert record.top_action == "push_conflict"


def test_backend_narrative_v2_evaluation_rank_applies_retention_adjustments() -> None:
    payload = {
        "chapter_index": 25,
        "stage": "mid_late",
        "mainline_progress": 0.66,
        "sideplot_progress": 0.25,
        "conflict_intensity": 0.63,
        "emotional_temperature": 0.57,
        "pacing_speed": 0.51,
        "foreshadowing_load": 0.41,
        "payoff_pressure": 0.64,
        "tags": ["power"],
        "characters": {},
    }

    state = NarrativeV2StateBuilder().build(payload)
    checks = NarrativeV2RuleService().evaluate(state)
    search_service = NarrativeV2SearchService()
    baseline_results = search_service.search(state, checks)
    retention_results = search_service.search(state, checks)

    baseline_scored = NarrativeV2EvaluationService().rank(baseline_results)
    retention_scored = NarrativeV2EvaluationService().rank(retention_results, state=state)

    baseline_scores = {item.action.action: item.score for item in baseline_scored}
    retention_scores = {item.action.action: item.score for item in retention_scored}

    assert baseline_scores.keys() == retention_scores.keys()
    assert any(
        baseline_scores[action] != retention_scores[action] for action in baseline_scores
    )
    if "open_new_thread" in baseline_scores:
        assert retention_scores["open_new_thread"] <= baseline_scores["open_new_thread"]


def test_backend_narrative_v2_evaluation_exposes_retention_driver_for_main_decision_chain() -> None:
    payload = {
        "chapter_index": 19,
        "stage": "mid_late",
        "mainline_progress": 0.71,
        "sideplot_progress": 0.33,
        "conflict_intensity": 0.69,
        "emotional_temperature": 0.62,
        "pacing_speed": 0.53,
        "foreshadowing_load": 0.45,
        "payoff_pressure": 0.66,
        "tags": ["power"],
        "characters": {},
    }

    state = NarrativeV2StateBuilder().build(payload)
    checks = NarrativeV2RuleService().evaluate(state)
    search_service = NarrativeV2SearchService()
    results = search_service.search(state, checks)
    evaluation_service = NarrativeV2EvaluationService()
    scored = evaluation_service.rank(results, state=state)

    top = scored[0]
    driver = evaluation_service.build_retention_driver(top, state)

    assert "retention_target_score" in top.details
    assert "retention_guardrail_penalty" in top.details
    assert driver is not None
    assert driver["target_function"] == "reader-retention"
    assert driver["selected_final_score"] == top.score
