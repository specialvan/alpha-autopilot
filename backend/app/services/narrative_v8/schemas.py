from __future__ import annotations

from typing import Literal, Mapping, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator


PsychologyLiteracyLevel: TypeAlias = Literal[
    "instinctive",
    "experiential",
    "semi_systematic",
    "systematic",
]
TimeHorizon: TypeAlias = Literal["short", "mid", "long"]
ShameRelation: TypeAlias = Literal["avoidant", "weaponized", "ritualized", "denied"]
WitnessNeed: TypeAlias = Literal["low", "mid", "high"]
ArenaType: TypeAlias = Literal[
    "shitu",
    "menpai",
    "shijia",
    "chaotang",
    "jianghu",
    "qingzhai",
    "ziyuan",
    "mingsheng",
]
StakeType: TypeAlias = Literal["status", "bond", "resource", "reputation", "survival"]
RelationshipDistance: TypeAlias = Literal["intimate", "personal", "formal", "distant"]
SceneVisibility: TypeAlias = Literal["private", "semi_public", "public"]
TimePressure: TypeAlias = Literal["low", "mid", "high"]
ControlPhase: TypeAlias = Literal[
    "probe",
    "pressure_test",
    "containment",
    "conversion",
    "harvest",
]
ControlSurfaceState: TypeAlias = Literal[
    "harmless",
    "suspicious",
    "distrusted",
    "repair_attempt",
    "partially_restored",
    "upgraded",
    "more_hidden",
    "stronger",
    "hardened",
    "collapsed",
]
FailureMode: TypeAlias = Literal[
    "shell_exposed",
    "pace_lost",
    "position_locked",
    "narrative_lost",
]
RecoveryMode: TypeAlias = Literal[
    "re_feel_vulnerability",
    "lower_intensity",
    "retreat_to_safer_role",
    "change_scene",
    "re_establish_decorum",
    "re_establish_narrative_control",
]
UpgradeTrigger: TypeAlias = Literal[
    "primitive_stalled",
    "shell_seen_through",
    "higher_order_path_found",
]
UpgradePath: TypeAlias = Literal[
    "more_hidden",
    "more_sparse",
    "more_systemic",
    "more_enduring",
    "more_complex",
    "outsourced_interpretation",
]
StructuralTarget: TypeAlias = Literal[
    "external_move",
    "risk_if_exposed",
    "future_hooks",
    "state_shift",
]
StateShiftFocus: TypeAlias = Literal["relationship", "narrative", "psychological", "hook"]
FallbackAction: TypeAlias = Literal[
    "hold_position",
    "gather_information",
    "defer_to_public_mask",
    "reduce_exposure",
]


class NarrativeV8BaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _looks_like_flavor_render(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    render_only_keys = {
        "delivery_surface",
        "pressure_channel",
        "witness_posture",
        "cost_profile",
        "hook_style",
        "structural_targets",
        "state_shift_focus",
    }
    return any(key in value for key in render_only_keys)


def _layer_abs_totals(shift: "StateLedgerShift") -> dict[str, int]:
    return {
        "relationship": sum(
            abs(value)
            for value in (
                shift.relationship.trust_delta,
                shift.relationship.debt_delta,
                shift.relationship.dependency_delta,
                shift.relationship.leverage_delta,
            )
        ),
        "narrative": sum(
            abs(value)
            for value in (
                shift.narrative.suspicion_delta,
                shift.narrative.reputation_delta,
                shift.narrative.witness_alignment_delta,
                shift.narrative.explanation_control_delta,
            )
        ),
        "psychological": sum(
            abs(value)
            for value in (
                shift.psychological.shame_load_delta,
                shift.psychological.wound_activation_delta,
                shift.psychological.protector_trigger_delta,
                shift.psychological.identity_destabilization_delta,
            )
        ),
        "hook": len(shift.hook.planted_hooks)
        + len(shift.hook.armed_payoffs)
        + len(shift.hook.recovered_hooks),
    }


class KnifeConstraintSet(NarrativeV8BaseModel):
    scene_restrictions: tuple[str, ...] = ()
    target_restrictions: tuple[str, ...] = ()
    observer_requirements: tuple[str, ...] = ()
    anti_conditions: tuple[str, ...] = ()
    backfire_conditions: tuple[str, ...] = ()
    ineffective_conditions: tuple[str, ...] = ()
    flavor_conflicts: tuple[str, ...] = ()


class KnifePrimitive(NarrativeV8BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    emotional_disguise: tuple[str, ...] = ()
    target_vulnerabilities: tuple[str, ...] = ()
    best_arenas: tuple[ArenaType, ...] = ()
    risks: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    compatible_with: tuple[str, ...] = ()
    incompatible_with: tuple[str, ...] = ()
    constraints: KnifeConstraintSet = Field(default_factory=KnifeConstraintSet)


class KnifeCompatibilityEdge(NarrativeV8BaseModel):
    left: str = Field(min_length=1)
    right: str = Field(min_length=1)
    relation: Literal["compatible", "incompatible", "conditional"]
    reason: str = Field(min_length=1)


class FlavorAxisProfile(NarrativeV8BaseModel):
    temperature: Literal["cold", "soft", "hot", "faded", "sacred", "decadent"]
    rituality: Literal["low", "mid", "high"]
    sensuality: Literal["low", "mid", "high"]
    theatricality: Literal["low", "mid", "high"]
    cruelty_visibility: Literal["hidden", "mixed", "open"]
    witness_dependence: Literal["private", "mixed", "public"]
    control_preference: Literal[
        "private_invasion",
        "public_rewrite",
        "resource_cut",
        "emotional_absorption",
    ]


class VillainProfile(NarrativeV8BaseModel):
    id: str = Field(min_length=1)
    archetype: str = Field(min_length=1)
    core_wound: str = Field(min_length=1)
    core_belief: str = Field(min_length=1)
    psychology_literacy: PsychologyLiteracyLevel
    preferred_knives: tuple[str, ...]
    secondary_knives: tuple[str, ...] = ()
    forbidden_moves: tuple[str, ...]
    public_mask: tuple[str, ...]
    private_drive: tuple[str, ...]
    time_horizon: TimeHorizon
    blind_spot: str = Field(min_length=1)
    escalation_rule: str = Field(min_length=1)
    shame_relation: ShameRelation
    witness_need: WitnessNeed
    flavor_profile: FlavorAxisProfile

    @model_validator(mode="before")
    @classmethod
    def _reject_flavor_render_input(cls, value: object) -> object:
        if isinstance(value, dict) and _looks_like_flavor_render(value.get("flavor_profile")):
            raise ValueError("flavor_profile must use FlavorAxisProfile, not FlavorRender")
        return value

    @model_validator(mode="after")
    def _validate_constraints(self) -> "VillainProfile":
        if not 1 <= len(self.preferred_knives) <= 3:
            raise ValueError("preferred_knives must contain 1 to 3 items")
        if len(self.secondary_knives) > 2:
            raise ValueError("secondary_knives must contain at most 2 items")
        if not self.forbidden_moves:
            raise ValueError("forbidden_moves must not be empty")
        overlap = set(self.preferred_knives).intersection(self.forbidden_moves)
        if overlap:
            raise ValueError(
                f"preferred_knives must not overlap forbidden_moves: {sorted(overlap)!r}"
            )
        return self


class TargetProfile(NarrativeV8BaseModel):
    id: str = Field(min_length=1)
    self_image: str = Field(min_length=1)
    core_need: str = Field(min_length=1)
    core_fear: str = Field(min_length=1)
    weak_points: tuple[str, ...]
    defense_style: str = Field(min_length=1)
    resistance_style: str = Field(min_length=1)
    witness_sensitivity: Literal["low", "mid", "high"]
    identity_anchor: str = Field(min_length=1)
    social_priorities: tuple[str, ...] = ()


class FutureHook(NarrativeV8BaseModel):
    id: str = Field(min_length=1)
    source_knife_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    payoff_window: Literal["immediate", "near", "mid", "long"]
    recovery_condition: str = Field(min_length=1)


class RelationshipLedgerState(NarrativeV8BaseModel):
    trust: int = Field(default=0, ge=-3, le=3)
    debt: int = Field(default=0, ge=-3, le=3)
    dependency: int = Field(default=0, ge=-3, le=3)
    leverage: int = Field(default=0, ge=-3, le=3)


class NarrativeLedgerState(NarrativeV8BaseModel):
    suspicion: int = Field(default=0, ge=-3, le=3)
    reputation: int = Field(default=0, ge=-3, le=3)
    witness_alignment: int = Field(default=0, ge=-3, le=3)
    explanation_control: int = Field(default=0, ge=-3, le=3)


class PsychologicalLedgerState(NarrativeV8BaseModel):
    shame_load: int = Field(default=0, ge=-3, le=3)
    wound_activation: int = Field(default=0, ge=-3, le=3)
    protector_trigger: int = Field(default=0, ge=-3, le=3)
    identity_destabilization: int = Field(default=0, ge=-3, le=3)


class HookLedgerState(NarrativeV8BaseModel):
    planted_hooks: tuple[FutureHook, ...] = ()
    armed_payoffs: tuple[FutureHook, ...] = ()
    recovered_hooks: tuple[str, ...] = ()


class LedgerSnapshot(NarrativeV8BaseModel):
    relationship: RelationshipLedgerState = Field(default_factory=RelationshipLedgerState)
    narrative: NarrativeLedgerState = Field(default_factory=NarrativeLedgerState)
    psychological: PsychologicalLedgerState = Field(default_factory=PsychologicalLedgerState)
    hook: HookLedgerState = Field(default_factory=HookLedgerState)


class RelationshipLedgerShift(NarrativeV8BaseModel):
    trust_delta: int = Field(default=0, ge=-3, le=3)
    debt_delta: int = Field(default=0, ge=-3, le=3)
    dependency_delta: int = Field(default=0, ge=-3, le=3)
    leverage_delta: int = Field(default=0, ge=-3, le=3)


class NarrativeLedgerShift(NarrativeV8BaseModel):
    suspicion_delta: int = Field(default=0, ge=-3, le=3)
    reputation_delta: int = Field(default=0, ge=-3, le=3)
    witness_alignment_delta: int = Field(default=0, ge=-3, le=3)
    explanation_control_delta: int = Field(default=0, ge=-3, le=3)


class PsychologicalLedgerShift(NarrativeV8BaseModel):
    shame_load_delta: int = Field(default=0, ge=-3, le=3)
    wound_activation_delta: int = Field(default=0, ge=-3, le=3)
    protector_trigger_delta: int = Field(default=0, ge=-3, le=3)
    identity_destabilization_delta: int = Field(default=0, ge=-3, le=3)


class HookLedgerShift(NarrativeV8BaseModel):
    planted_hooks: tuple[FutureHook, ...] = ()
    armed_payoffs: tuple[FutureHook, ...] = ()
    recovered_hooks: tuple[str, ...] = ()


class StateLedgerShift(NarrativeV8BaseModel):
    relationship: RelationshipLedgerShift = Field(default_factory=RelationshipLedgerShift)
    narrative: NarrativeLedgerShift = Field(default_factory=NarrativeLedgerShift)
    psychological: PsychologicalLedgerShift = Field(default_factory=PsychologicalLedgerShift)
    hook: HookLedgerShift = Field(default_factory=HookLedgerShift)


class SceneObserver(NarrativeV8BaseModel):
    id: str = Field(min_length=1)
    role: Literal["witness", "judge", "transmitter", "buffer", "recovery_node"]
    alignment: Literal["villain", "target", "mixed", "volatile", "unknown"]
    importance: int = Field(ge=1, le=3)
    visibility_impact: int = Field(ge=-3, le=3)


class PowerEdge(NarrativeV8BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    relation: str = Field(min_length=1)
    asymmetry: int = Field(ge=-3, le=3)


class SceneContext(NarrativeV8BaseModel):
    arena: ArenaType
    stake: StakeType
    observers: tuple[SceneObserver, ...]
    power_topology: tuple[PowerEdge, ...]
    relationship_distance: RelationshipDistance
    visibility: SceneVisibility
    time_pressure: TimePressure
    current_phase: ControlPhase
    current_control_state: ControlSurfaceState
    existing_state: LedgerSnapshot = Field(default_factory=LedgerSnapshot)

    @model_validator(mode="after")
    def _validate_public_observers(self) -> "SceneContext":
        if self.visibility == "public" and not self.observers:
            raise ValueError("public scenes must declare at least one observer")
        return self


class SelectedKnifeSignal(NarrativeV8BaseModel):
    knife_id: str = Field(min_length=1)
    fit_score: float = Field(ge=0.0, le=1.0)
    reasons: tuple[str, ...]


class RejectedKnifeReason(NarrativeV8BaseModel):
    knife_id: str = Field(min_length=1)
    category: Literal[
        "forbidden_move",
        "scene_restriction",
        "target_restriction",
        "observer_requirement_missing",
        "anti_condition",
        "compatibility_conflict",
        "backfire_condition",
        "ineffective_condition",
        "flavor_conflict",
        "low_fit_score",
    ]
    detail: str = Field(min_length=1)


class DecisionLayer(NarrativeV8BaseModel):
    selection_mode: Literal["scored_fit", "fallback"]
    primary_knife_id: str | None = None
    secondary_knife_id: str | None = None
    fallback_action: FallbackAction | None = None
    fallback_reason: str | None = None
    selected_signals: tuple[SelectedKnifeSignal, ...] = ()
    rejected_knives: tuple[RejectedKnifeReason, ...] = ()

    @model_validator(mode="after")
    def _validate_mode_shape(self) -> "DecisionLayer":
        if self.selection_mode == "fallback":
            if self.primary_knife_id is not None or self.secondary_knife_id is not None:
                raise ValueError("fallback decision must not carry knife ids")
            if self.selected_signals:
                raise ValueError("fallback decision must not carry selected_signals")
            if self.fallback_action is None or not self.fallback_reason:
                raise ValueError("fallback decision requires fallback_action and fallback_reason")
            return self

        if self.primary_knife_id is None:
            raise ValueError("scored_fit decision requires a primary_knife_id")
        if not self.selected_signals:
            raise ValueError("scored_fit decision requires non-empty selected_signals")
        if self.fallback_action is not None or self.fallback_reason is not None:
            raise ValueError("scored_fit decision must not carry fallback metadata")
        return self


class ExplanationLayer(NarrativeV8BaseModel):
    external_move: str = Field(min_length=1)
    inner_drive: str = Field(min_length=1)
    target_misread: str = Field(min_length=1)
    why_now: str = Field(min_length=1)
    why_this_choice: str = Field(min_length=1)
    why_this_villain_style: str = Field(min_length=1)


class TransitionLayer(NarrativeV8BaseModel):
    prior_state: ControlSurfaceState
    next_state: ControlSurfaceState
    failure_mode: FailureMode | None = None
    recovery_mode: RecoveryMode | None = None
    upgrade_trigger: UpgradeTrigger | None = None
    upgrade_path: UpgradePath | None = None
    transition_reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_transition_consistency(self) -> "TransitionLayer":
        if self.upgrade_path is not None and self.upgrade_trigger is None:
            raise ValueError("upgrade_path requires upgrade_trigger")
        if self.next_state == "collapsed" and self.recovery_mode is not None:
            raise ValueError("collapsed transition must not carry recovery_mode")
        return self


class FlavorRender(NarrativeV8BaseModel):
    tone: str = Field(min_length=1)
    aesthetic: tuple[str, ...]
    social_surface: tuple[str, ...]
    private_subtext: tuple[str, ...]
    delivery_surface: Literal[
        "private_softness",
        "public_innocence",
        "ritual_distance",
        "courteous_superiority",
        "fatigued_reserve",
    ]
    pressure_channel: Literal[
        "self_image",
        "witness_pressure",
        "guilt_pull",
        "status_gap",
        "dependency_pull",
        "memory_reframe",
    ]
    witness_posture: Literal[
        "avoid_witness",
        "use_witness",
        "perform_for_judge",
        "seed_for_transmitter",
        "hide_from_recovery_node",
    ]
    cost_profile: Literal[
        "low_exposure",
        "delayed_exposure",
        "high_backfire",
        "reputation_bet",
    ]
    hook_style: Literal[
        "debt_seed",
        "shame_seed",
        "misread_seed",
        "dependency_seed",
        "public_record_seed",
    ]
    structural_targets: tuple[StructuralTarget, ...]
    state_shift_focus: StateShiftFocus

    @model_validator(mode="after")
    def _validate_structural_targets(self) -> "FlavorRender":
        if len(set(self.structural_targets)) < 2:
            raise ValueError("structural_targets must declare at least two packet surfaces")
        return self


class VillainFeedbackPacket(NarrativeV8BaseModel):
    villain_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    scene_arena: ArenaType
    decision: DecisionLayer
    explanation: ExplanationLayer
    transition: TransitionLayer
    state_shift: StateLedgerShift
    future_hooks: tuple[FutureHook, ...] = ()
    risk_if_exposed: tuple[str, ...] = ()
    flavor_render: FlavorRender

    @model_validator(mode="after")
    def _validate_flavor_focus(self) -> "VillainFeedbackPacket":
        totals = _layer_abs_totals(self.state_shift)
        max_total = max(totals.values())
        if max_total > 0 and totals[self.flavor_render.state_shift_focus] != max_total:
            raise ValueError("flavor_render.state_shift_focus must match the packet state emphasis")
        return self


class BuildVillainFeedbackInput(NarrativeV8BaseModel):
    villain: VillainProfile
    target: TargetProfile
    scene: SceneContext
    knife_library: tuple[KnifePrimitive, ...] = ()


class BuildVillainFeedbackOutput(NarrativeV8BaseModel):
    packet: VillainFeedbackPacket
    next_snapshot: LedgerSnapshot
    next_control_state: ControlSurfaceState

    @model_validator(mode="after")
    def _validate_control_surface_handoff(self) -> "BuildVillainFeedbackOutput":
        if self.next_control_state != self.packet.transition.next_state:
            raise ValueError("next_control_state must match packet.transition.next_state")
        return self

    def build_followup_scene(
        self,
        scene: SceneContext | dict[str, object],
        *,
        updates: Mapping[str, object] | None = None,
    ) -> SceneContext:
        update_payload = dict(updates or {})
        blocked_fields = {"current_control_state", "existing_state"}.intersection(update_payload)
        if blocked_fields:
            blocked = ", ".join(sorted(blocked_fields))
            raise ValueError(
                f"handoff-managed fields must not be overridden manually: {blocked}"
            )

        base_scene = scene if isinstance(scene, SceneContext) else SceneContext.model_validate(scene)
        payload = base_scene.model_dump()
        payload.update(update_payload)
        payload["current_control_state"] = self.next_control_state
        payload["existing_state"] = self.next_snapshot.model_dump()
        return SceneContext.model_validate(payload)
