from __future__ import annotations

from dataclasses import dataclass

from alpha_autopilot_v2.domain import CharacterState, StoryState


@dataclass
class NarrativeV2StateBuilder:
    def build(self, payload: dict[str, object]) -> StoryState:
        characters_payload = payload.get("characters", {})
        retention_desire_payload = payload.get("retention_desire")
        if hasattr(retention_desire_payload, "model_dump"):
            retention_desire_payload = retention_desire_payload.model_dump()
        retention_desire = (
            dict(retention_desire_payload)
            if isinstance(retention_desire_payload, dict)
            else None
        )
        macro_structure_raw = payload.get("macro_structure", "progressive")
        if hasattr(macro_structure_raw, "value"):
            macro_structure = str(macro_structure_raw.value)  # type: ignore[attr-defined]
        else:
            macro_structure = str(macro_structure_raw or "progressive")
        characters = {
            name: value
            if isinstance(value, CharacterState)
            else CharacterState(**value)
            for name, value in characters_payload.items()
        }
        return StoryState(
            chapter_index=int(payload["chapter_index"]),
            stage=str(payload["stage"]),
            mainline_progress=float(payload["mainline_progress"]),
            sideplot_progress=float(payload["sideplot_progress"]),
            conflict_intensity=float(payload["conflict_intensity"]),
            emotional_temperature=float(payload["emotional_temperature"]),
            pacing_speed=float(payload["pacing_speed"]),
            foreshadowing_load=float(payload["foreshadowing_load"]),
            payoff_pressure=float(payload["payoff_pressure"]),
            characters=characters,
            tags=list(payload.get("tags", [])),
            retention_desire=retention_desire,
            macro_structure=macro_structure,
        )
