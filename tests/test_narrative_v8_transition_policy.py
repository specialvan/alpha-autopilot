from __future__ import annotations

from backend.app.services.narrative_v8.schemas import FlavorRender, SceneContext
from backend.app.services.narrative_v8.transition_policy import (
    TRANSITION_RULE_ORDER,
    TransitionPolicyConfig,
    build_transition_signals,
    build_default_transition_policy,
    derive_non_fallback_transition,
)


def build_scene(*, current_control_state: str, observers: tuple[dict[str, object], ...]) -> SceneContext:
    return SceneContext(
        arena="chaotang",
        stake="reputation",
        observers=observers,
        power_topology=(
            {
                "source": "villain-policy",
                "target": "target-policy",
                "relation": "ritual_seniority",
                "asymmetry": 2,
            },
        ),
        relationship_distance="formal",
        visibility="public",
        time_pressure="mid",
        current_phase="pressure_test",
        current_control_state=current_control_state,
        existing_state={},
    )


def build_flavor(
    *,
    witness_posture: str,
    cost_profile: str,
    state_shift_focus: str = "narrative",
) -> FlavorRender:
    return FlavorRender(
        tone="policy-test",
        aesthetic=("法统", "冷静"),
        social_surface=("克制", "体贴"),
        private_subtext=("解释权",),
        delivery_surface="courteous_superiority",
        pressure_channel="witness_pressure",
        witness_posture=witness_posture,
        cost_profile=cost_profile,
        hook_style="public_record_seed",
        structural_targets=("external_move", "state_shift"),
        state_shift_focus=state_shift_focus,
    )


def judge_and_transmitter_observers() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "observer-judge",
            "role": "judge",
            "alignment": "unknown",
            "importance": 3,
            "visibility_impact": 3,
        },
        {
            "id": "observer-transmitter",
            "role": "transmitter",
            "alignment": "volatile",
            "importance": 2,
            "visibility_impact": 3,
        },
    )


def judge_only_observers() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "observer-judge",
            "role": "judge",
            "alignment": "unknown",
            "importance": 3,
            "visibility_impact": 3,
        },
    )


def witness_only_observers() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "observer-witness",
            "role": "witness",
            "alignment": "mixed",
            "importance": 2,
            "visibility_impact": 2,
        },
    )


def test_transition_policy_declares_explicit_rule_order() -> None:
    assert TRANSITION_RULE_ORDER == (
        "repair_attempt_restoration",
        "suspicious_upgrade",
        "public_trace_exposure",
        "distrusted_hardening",
        "steady_state",
    )


def test_transition_policy_exposes_default_threshold_table() -> None:
    policy = build_default_transition_policy()

    assert "reputation_bet" in policy.public_trace_cost_profiles
    assert "low_exposure" in policy.upgrade_window_cost_profiles
    assert "harmless" in policy.public_trace_states
    assert "suspicious" in policy.upgrade_eligible_states


def test_transition_policy_signals_can_show_upgrade_and_public_trace_at_once() -> None:
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=judge_and_transmitter_observers(),
        ),
        flavor=build_flavor(
            witness_posture="perform_for_judge",
            cost_profile="reputation_bet",
        ),
    )

    assert signals.prior_state == "suspicious"
    assert signals.public_trace_visible is True
    assert signals.upgrade_window_open is True
    assert signals.transmitter_present is True


def test_transition_policy_prioritizes_upgrade_before_public_trace() -> None:
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=judge_and_transmitter_observers(),
        ),
        flavor=build_flavor(
            witness_posture="perform_for_judge",
            cost_profile="reputation_bet",
        ),
    )

    result = derive_non_fallback_transition(signals)

    assert result.next_state == "upgraded"
    assert result.upgrade_path == "more_systemic"


def test_transition_policy_can_reach_more_hidden_upgrade_path() -> None:
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=witness_only_observers(),
        ),
        flavor=build_flavor(
            witness_posture="use_witness",
            cost_profile="low_exposure",
        ),
    )

    result = derive_non_fallback_transition(signals)

    assert signals.upgrade_window_open is True
    assert result.next_state == "upgraded"
    assert result.upgrade_path == "more_hidden"


def test_transition_policy_does_not_upgrade_judge_only_public_trace_without_witness_network() -> None:
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=judge_only_observers(),
        ),
        flavor=build_flavor(
            witness_posture="perform_for_judge",
            cost_profile="reputation_bet",
        ),
    )

    result = derive_non_fallback_transition(signals)

    assert signals.public_trace_visible is True
    assert result.next_state == "suspicious"
    assert result.upgrade_trigger is None


def test_transition_policy_does_not_upgrade_transmitter_path_without_public_trace() -> None:
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=judge_and_transmitter_observers(),
        ),
        flavor=build_flavor(
            witness_posture="seed_for_transmitter",
            cost_profile="low_exposure",
        ),
    )

    result = derive_non_fallback_transition(signals)

    assert signals.public_trace_visible is False
    assert signals.transmitter_present is True
    assert result.next_state == "suspicious"
    assert result.upgrade_trigger is None


def test_transition_policy_respects_custom_upgrade_threshold_table() -> None:
    policy = TransitionPolicyConfig(
        public_trace_cost_profiles=("reputation_bet", "high_backfire", "delayed_exposure"),
        upgrade_window_cost_profiles=("reputation_bet",),
        public_trace_states=("harmless", "more_hidden"),
        upgrade_eligible_states=("suspicious",),
    )
    signals = build_transition_signals(
        scene=build_scene(
            current_control_state="suspicious",
            observers=judge_only_observers(),
        ),
        flavor=build_flavor(
            witness_posture="use_witness",
            cost_profile="low_exposure",
        ),
        policy=policy,
    )

    result = derive_non_fallback_transition(signals, policy=policy)

    assert signals.upgrade_window_open is False
    assert result.next_state == "suspicious"
