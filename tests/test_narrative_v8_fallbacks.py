from __future__ import annotations

from backend.app.services.narrative_v8.fallbacks import (
    build_fallback_decision,
    choose_fallback_action,
    derive_fallback_transition,
)
from backend.app.services.narrative_v8.schemas import RejectedKnifeReason, SceneContext


def build_scene(*, visibility: str, current_control_state: str) -> SceneContext:
    observers = (
        {
            "id": "observer-judge",
            "role": "judge",
            "alignment": "unknown",
            "importance": 3,
            "visibility_impact": 3,
        },
    ) if visibility == "public" else ()
    return SceneContext(
        arena="chaotang" if visibility == "public" else "qingzhai",
        stake="reputation" if visibility == "public" else "bond",
        observers=observers,
        power_topology=(
            {
                "source": "villain-fallback-helper",
                "target": "target-fallback-helper",
                "relation": "narrative_pressure",
                "asymmetry": 2,
            },
        ),
        relationship_distance="formal" if visibility == "public" else "personal",
        visibility=visibility,
        time_pressure="mid",
        current_phase="pressure_test",
        current_control_state=current_control_state,
        existing_state={},
    )


def build_rejection() -> RejectedKnifeReason:
    return RejectedKnifeReason(
        knife_id="courteous_humiliation",
        category="observer_requirement_missing",
        detail="judge observer required",
    )


def test_fallback_helper_uses_public_mask_for_public_suspicion() -> None:
    scene = build_scene(visibility="public", current_control_state="suspicious")

    assert choose_fallback_action(scene) == "defer_to_public_mask"


def test_fallback_helper_uses_hold_position_for_private_suspicion() -> None:
    scene = build_scene(visibility="private", current_control_state="suspicious")

    assert choose_fallback_action(scene) == "hold_position"


def test_fallback_helper_uses_reduce_exposure_for_public_distrust() -> None:
    scene = build_scene(visibility="public", current_control_state="distrusted")

    assert choose_fallback_action(scene) == "reduce_exposure"


def test_fallback_helper_builds_structured_decision_and_transition_from_shared_policy() -> None:
    scene = build_scene(visibility="public", current_control_state="suspicious")
    decision = build_fallback_decision(
        scene=scene,
        rejected_knives=(build_rejection(),),
        fallback_reason="no public knife survived hard filters",
    )
    transition = derive_fallback_transition(scene=scene, decision=decision)

    assert decision.selection_mode == "fallback"
    assert decision.fallback_action == "defer_to_public_mask"
    assert decision.selected_signals == ()
    assert transition.next_state == "repair_attempt"
    assert transition.recovery_mode == "retreat_to_safer_role"
    assert transition.failure_mode == "narrative_lost"
