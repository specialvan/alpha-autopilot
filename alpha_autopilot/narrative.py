from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class StoryState:
    chapter_index: int = 1
    stage: str = "opening"
    mainline_progress: float = 0.0
    sideplot_progress: float = 0.0
    conflict_intensity: float = 0.5
    emotional_temperature: float = 0.5
    pacing_speed: float = 0.5
    foreshadowing_load: float = 0.2
    payoff_pressure: float = 0.2
    characters: Dict[str, "CharacterState"] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class CharacterState:
    name: str
    presence: float = 0.5
    consistency_risk: float = 0.0
    relationship_tension: float = 0.5
    arc_progress: float = 0.0


@dataclass(frozen=True)
class NarrativeCandidate:
    action: str
    delta: Dict[str, float]
    explanation: str


@dataclass
class RecommendationResult:
    candidate: NarrativeCandidate
    score: float
    details: Dict[str, float]


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def apply_delta(state: StoryState, delta: Dict[str, float]) -> StoryState:
    new_state = StoryState(
        chapter_index=state.chapter_index + 1,
        stage=state.stage,
        mainline_progress=state.mainline_progress,
        sideplot_progress=state.sideplot_progress,
        conflict_intensity=state.conflict_intensity,
        emotional_temperature=state.emotional_temperature,
        pacing_speed=state.pacing_speed,
        foreshadowing_load=state.foreshadowing_load,
        payoff_pressure=state.payoff_pressure,
        characters={name: CharacterState(**vars(char)) for name, char in state.characters.items()},
        tags=list(state.tags),
    )
    for key, value in delta.items():
        if hasattr(new_state, key):
            setattr(new_state, key, clamp01(getattr(new_state, key) + value))
    return new_state
