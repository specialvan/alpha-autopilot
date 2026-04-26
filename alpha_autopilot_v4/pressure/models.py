from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PressureSource:
    pressure_type: str
    intensity: float


@dataclass(frozen=True)
class PressureIntensity:
    total: float
    survival_pressure: float
    relationship_break_pressure: float


@dataclass(frozen=True)
class PressureProfile:
    sources: list[PressureSource]
    intensity: PressureIntensity
