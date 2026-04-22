from __future__ import annotations

from alpha_autopilot_v2.domain import StoryState
from alpha_autopilot_v2.rules.service import RuleService
from alpha_autopilot_v2.validation.assets import load_rule_fixtures


def _state_for_fixture(fixture_id: str) -> StoryState:
    if fixture_id == "rule-middle-legal-conflict":
        return StoryState(
            chapter_index=13,
            stage="middle",
            mainline_progress=0.48,
            sideplot_progress=0.31,
            conflict_intensity=0.66,
            emotional_temperature=0.58,
            pacing_speed=0.52,
            foreshadowing_load=0.39,
            payoff_pressure=0.33,
            characters={},
            tags=["power"],
        )
    if fixture_id == "rule-middle-block-payoff":
        return StoryState(
            chapter_index=13,
            stage="middle",
            mainline_progress=0.48,
            sideplot_progress=0.31,
            conflict_intensity=0.66,
            emotional_temperature=0.58,
            pacing_speed=0.52,
            foreshadowing_load=0.39,
            payoff_pressure=0.33,
            characters={},
            tags=["power"],
        )
    if fixture_id == "rule-late-missing-thread":
        return StoryState(
            chapter_index=34,
            stage="late",
            mainline_progress=0.86,
            sideplot_progress=0.72,
            conflict_intensity=0.74,
            emotional_temperature=0.76,
            pacing_speed=0.61,
            foreshadowing_load=0.28,
            payoff_pressure=0.82,
            characters={},
            tags=["power", "payoff"],
        )
    raise AssertionError(f"Unexpected fixture id: {fixture_id}")


def test_v2_rule_runtime_matches_frozen_rule_fixtures() -> None:
    service = RuleService()
    for fixture in load_rule_fixtures():
        state = _state_for_fixture(fixture.fixture_id)
        checks = {item.action: item for item in service.evaluate(state)}
        assert fixture.action in checks
        selected = checks[fixture.action]
        assert selected.status == fixture.status
        if fixture.blockers:
            assert set(fixture.blockers).issubset(set(selected.blockers))
