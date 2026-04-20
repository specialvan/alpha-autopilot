from __future__ import annotations

from alpha_autopilot import FeatureMatrix, preview_recommendations

from .schemas import PreviewRequest
from .state_builder import base_state


def build_preview(payload: PreviewRequest):
    state = base_state()
    tuning = [weight.model_dump() for weight in payload.tuningWeights]
    recommendations = preview_recommendations(state, tuning, FeatureMatrix())
    return {"recommendations": recommendations}
