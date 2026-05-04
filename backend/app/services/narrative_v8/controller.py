from __future__ import annotations

from .flavor import (
    build_explanation,
    build_future_hooks,
    build_risk_if_exposed,
    render_flavor,
)
from .knife_library import build_compatibility_graph, build_default_knife_library, get_knife_by_id
from .ledger import apply_state_shift, build_state_shift
from .schemas import BuildVillainFeedbackInput, BuildVillainFeedbackOutput, VillainFeedbackPacket
from .selection import select_knives
from .transitions import derive_transition_outcome


def build_villain_feedback(
    payload: BuildVillainFeedbackInput | dict[str, object],
) -> BuildVillainFeedbackOutput:
    request = (
        payload
        if isinstance(payload, BuildVillainFeedbackInput)
        else BuildVillainFeedbackInput.model_validate(payload)
    )
    library = request.knife_library or build_default_knife_library()
    compatibility_graph = build_compatibility_graph()

    selection_result = select_knives(
        request.villain,
        request.target,
        request.scene,
        library=library,
        compatibility_graph=compatibility_graph,
    )

    reference_knife_id = selection_result.decision.primary_knife_id or request.villain.preferred_knives[0]
    reference_knife = get_knife_by_id(reference_knife_id, library=library)
    flavor = render_flavor(request.villain, reference_knife, request.scene)

    if selection_result.decision.selection_mode == "fallback":
        future_hooks = ()
    else:
        future_hooks = build_future_hooks(
            knife=reference_knife,
            flavor=flavor,
            villain=request.villain,
            scene=request.scene,
        )

    state_shift = build_state_shift(
        flavor=flavor,
        future_hooks=future_hooks,
    )
    explanation = build_explanation(
        decision=selection_result.decision,
        knife=reference_knife,
        flavor=flavor,
        villain=request.villain,
        scene=request.scene,
    )
    transition = derive_transition_outcome(
        scene=request.scene,
        decision=selection_result.decision,
        flavor=flavor,
    )
    risk_if_exposed = build_risk_if_exposed(reference_knife, flavor)
    next_snapshot = apply_state_shift(request.scene.existing_state, state_shift)

    packet = VillainFeedbackPacket(
        villain_id=request.villain.id,
        target_id=request.target.id,
        scene_arena=request.scene.arena,
        decision=selection_result.decision,
        explanation=explanation,
        transition=transition,
        state_shift=state_shift,
        future_hooks=future_hooks,
        risk_if_exposed=risk_if_exposed,
        flavor_render=flavor,
    )
    return BuildVillainFeedbackOutput(
        packet=packet,
        next_snapshot=next_snapshot,
        next_control_state=transition.next_state,
    )
