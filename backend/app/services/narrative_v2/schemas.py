from __future__ import annotations

from typing import Any

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


class RuleStatusSummaryPayload(BaseModel):
    legal_count: int = 0
    blocked_count: int = 0
    prerequisite_missing_count: int = 0


class NarrativeV2DecisionCandidatePayload(BaseModel):
    action: str
    score: float
    explanation: str = ""
    details: dict[str, float] = Field(default_factory=dict)


class NarrativeV2RetentionDriverPayload(BaseModel):
    target_function: str = "reader-retention"
    primary_objective: str = ""
    priority_order: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    selected_base_score: float = 0.0
    selected_retention_score: float = 0.0
    selected_guardrail_penalty: float = 0.0
    selected_final_score: float = 0.0
    control_mode: str = "balance-and-sharpen"
    decision_tags: dict[str, Any] = Field(default_factory=dict)


class NarrativeV2DecisionPayload(BaseModel):
    selected_action: str = ""
    selected_score: float = 0.0
    accepted_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    prerequisite_missing_actions: list[str] = Field(default_factory=list)
    rule_status_summary: RuleStatusSummaryPayload = Field(default_factory=RuleStatusSummaryPayload)
    constraint_hint: str = "clear"
    validation_case_id: str = ""
    quality_hint: str = "blocked"
    explanation: str = ""
    details: dict[str, float] = Field(default_factory=dict)
    candidates: list[NarrativeV2DecisionCandidatePayload] = Field(default_factory=list)
    retention_driver: NarrativeV2RetentionDriverPayload | None = None
