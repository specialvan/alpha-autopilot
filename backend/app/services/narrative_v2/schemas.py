from __future__ import annotations

from pydantic import BaseModel, Field


class CharacterStatePayload(BaseModel):
    name: str
    presence: float = 0.0
    consistency_risk: float = 0.0
    relationship_tension: float = 0.0
    arc_progress: float = 0.0


class StoryStatePayload(BaseModel):
    chapter_index: int
    stage: str
    mainline_progress: float = Field(ge=0.0, le=1.0)
    sideplot_progress: float = Field(ge=0.0, le=1.0)
    conflict_intensity: float = Field(ge=0.0, le=1.0)
    emotional_temperature: float = Field(ge=0.0, le=1.0)
    pacing_speed: float = Field(ge=0.0, le=1.0)
    foreshadowing_load: float = Field(ge=0.0, le=1.0)
    payoff_pressure: float = Field(ge=0.0, le=1.0)
    characters: dict[str, CharacterStatePayload] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class NarrativeV2PreviewRequest(BaseModel):
    case_id: str
    state: StoryStatePayload
