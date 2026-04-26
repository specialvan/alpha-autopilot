from __future__ import annotations

from .pressure_index import compute_pressure_index
from .models import PressureIntensity, PressureProfile, PressureSource


def analyze_pressure(context: dict[str, object]) -> PressureProfile:
    sources: list[PressureSource] = []

    pressure_items = context.get("pressure_items", [])
    if isinstance(pressure_items, list):
        for item in pressure_items:
            if not isinstance(item, dict):
                continue
            pressure_type = str(item.get("type", "unknown"))
            intensity = max(0.0, min(1.0, float(item.get("intensity", 0.0))))
            sources.append(PressureSource(pressure_type=pressure_type, intensity=intensity))
    intensity = compute_pressure_index(sources)

    return PressureProfile(
        sources=sources,
        intensity=PressureIntensity(
            total=intensity.total,
            survival_pressure=intensity.survival_pressure,
            relationship_break_pressure=intensity.relationship_break_pressure,
        ),
    )
