from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from alpha_autopilot_v2.domain import CharacterState, StoryState


@dataclass
class GoldenCase:
    case_id: str
    state: StoryState
    expected_top_action: str
    accepted_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class RuleFixture:
    fixture_id: str
    stage: str
    action: str
    status: str
    prerequisites: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    notes: str = ""


def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


def ledger_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "artifacts" / "v2" / "ledger"


def load_golden_cases() -> list[GoldenCase]:
    payload = _load_json(fixtures_dir() / "golden_cases.json")
    return [
        GoldenCase(
            case_id=item["case_id"],
            state=_build_story_state(item["state"]),
            expected_top_action=item["expected_top_action"],
            accepted_actions=list(item.get("accepted_actions", [])),
            blocked_actions=list(item.get("blocked_actions", [])),
            notes=item.get("notes", ""),
        )
        for item in payload
    ]


def load_rule_fixtures() -> list[RuleFixture]:
    payload = _load_json(fixtures_dir() / "rule_fixtures.json")
    return [
        RuleFixture(
            fixture_id=item["fixture_id"],
            stage=item["stage"],
            action=item["action"],
            status=item["status"],
            prerequisites=list(item.get("prerequisites", [])),
            blockers=list(item.get("blockers", [])),
            risk_flags=list(item.get("risk_flags", [])),
            notes=item.get("notes", ""),
        )
        for item in payload
    ]


def _load_json(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_story_state(raw: dict[str, object]) -> StoryState:
    characters_payload = raw.get("characters", {})
    characters = {
        name: value
        if isinstance(value, CharacterState)
        else CharacterState(**value)
        for name, value in characters_payload.items()
    }
    return StoryState(
        chapter_index=int(raw["chapter_index"]),
        stage=str(raw["stage"]),
        mainline_progress=float(raw["mainline_progress"]),
        sideplot_progress=float(raw["sideplot_progress"]),
        conflict_intensity=float(raw["conflict_intensity"]),
        emotional_temperature=float(raw["emotional_temperature"]),
        pacing_speed=float(raw["pacing_speed"]),
        foreshadowing_load=float(raw["foreshadowing_load"]),
        payoff_pressure=float(raw["payoff_pressure"]),
        characters=characters,
        tags=list(raw.get("tags", [])),
    )
