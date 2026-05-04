from __future__ import annotations

from .schemas import DecisionLayer, FlavorRender, SceneContext, TransitionLayer


def derive_transition_outcome(
    *,
    scene: SceneContext,
    decision: DecisionLayer,
    flavor: FlavorRender,
) -> TransitionLayer:
    prior_state = scene.current_control_state

    if decision.selection_mode == "fallback":
        return _derive_fallback_transition(scene=scene, decision=decision)

    if prior_state == "repair_attempt":
        recovery_mode = (
            "re_establish_narrative_control"
            if flavor.state_shift_focus == "narrative"
            else "re_establish_decorum"
        )
        return TransitionLayer(
            prior_state=prior_state,
            next_state="partially_restored",
            recovery_mode=recovery_mode,
            transition_reason="a successful controlled move starts to restore room-level coherence",
        )

    if prior_state == "suspicious" and _has_upgrade_window(scene=scene, flavor=flavor):
        return TransitionLayer(
            prior_state=prior_state,
            next_state="upgraded",
            upgrade_trigger="higher_order_path_found",
            upgrade_path=_select_upgrade_path(scene=scene, flavor=flavor),
            transition_reason="the room now supports a higher-order control path rather than a one-off primitive",
        )

    if prior_state in {"harmless", "more_hidden"} and _creates_public_trace(scene=scene, flavor=flavor):
        return TransitionLayer(
            prior_state=prior_state,
            next_state="suspicious",
            transition_reason="public pressure creates a visible control trace even when the move lands cleanly",
        )

    if prior_state == "distrusted":
        return TransitionLayer(
            prior_state=prior_state,
            next_state="hardened",
            transition_reason="a clean move may preserve leverage but does not restore trust from a distrusted state",
        )

    return TransitionLayer(
        prior_state=prior_state,
        next_state=prior_state,
        transition_reason="the current move preserves the existing control posture without forcing a state jump",
    )


def _derive_fallback_transition(*, scene: SceneContext, decision: DecisionLayer) -> TransitionLayer:
    prior_state = scene.current_control_state

    if prior_state == "distrusted" and scene.visibility == "public":
        return TransitionLayer(
            prior_state=prior_state,
            next_state="collapsed",
            failure_mode="shell_exposed",
            transition_reason="a public fallback from a distrusted state leaves no safe legitimacy shell to hide behind",
        )

    recovery_mode = _fallback_recovery_mode(decision.fallback_action)
    failure_mode = "narrative_lost" if decision.fallback_action == "defer_to_public_mask" else "pace_lost"

    if prior_state in {"suspicious", "repair_attempt", "partially_restored"}:
        next_state = "repair_attempt"
    elif scene.visibility == "public":
        next_state = "suspicious"
    else:
        next_state = prior_state

    return TransitionLayer(
        prior_state=prior_state,
        next_state=next_state,
        failure_mode=failure_mode,
        recovery_mode=recovery_mode,
        transition_reason=decision.fallback_reason or "the current room does not support a stable knife, so control shifts into recovery posture",
    )


def _fallback_recovery_mode(action: str | None) -> str:
    mapping = {
        "reduce_exposure": "lower_intensity",
        "defer_to_public_mask": "retreat_to_safer_role",
        "hold_position": "re_establish_decorum",
        "gather_information": "change_scene",
    }
    return mapping.get(action or "gather_information", "change_scene")


def _has_upgrade_window(*, scene: SceneContext, flavor: FlavorRender) -> bool:
    return scene.visibility == "public" and (
        flavor.cost_profile == "reputation_bet" or flavor.witness_posture == "perform_for_judge"
    )


def _creates_public_trace(*, scene: SceneContext, flavor: FlavorRender) -> bool:
    return scene.visibility == "public" and flavor.cost_profile in {
        "reputation_bet",
        "high_backfire",
        "delayed_exposure",
    }


def _select_upgrade_path(*, scene: SceneContext, flavor: FlavorRender) -> str:
    if any(observer.role == "transmitter" for observer in scene.observers):
        return "more_systemic"
    if flavor.witness_posture == "perform_for_judge":
        return "outsourced_interpretation"
    if flavor.cost_profile == "low_exposure":
        return "more_hidden"
    return "more_complex"
