from __future__ import annotations

import json
from pathlib import Path

from alpha_autopilot import FeatureMatrix, StoryState, recommend_chapter


ROOT = Path(__file__).resolve().parent
SAMPLES_PATH = ROOT / "samples.json"


def build_state() -> StoryState:
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


def main() -> None:
    state = build_state()
    recommendations = recommend_chapter(state, FeatureMatrix())
    print(json.dumps({"state": state.__dict__, "recommendations": recommendations}, ensure_ascii=False, indent=2, default=lambda o: o.__dict__))


if __name__ == "__main__":
    main()
