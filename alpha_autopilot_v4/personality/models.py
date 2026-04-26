from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionBias:
    impulsiveness: float
    calmness: float
    resilience: float
    directness: float
    pragmatism: float
    idealism: float
    assertiveness: float
    avoidance: float
    self_protection: float
    sacrifice_tendency: float
    risk_appetite: float


@dataclass(frozen=True)
class ActionPreference:
    pressure_response: str
    preferred_moves: list[str]
    risk_level: float


@dataclass(frozen=True)
class PersonalityProfile:
    character_id: str
    bias: DecisionBias
    action_preference: ActionPreference
    genre_calibration: str | None = None
