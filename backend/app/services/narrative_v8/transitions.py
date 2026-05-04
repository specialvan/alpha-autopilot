from __future__ import annotations

from .fallbacks import derive_fallback_transition
from .schemas import DecisionLayer, FlavorRender, SceneContext, TransitionLayer
from .transition_policy import build_transition_signals, derive_non_fallback_transition


def derive_transition_outcome(
    *,
    scene: SceneContext,
    decision: DecisionLayer,
    flavor: FlavorRender,
) -> TransitionLayer:
    if decision.selection_mode == "fallback":
        return derive_fallback_transition(scene=scene, decision=decision)
    return derive_non_fallback_transition(
        build_transition_signals(scene=scene, flavor=flavor)
    )
