from __future__ import annotations

from .models import PlotQCSummary
from ..plot_generation.models import PlotGenerationResult


def evaluate_plot_qc(result: PlotGenerationResult) -> PlotQCSummary:
    candidates = result.plot_candidates
    if not candidates:
        return PlotQCSummary(
            template_risk=0.8,
            relationship_stasis_risk=0.8,
            personality_drift_risk=0.8,
            pressure_weakness_risk=0.8,
            warnings=["no-candidate"],
        )

    unique_turns = {candidate.predicted_turning_point for candidate in candidates}
    template_risk = 0.5 if len(unique_turns) <= 1 else 0.2
    relationship_stasis_risk = 0.4 if all(candidate.tension_score < 0.4 for candidate in candidates) else 0.2
    personality_drift_risk = 0.3 if any(not candidate.triggering_personalities for candidate in candidates) else 0.1
    pressure_weakness_risk = 0.4 if any(candidate.triggering_pressure.intensity.total < 0.3 for candidate in candidates) else 0.1
    warnings: list[str] = []
    if template_risk >= 0.35:
        warnings.append("template-risk")
    if relationship_stasis_risk >= 0.3:
        warnings.append("relationship-stasis")
    if personality_drift_risk >= 0.25:
        warnings.append("personality-drift")
    if pressure_weakness_risk >= 0.25:
        warnings.append("pressure-weakness")
    return PlotQCSummary(
        template_risk=template_risk,
        relationship_stasis_risk=relationship_stasis_risk,
        personality_drift_risk=personality_drift_risk,
        pressure_weakness_risk=pressure_weakness_risk,
        warnings=warnings,
    )
