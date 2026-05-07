from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .retention_desire import RetentionDesireVector


class MacroStructureEnum(str, Enum):
    HUB_AND_SPOKE = "hub_and_spoke"
    PROGRESSIVE = "progressive"
    ANTHOLOGY = "anthology"


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
    retention_desire: RetentionDesireVector | None = None
    macro_structure: MacroStructureEnum = MacroStructureEnum.PROGRESSIVE


class TurnTypeEnum(str, Enum):
    OBSTACLE_SHIFT = "obstacle_shift"
    GOAL_INVERSION = "goal_inversion"
    CHARACTER_CONTRAST = "character_contrast"


class PlotUnitActionClimax(BaseModel):
    node: str
    turn_type: TurnTypeEnum


class PlotUnitScaffold(BaseModel):
    encounter_event: str
    desire_goal: str
    obstacle: str
    solution_method: str
    action_climax: PlotUnitActionClimax
    resolution: str


class NarrativeV2PreviewRequest(BaseModel):
    case_id: str
    state: StoryStatePayload
    plot_unit_scaffold: PlotUnitScaffold | None = None


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


class StoryStateContextPayload(BaseModel):
    chapter_index: int
    stage: str
    mainline_progress: float = Field(ge=0.0, le=1.0)
    sideplot_progress: float = Field(ge=0.0, le=1.0)
    conflict_intensity: float = Field(ge=0.0, le=1.0)
    emotional_temperature: float = Field(ge=0.0, le=1.0)
    pacing_speed: float = Field(ge=0.0, le=1.0)
    foreshadowing_load: float = Field(ge=0.0, le=1.0)
    payoff_pressure: float = Field(ge=0.0, le=1.0)
    characters: dict[str, dict[str, Any]] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    macro_structure: MacroStructureEnum = MacroStructureEnum.PROGRESSIVE


class NarrativeV2ContextCheckpointPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    status: str
    evidence: str | None = None
    implication: str | None = None


class NarrativeV2ContextQualityPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    admission: str | None = None
    primary_function: str | None = None
    style_dna: dict[str, str] = Field(default_factory=dict)
    checkpoints: list[NarrativeV2ContextCheckpointPayload] = Field(default_factory=list)
    checkpoint_summary: dict[str, int] | None = None
    quality_notes: str | None = None


class NarrativeV2CompareBaselinePayload(BaseModel):
    baseline_context_id: str | None = None
    baseline_chapter_number: int | None = None
    delta: dict[str, float] = Field(default_factory=dict)


class NarrativeV4WorkbenchCandidatePayload(BaseModel):
    candidate_id: str = ""
    predicted_action: str = ""
    predicted_turning_point: str = ""
    predicted_conflict_type: str = ""
    predicted_payoff_type: str = ""
    retention_score: float = 0.0
    tension_score: float = 0.0
    explanation: str = ""
    risk_flags: list[str] = Field(default_factory=list)


class NarrativeV4WorkbenchPreviewPayload(BaseModel):
    enabled: bool
    fallback_reason: str | None = None
    candidate_count: int = 0
    retention_sort_key: str | None = None
    relationship_graph: dict[str, Any] = Field(default_factory=dict)
    relationship_displacements: list[dict[str, Any]] = Field(default_factory=list)
    relationship_timeline: list[dict[str, Any]] = Field(default_factory=list)
    candidate_timeline: list[dict[str, Any]] = Field(default_factory=list)
    genre_calibration: dict[str, Any] = Field(default_factory=dict)
    retention_writeback: dict[str, Any] = Field(default_factory=dict)
    character_behavior_constraints: list[dict[str, Any]] = Field(default_factory=list)
    character_validation: dict[str, Any] = Field(default_factory=dict)
    relationship_graph_constraints: dict[str, Any] = Field(default_factory=dict)
    prompt_documents: dict[str, str] = Field(default_factory=dict)
    prompt_compression_logs: list[dict[str, Any]] = Field(default_factory=list)
    memory_summary: dict[str, Any] = Field(default_factory=dict)
    selected_candidate: NarrativeV4WorkbenchCandidatePayload | None = None
    top_candidates: list[NarrativeV4WorkbenchCandidatePayload] = Field(default_factory=list)
    qc_summary: dict[str, Any] = Field(default_factory=dict)
    v4_input_profile: dict[str, Any] = Field(default_factory=dict)


class NarrativeV8WorkbenchPreviewPayload(BaseModel):
    enabled: bool
    fallback_reason: str | None = None
    decision_mode: str | None = None
    primary_knife_id: str | None = None
    secondary_knife_id: str | None = None
    fallback_action: str | None = None
    next_control_state: str | None = None
    transition: dict[str, Any] | None = None
    followup_scene: dict[str, Any] | None = None
    explanation: dict[str, str] = Field(default_factory=dict)
    future_hooks: list[dict[str, Any]] = Field(default_factory=list)
    risk_if_exposed: list[str] = Field(default_factory=list)
    v8_input_profile: dict[str, Any] = Field(default_factory=dict)


class NarrativeV2WorkbenchContextPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    chapterNumber: int
    title: str
    stage: str
    summary: str
    state: StoryStateContextPayload
    compare_baseline: NarrativeV2CompareBaselinePayload | None = None
    v4_preview: NarrativeV4WorkbenchPreviewPayload | None = None
    v8_preview: NarrativeV8WorkbenchPreviewPayload | None = None
    quality: NarrativeV2ContextQualityPayload | None = None
    admission: str | None = None
    primary_function: str | None = None
    style_dna: dict[str, str] = Field(default_factory=dict)
    checkpoints: list[NarrativeV2ContextCheckpointPayload] = Field(default_factory=list)
    checkpoint_summary: dict[str, int] | None = None
    quality_notes: str | None = None


class NarrativeV2WorkbenchContextsResponsePayload(BaseModel):
    contexts: list[NarrativeV2WorkbenchContextPayload] = Field(default_factory=list)
    source: str | None = None
    context_contract: str | None = None
    fallback_reason: str | None = None
    report_path: str | None = None
    report_url: str | None = None
    run_id: str | None = None
    manifest_path: str | None = None
    preferred_model: str | None = None
    resolved_model: str | None = None
    report_success_rate: float | None = None
    report_timestamp: str | None = None
    arbitration_strategy: str | None = None
    source_diagnostics: dict[str, Any] = Field(default_factory=dict)
