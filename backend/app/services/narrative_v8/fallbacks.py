from __future__ import annotations

from .schemas import DecisionLayer, RejectedKnifeReason, SceneContext, TransitionLayer


REPAIR_OR_RECOVERY_STATES = {"suspicious", "repair_attempt", "partially_restored"}


def choose_fallback_action(scene: SceneContext) -> str:
    if scene.visibility == "public":
        if scene.current_control_state == "distrusted":
            return "reduce_exposure"
        return "defer_to_public_mask"

    if scene.current_control_state in REPAIR_OR_RECOVERY_STATES:
        return "hold_position"
    return "gather_information"


def build_fallback_decision(
    *,
    scene: SceneContext,
    rejected_knives: tuple[RejectedKnifeReason, ...],
    fallback_reason: str,
) -> DecisionLayer:
    return DecisionLayer(
        selection_mode="fallback",
        fallback_action=choose_fallback_action(scene),
        fallback_reason=fallback_reason,
        selected_signals=(),
        rejected_knives=rejected_knives,
    )


def derive_fallback_transition(*, scene: SceneContext, decision: DecisionLayer) -> TransitionLayer:
    prior_state = scene.current_control_state

    if prior_state == "distrusted" and scene.visibility == "public":
        return TransitionLayer(
            prior_state=prior_state,
            next_state="collapsed",
            failure_mode="shell_exposed",
            transition_reason="a public fallback from a distrusted state leaves no safe legitimacy shell to hide behind",
        )

    fallback_action = decision.fallback_action or choose_fallback_action(scene)
    recovery_mode = _fallback_recovery_mode(fallback_action)
    failure_mode = (
        "narrative_lost" if fallback_action == "defer_to_public_mask" else "pace_lost"
    )

    if prior_state in REPAIR_OR_RECOVERY_STATES:
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
        transition_reason=decision.fallback_reason
        or "the current room does not support a stable knife, so control shifts into recovery posture",
    )


def _fallback_recovery_mode(action: str) -> str:
    mapping = {
        "reduce_exposure": "lower_intensity",
        "defer_to_public_mask": "retreat_to_safer_role",
        "hold_position": "re_establish_decorum",
        "gather_information": "change_scene",
    }
    return mapping.get(action, "change_scene")
