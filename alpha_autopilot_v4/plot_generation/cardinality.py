from __future__ import annotations

from ..personality.models import PersonalityProfile
from ..pressure.models import PressureProfile
from .candidate_builder import build_plot_candidate
from .models import PlotCandidate


def ensure_candidate_cardinality(
    candidates: list[PlotCandidate],
    *,
    minimum: int,
    personalities: list[PersonalityProfile],
    pressure_profile: PressureProfile,
) -> list[PlotCandidate]:
    if len(candidates) >= minimum:
        return candidates

    expanded = list(candidates)
    while len(expanded) < minimum:
        index = len(expanded) + 1
        base = expanded[0] if expanded else None
        if base is not None:
            expanded.append(
                build_plot_candidate(
                    candidate_id=f"{base.candidate_id}-alt-{index}",
                    triggering_relationships=list(base.triggering_relationships),
                    triggering_personalities=list(base.triggering_personalities),
                    triggering_pressure=base.triggering_pressure,
                    predicted_action=f"{base.predicted_action}-variant",
                    predicted_turning_point=f"{base.predicted_turning_point}-alt",
                    predicted_conflict_type=base.predicted_conflict_type,
                    predicted_payoff_type=base.predicted_payoff_type,
                    retention_score=max(0.0, base.retention_score - 0.03 * index),
                    tension_score=max(0.0, base.tension_score - 0.02 * index),
                    explanation=f"{base.explanation} Alternative branch #{index}.",
                    risk_flags=list(base.risk_flags),
                )
            )
            continue

        fallback_personalities = personalities[:2]
        expanded.append(
            build_plot_candidate(
                candidate_id=f"fallback-{index}",
                triggering_relationships=[],
                triggering_personalities=fallback_personalities,
                triggering_pressure=pressure_profile,
                predicted_action="stabilize-and-probe",
                predicted_turning_point="fallback-turn",
                predicted_conflict_type="latent-conflict",
                predicted_payoff_type="deferred-payoff",
                retention_score=0.42,
                tension_score=0.38,
                explanation="Fallback candidate generated to preserve minimum candidate cardinality.",
                risk_flags=["fallback-generated"],
            )
        )
    return expanded
