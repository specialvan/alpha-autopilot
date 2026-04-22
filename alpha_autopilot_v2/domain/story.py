from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CharacterState:
    name: str
    presence: float = 0.0
    consistency_risk: float = 0.0
    relationship_tension: float = 0.0
    arc_progress: float = 0.0


@dataclass
class StoryState:
    chapter_index: int
    stage: str
    mainline_progress: float
    sideplot_progress: float
    conflict_intensity: float
    emotional_temperature: float
    pacing_speed: float
    foreshadowing_load: float
    payoff_pressure: float
    characters: dict[str, CharacterState] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
