from __future__ import annotations

from ..personality.models import PersonalityProfile
from ..pressure.models import PressureProfile
from ..relations.models import RelationshipProfile
from .models import PlotCandidate


def build_plot_candidate(
    *,
    candidate_id: str,
    triggering_relationships: list[RelationshipProfile],
    triggering_personalities: list[PersonalityProfile],
    triggering_pressure: PressureProfile,
    predicted_action: str,
    predicted_turning_point: str,
    predicted_conflict_type: str,
    predicted_payoff_type: str,
    retention_score: float,
    tension_score: float,
    explanation: str,
    risk_flags: list[str] | None = None,
) -> PlotCandidate:
    return PlotCandidate(
        candidate_id=candidate_id,
        triggering_relationships=triggering_relationships,
        triggering_personalities=triggering_personalities,
        triggering_pressure=triggering_pressure,
        predicted_action=predicted_action,
        predicted_turning_point=predicted_turning_point,
        predicted_conflict_type=predicted_conflict_type,
        predicted_payoff_type=predicted_payoff_type,
        retention_score=max(0.0, min(1.0, round(retention_score, 4))),
        tension_score=max(0.0, min(1.0, round(tension_score, 4))),
        explanation=explanation,
        risk_flags=list(risk_flags or []),
    )
