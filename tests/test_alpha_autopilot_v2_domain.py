from alpha_autopilot_v2.domain.actions import (
    NarrativeAction,
    RecommendationResult,
    RuleCheck,
    SearchResult,
)
from alpha_autopilot_v2.domain.story import CharacterState, StoryState
from alpha_autopilot_v2.evaluation.service import EvaluationService
from alpha_autopilot_v2.feedback.models import FeedbackRecord
from alpha_autopilot_v2.rules.service import RuleService
from alpha_autopilot_v2.search.service import SearchService
from alpha_autopilot_v2.validation.models import ValidationRecord


def test_v2_domain_objects_can_be_instantiated() -> None:
    hero = CharacterState(
        name="hero",
        presence=0.8,
        consistency_risk=0.1,
        relationship_tension=0.6,
        arc_progress=0.3,
    )
    state = StoryState(
        chapter_index=12,
        stage="middle",
        mainline_progress=0.45,
        sideplot_progress=0.25,
        conflict_intensity=0.7,
        emotional_temperature=0.6,
        pacing_speed=0.55,
        foreshadowing_load=0.4,
        payoff_pressure=0.35,
        characters={"hero": hero},
        tags=["power", "fast"],
    )
    action = NarrativeAction(
        action="push_conflict",
        delta={"conflict_intensity": 0.1},
        explanation="Raise immediate confrontation.",
    )
    rule_check = RuleCheck(
        action="push_conflict",
        status="legal",
        prerequisites=["mainline_active"],
        blockers=[],
        risk_flags=["pace_up"],
    )
    result = SearchResult(
        action=action,
        rule_check=rule_check,
        score=1.2,
        details={"structure_value": 0.8},
    )
    recommendation = RecommendationResult(
        result=result,
        explanation="Conflict is currently the best legal move.",
    )

    assert state.characters["hero"].name == "hero"
    assert result.rule_check.status == "legal"
    assert recommendation.result.action.action == "push_conflict"


def test_v2_services_and_support_models_exist() -> None:
    state = StoryState(
        chapter_index=8,
        stage="middle",
        mainline_progress=0.42,
        sideplot_progress=0.22,
        conflict_intensity=0.64,
        emotional_temperature=0.58,
        pacing_speed=0.5,
        foreshadowing_load=0.38,
        payoff_pressure=0.32,
        characters={},
        tags=["power"],
    )
    checks = RuleService().evaluate(state)
    results = SearchService().search(state, checks)
    ranked = EvaluationService().rank(results)
    assert checks
    assert results
    assert ranked[0].score >= ranked[-1].score

    feedback = FeedbackRecord(
        stage="middle",
        action="push_conflict",
        predicted=1.2,
        target=1.0,
        feedback=0.9,
    )
    validation = ValidationRecord(
        case_id="case-001",
        accepted_actions=["push_conflict"],
        blocked_actions=["deliver_payoff"],
        top_action="push_conflict",
        notes="baseline expectation",
    )

    assert feedback.action == "push_conflict"
    assert validation.top_action == "push_conflict"
