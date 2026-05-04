from __future__ import annotations

from .schemas import ControlSurfaceState, FlavorRender, NarrativeV8BaseModel, SceneContext, TransitionLayer


TRANSITION_RULE_ORDER = (
    "repair_attempt_restoration",
    "suspicious_upgrade",
    "public_trace_exposure",
    "distrusted_hardening",
    "steady_state",
)


class TransitionPolicyConfig(NarrativeV8BaseModel):
    public_trace_cost_profiles: tuple[str, ...]
    upgrade_window_cost_profiles: tuple[str, ...]
    public_trace_states: tuple[ControlSurfaceState, ...]
    upgrade_eligible_states: tuple[ControlSurfaceState, ...]


class TransitionSignals(NarrativeV8BaseModel):
    prior_state: ControlSurfaceState
    public_visibility: bool
    repair_cycle_active: bool
    public_trace_visible: bool
    upgrade_window_open: bool
    transmitter_present: bool
    witness_network_present: bool
    judge_pressure: bool
    low_exposure_window: bool
    narrative_repair_focus: bool


DEFAULT_TRANSITION_POLICY = TransitionPolicyConfig(
    public_trace_cost_profiles=("reputation_bet", "high_backfire", "delayed_exposure"),
    upgrade_window_cost_profiles=("reputation_bet", "low_exposure"),
    public_trace_states=("harmless", "more_hidden"),
    upgrade_eligible_states=("suspicious",),
)


def build_default_transition_policy() -> TransitionPolicyConfig:
    return DEFAULT_TRANSITION_POLICY


def build_transition_signals(
    *,
    scene: SceneContext,
    flavor: FlavorRender,
    policy: TransitionPolicyConfig | None = None,
) -> TransitionSignals:
    resolved_policy = policy or DEFAULT_TRANSITION_POLICY
    public_visibility = scene.visibility == "public"
    judge_pressure = flavor.witness_posture == "perform_for_judge"
    public_trace_visible = public_visibility and (
        flavor.cost_profile in resolved_policy.public_trace_cost_profiles
    )
    witness_network_present = any(
        observer.role == "witness" and observer.alignment != "target" for observer in scene.observers
    )
    low_exposure_window = (
        public_visibility
        and flavor.cost_profile == "low_exposure"
        and flavor.cost_profile in resolved_policy.upgrade_window_cost_profiles
    )
    transmitter_present = any(observer.role == "transmitter" for observer in scene.observers)
    upgrade_window_open = (
        public_trace_visible and transmitter_present
    ) or (
        public_trace_visible and judge_pressure and witness_network_present
    ) or (
        low_exposure_window and not judge_pressure and not transmitter_present
    )

    return TransitionSignals(
        prior_state=scene.current_control_state,
        public_visibility=public_visibility,
        repair_cycle_active=scene.current_control_state == "repair_attempt",
        public_trace_visible=public_trace_visible,
        upgrade_window_open=upgrade_window_open,
        transmitter_present=transmitter_present,
        witness_network_present=witness_network_present,
        judge_pressure=judge_pressure,
        low_exposure_window=low_exposure_window,
        narrative_repair_focus=flavor.state_shift_focus == "narrative",
    )


def derive_non_fallback_transition(
    signals: TransitionSignals,
    *,
    policy: TransitionPolicyConfig | None = None,
) -> TransitionLayer:
    resolved_policy = policy or DEFAULT_TRANSITION_POLICY
    if signals.repair_cycle_active:
        recovery_mode = (
            "re_establish_narrative_control"
            if signals.narrative_repair_focus
            else "re_establish_decorum"
        )
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="partially_restored",
            recovery_mode=recovery_mode,
            transition_reason="a successful controlled move starts to restore room-level coherence",
        )

    if (
        signals.prior_state in resolved_policy.upgrade_eligible_states
        and signals.public_trace_visible
        and signals.transmitter_present
    ):
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="upgraded",
            upgrade_trigger="higher_order_path_found",
            upgrade_path="more_systemic",
            transition_reason="a visible public trace plus a transmitter turns the move into a reusable networked control path",
        )

    if (
        signals.prior_state in resolved_policy.upgrade_eligible_states
        and signals.public_trace_visible
        and signals.judge_pressure
        and signals.witness_network_present
    ):
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="upgraded",
            upgrade_trigger="higher_order_path_found",
            upgrade_path="outsourced_interpretation",
            transition_reason="judge pressure only becomes a higher-order path once a wider witness network can carry the room's interpretation",
        )

    if (
        signals.prior_state in resolved_policy.upgrade_eligible_states
        and signals.low_exposure_window
        and not signals.judge_pressure
        and not signals.transmitter_present
    ):
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="upgraded",
            upgrade_trigger="higher_order_path_found",
            upgrade_path="more_hidden",
            transition_reason="the room is quiet enough to convert a suspicious posture into a stealthier control path rather than forcing a public escalation",
        )

    if (
        signals.prior_state in resolved_policy.public_trace_states
        and signals.public_trace_visible
    ):
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="suspicious",
            transition_reason="public pressure creates a visible control trace even when the move lands cleanly",
        )

    if signals.prior_state == "distrusted":
        return TransitionLayer(
            prior_state=signals.prior_state,
            next_state="hardened",
            transition_reason="a clean move may preserve leverage but does not restore trust from a distrusted state",
        )

    return TransitionLayer(
        prior_state=signals.prior_state,
        next_state=signals.prior_state,
        transition_reason="the current move preserves the existing control posture without forcing a state jump",
    )
