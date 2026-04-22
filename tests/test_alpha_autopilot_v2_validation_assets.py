from __future__ import annotations

from alpha_autopilot_v2.validation.assets import ledger_dir, load_golden_cases, load_rule_fixtures


def test_v2_validation_assets_load_from_frozen_fixtures() -> None:
    golden_cases = load_golden_cases()
    rule_fixtures = load_rule_fixtures()

    assert len(golden_cases) >= 2
    assert len(rule_fixtures) >= 3

    middle_case = next(case for case in golden_cases if case.case_id == "golden-middle-conflict")
    blocked_payoff = next(item for item in rule_fixtures if item.fixture_id == "rule-middle-block-payoff")

    assert middle_case.state.stage == "middle"
    assert middle_case.expected_top_action == "push_conflict"
    assert "deliver_payoff" in middle_case.blocked_actions
    assert blocked_payoff.status == "blocked"
    assert blocked_payoff.blockers == ["payoff_pressure_low"]
    assert ledger_dir().name == "ledger"
