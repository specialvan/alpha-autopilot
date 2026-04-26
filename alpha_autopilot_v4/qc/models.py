from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlotQCSummary:
    template_risk: float
    relationship_stasis_risk: float
    personality_drift_risk: float
    pressure_weakness_risk: float
    warnings: list[str]
