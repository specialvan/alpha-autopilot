from __future__ import annotations

from alpha_autopilot import StoryState


def base_state() -> StoryState:
    return StoryState(
        chapter_index=18,
        stage="middle",
        mainline_progress=0.61,
        sideplot_progress=0.37,
        conflict_intensity=0.64,
        emotional_temperature=0.53,
        pacing_speed=0.49,
        foreshadowing_load=0.36,
        payoff_pressure=0.31,
        tags=["power", "middle"],
    )
