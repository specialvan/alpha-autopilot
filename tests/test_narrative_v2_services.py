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
