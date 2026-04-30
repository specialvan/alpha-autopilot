from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChapterTextInput(BaseModel):
    chapter_number: int | None = None
    title: str | None = None
    text: str = Field(min_length=1)
    author_note: str | None = None


class NarrativeSeedExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapters: list[ChapterTextInput] = Field(default_factory=list, min_length=1)
    mode: Literal["full", "incremental", "chapter_only"] = "full"
    existing_story_bible: dict[str, Any] | None = None
    compression_mode: str | None = None


class CharacterSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    first_appeared_chapter: int | None = None
    appearance_count: int = 0
    evidence_snippets: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class RelationshipTriple(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    relation: str
    target: str
    chapter_start: int | None = None
    chapter_end: int | None = None
    hidden: bool = False
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_sentence: str = ""


class WorldRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_sentence: str = ""


class PlotEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    participants: list[str] = Field(default_factory=list)
    impact_targets: list[str] = Field(default_factory=list)
    chapter_start: int | None = None
    chapter_end: int | None = None
    consequence: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_sentence: str = ""


class OpenThread(BaseModel):
    model_config = ConfigDict(extra="forbid")

    thread: str
    chapter_hint: int | None = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_sentence: str = ""


class NarrativePotential(BaseModel):
    model_config = ConfigDict(extra="forbid")

    highest_tension_points: list[str] = Field(default_factory=list)
    potential_payoffs: list[str] = Field(default_factory=list)
    potential_crises: list[str] = Field(default_factory=list)
    simulation_directions: list[str] = Field(default_factory=list)


class NarrativeSeed(BaseModel):
    model_config = ConfigDict(extra="forbid")

    characters: list[CharacterSeed] = Field(default_factory=list)
    relationship_triples: list[RelationshipTriple] = Field(default_factory=list)
    world_rules: list[WorldRule] = Field(default_factory=list)
    plot_events: list[PlotEvent] = Field(default_factory=list)
    open_threads: list[OpenThread] = Field(default_factory=list)
    narrative_potential: NarrativePotential = Field(default_factory=NarrativePotential)
    extraction_evidence: dict[str, list[str]] = Field(default_factory=dict)
    needs_review: list[str] = Field(default_factory=list)


class NarrativeSeedExtractionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed: NarrativeSeed
    relationship_graph_input: dict[str, Any] = Field(default_factory=dict)
    character_behavior_events: list[dict[str, Any]] = Field(default_factory=list)


class GraphRAGHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_type: str
    summary: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: str = ""
    hidden: bool = False


class GraphRAGRetrieveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    narrative_seed: NarrativeSeed | None = None
    relationship_graph_input: dict[str, Any] | None = None
    group_memory_graph: GroupMemoryGraph | None = None
    top_k: int = Field(default=4, ge=1, le=12)
    include_hidden: bool = False
    chapter_index: int | None = None


class GraphRAGRetrieveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    top_k: int
    hits: list[GraphRAGHit] = Field(default_factory=list)
    retrieval_mode: str = "deterministic"
    fallback_used: bool = False
    fallback_reason: str | None = None
    stitched_from_history_count: int = Field(default=0, ge=0)
    history_recall_used: bool = False


class GraphMemoryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    query: str
    query_tokens: list[str] = Field(default_factory=list)
    source_route: str
    chapter_index: int | None = None
    simulation_id: str | None = None
    node_id: str
    node_type: str
    summary: str
    evidence: str = ""
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    hidden: bool = False
    created_at_utc: str


class CharacterFunctionType(str, Enum):
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    DEUTERAGONIST = "deuteragonist"
    MENTOR = "mentor"
    RIVAL = "rival"
    DISGUISE = "disguise"
    CATALYST = "catalyst"
    CONFIDANT = "confidant"


class TurnTypeEnum(str, Enum):
    OBSTACLE_SHIFT = "obstacle_shift"
    GOAL_INVERSION = "goal_inversion"
    CHARACTER_CONTRAST = "character_contrast"


class EmotionSliderMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stress_baseline: float = Field(default=0.0, ge=-10.0, le=10.0)
    impulsiveness: float = Field(default=0.0, ge=-10.0, le=10.0)
    empathy: float = Field(default=0.0, ge=-10.0, le=10.0)
    dominance: float = Field(default=0.0, ge=-10.0, le=10.0)


class DesireProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    explicit_desire: str
    hidden_desire: str
    fear: str
    bottom_line: str
    current_goal: str


class BehaviorTrigger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pressure: str
    action: str
    rationale: str


class OverridePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str
    emotion_slider_map: EmotionSliderMap | None = None
    function_type: CharacterFunctionType | None = None
    dialogue_style_summary: str | None = None
    desire_profile: DesireProfile | None = None


class OverrideRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = "author_override"
    applied_fields: list[str] = Field(default_factory=list)


class ParameterizedCharacterProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    emotion_slider_map: EmotionSliderMap = Field(default_factory=EmotionSliderMap)
    function_type: CharacterFunctionType = CharacterFunctionType.CONFIDANT
    mbti_suggestion: str | None = None
    enneagram_suggestion: str | None = None
    dialogue_style_summary: str = ""
    desire_profile: DesireProfile
    behavior_triggers: list[BehaviorTrigger] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    override_log: list[OverrideRecord] = Field(default_factory=list)


class CharacterParameterizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed: NarrativeSeed
    selected_character_ids: list[str] = Field(default_factory=list)
    chapter_range: tuple[int | None, int | None] | None = None
    existing_profiles: list[ParameterizedCharacterProfile] = Field(default_factory=list)
    overrides: list[OverridePatch] = Field(default_factory=list)


class CharacterParameterizeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: list[ParameterizedCharacterProfile] = Field(default_factory=list)


class PlotUnitActionClimax(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node: str
    turn_type: TurnTypeEnum


class PlotUnitScaffold(BaseModel):
    model_config = ConfigDict(extra="forbid")

    encounter_event: str
    desire_goal: str
    obstacle: str
    solution_method: str
    action_climax: PlotUnitActionClimax
    resolution: str


class SimulationPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path_id: str
    strategy: str
    status: Literal["ok", "failed"] = "ok"
    initial_assumptions: list[str] = Field(default_factory=list)
    plot_outline: list[str] = Field(default_factory=list)
    six_step_scaffold_mapping: dict[str, str] = Field(default_factory=dict)
    character_reactions: list[dict[str, str]] = Field(default_factory=list)
    relationship_deltas: list[dict[str, Any]] = Field(default_factory=list)
    memory_deltas: list[dict[str, Any]] = Field(default_factory=list)
    retention_score: float = 0.0
    retention_breakdown: dict[str, float] = Field(default_factory=dict)
    consistency_issues: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    recommendation_rank: int | None = None
    causal_chain: dict[str, str] = Field(default_factory=dict)
    graph_rag_hints: list[str] = Field(default_factory=list)
    error_message: str | None = None


class ParallelSimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    story_state: dict[str, Any] = Field(default_factory=dict)
    narrative_seed: NarrativeSeed
    character_profiles: list[ParameterizedCharacterProfile] = Field(default_factory=list)
    relationship_graph_input: dict[str, Any] | None = None
    group_memory_graph: GroupMemoryGraph | None = None
    plot_unit_scaffold: PlotUnitScaffold | None = None
    retention_desire_vector: dict[str, float | str] = Field(default_factory=dict)
    macro_story_structure: str = "progressive"
    path_count: int = Field(default=3, ge=2, le=3)
    strategies: list[str] = Field(default_factory=list)
    simulation_id: str | None = None
    debug_force_fail_strategies: list[str] = Field(default_factory=list)
    graph_rag_query: str | None = None
    graph_rag_top_k: int = Field(default=3, ge=1, le=8)
    graph_rag_include_hidden: bool = False


class ParallelPlotSimulationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    simulation_id: str
    paths: list[SimulationPath] = Field(default_factory=list)
    winner_path_id: str | None = None
    decision_summary: str
    generated_at_utc: str
    risk_flags: list[str] = Field(default_factory=list)


class GroupDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: str
    name: str
    description: str = ""


class GroupMembership(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: str
    character_id: str
    role: str = "member"


class GroupMemoryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    group_id: str
    summary: str
    influence: dict[str, float] = Field(default_factory=dict)
    chapter_start: int | None = None
    chapter_end: int | None = None
    hidden: bool = False
    propagation_strength: float = Field(default=0.6, ge=0.0, le=1.0)


class BehaviorEffect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: str
    character_id: str
    effect: dict[str, float] = Field(default_factory=dict)
    source_memory_id: str
    hidden: bool = False


class GroupMemoryPropagationLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str
    group_id: str
    character_id: str
    status: str
    reason: str = ""


class ReversiblePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patch_id: str
    character_id: str
    reverse_effect: dict[str, float] = Field(default_factory=dict)
    source_memory_id: str


class GroupMemoryGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groups: list[GroupDefinition] = Field(default_factory=list)
    memberships: list[GroupMembership] = Field(default_factory=list)
    group_memories: list[GroupMemoryEvent] = Field(default_factory=list)
    behavior_effects: list[BehaviorEffect] = Field(default_factory=list)
    propagation_logs: list[GroupMemoryPropagationLog] = Field(default_factory=list)
    reversible_patches: list[ReversiblePatch] = Field(default_factory=list)


class GroupMemoryApplyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groups: list[GroupDefinition] = Field(default_factory=list)
    memberships: list[GroupMembership] = Field(default_factory=list)
    group_memories: list[GroupMemoryEvent] = Field(default_factory=list)
    chapter_index: int | None = None
    reveal_hidden: bool = False


class InteractionRound(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round_index: int
    exchanges: list[dict[str, Any]] = Field(default_factory=list)


class ConflictCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    trigger_characters: list[str] = Field(default_factory=list)
    trigger_relationship: str
    trigger_personality: str
    trigger_pressure: str
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)


class InformationLeak(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_character: str
    leaked_information: str
    risk: str


class EmergentConflictProbeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    characters: list[ParameterizedCharacterProfile] = Field(default_factory=list)
    relationship_graph_input: dict[str, Any] | None = None
    group_memory_graph: GroupMemoryGraph | None = None
    scene_constraints: dict[str, Any] = Field(default_factory=dict)
    rounds: int = Field(default=3, ge=1, le=6)


class EmergentConflictProbeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_rounds: list[InteractionRound] = Field(default_factory=list)
    conflict_candidates: list[ConflictCandidate] = Field(default_factory=list)
    information_leaks: list[InformationLeak] = Field(default_factory=list)
    relationship_changes: list[dict[str, Any]] = Field(default_factory=list)
    recommended_plot_hooks: list[str] = Field(default_factory=list)
    six_step_binding_suggestions: dict[str, str] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)


class InjectedWorldEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = ""
    event_type: str
    description: str
    affected_characters: list[str] = Field(default_factory=list)
    affected_groups: list[str] = Field(default_factory=list)
    happened_at: str = "immediate"
    force_level: float = Field(default=0.5, ge=0.0, le=1.0)


class EventInjectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    injected_event: InjectedWorldEvent
    author_intent: dict[str, Any] = Field(default_factory=dict)
    macro_story_structure: str = "progressive"


class EventInjectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    simulation_id: str
    previous_winner_path_id: str | None = None
    winner_path_id: str | None = None
    updated_paths: list[SimulationPath] = Field(default_factory=list)
    ranking_changes: list[dict[str, Any]] = Field(default_factory=list)
    macro_structure_risk: list[str] = Field(default_factory=list)
    destructive_confirmation_required: bool = False
    audit_log: list[dict[str, Any]] = Field(default_factory=list)
    decision_summary: str
    updated_simulation: ParallelPlotSimulationResult


class InterviewMode(str, Enum):
    VOICE_TEST = "voice_test"
    SCENE_REACTION = "scene_reaction"
    SECRET_PROBE = "secret_probe"
    FREE_CHAT = "free_chat"


class CharacterInterviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: ParameterizedCharacterProfile
    chapter_memory: list[str] = Field(default_factory=list)
    relationship_graph_input: dict[str, Any] | None = None
    group_memory_graph: GroupMemoryGraph | None = None
    user_message: str = Field(min_length=1)
    mode: InterviewMode = InterviewMode.FREE_CHAT
    allow_hidden_info: bool = False
    graph_rag_query: str | None = None
    graph_rag_top_k: int = Field(default=3, ge=1, le=8)
    graph_rag_include_hidden: bool = False
    chapter_index: int | None = None


class CharacterInterviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str
    reply: str
    memory_evidence: list[str] = Field(default_factory=list)
    emotion_state_shift: str = "stable"
    ooc_risk_flags: list[str] = Field(default_factory=list)
    hidden_info_risk_flags: list[str] = Field(default_factory=list)
    transcript: list[dict[str, str]] = Field(default_factory=list)
    plot_foreshadow_candidates: list[str] = Field(default_factory=list)
    graph_rag_hints: list[str] = Field(default_factory=list)
