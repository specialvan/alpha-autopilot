from __future__ import annotations

from alpha_autopilot_v2.evaluation.service import EvaluationService
from alpha_autopilot_v2.rules.service import RuleService
from alpha_autopilot_v2.search.service import SearchService
from alpha_autopilot_v2.validation.assets import load_golden_cases


def test_v2_golden_cases_match_expected_boundaries() -> None:
    rule_service = RuleService()
    search_service = SearchService()
    evaluation_service = EvaluationService()

    for case in load_golden_cases():
        checks = rule_service.evaluate(case.state)
        status_by_action = {item.action: item.status for item in checks}

        for accepted in case.accepted_actions:
            assert status_by_action.get(accepted) == "legal"
        for blocked in case.blocked_actions:
            assert status_by_action.get(blocked) in {"blocked", "prerequisite_missing"}

        ranked = evaluation_service.rank(search_service.search(case.state, checks))
        assert ranked
        assert ranked[0].action.action == case.expected_top_action
