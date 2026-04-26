from __future__ import annotations


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def average_pair(left: float, right: float) -> float:
    return clamp01((left + right) / 2)


def relationship_tension(
    *,
    status_gap: float,
    info_gap: float,
    emotion_gap: float,
    interest_conflict: float,
    control_dependency: float,
    betrayal_risk: float,
) -> float:
    return clamp01(
        0.22 * status_gap
        + 0.22 * info_gap
        + 0.18 * emotion_gap
        + 0.16 * interest_conflict
        + 0.12 * control_dependency
        + 0.1 * betrayal_risk
    )
