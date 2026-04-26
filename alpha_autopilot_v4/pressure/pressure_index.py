from __future__ import annotations

from .models import PressureIntensity, PressureSource


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def compute_pressure_index(sources: list[PressureSource]) -> PressureIntensity:
    if not sources:
        return PressureIntensity(total=0.0, survival_pressure=0.0, relationship_break_pressure=0.0)

    total = sum(item.intensity for item in sources) / len(sources)
    survival_pressure = (
        sum(item.intensity for item in sources if item.pressure_type in {"survival", "resource_scarcity", "death"})
        / len(sources)
    )
    relationship_break_pressure = (
        sum(
            item.intensity
            for item in sources
            if item.pressure_type in {"betrayal", "humiliation", "conflict", "relationship_break"}
        )
        / len(sources)
    )
    return PressureIntensity(
        total=_clip01(total),
        survival_pressure=_clip01(survival_pressure),
        relationship_break_pressure=_clip01(relationship_break_pressure),
    )
