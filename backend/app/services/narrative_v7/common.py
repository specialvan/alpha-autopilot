from __future__ import annotations


def clamp(value: float, *, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def safe_div(numerator: float, denominator: float, *, default: float = 0.0) -> float:
    if abs(float(denominator)) < 1e-9:
        return float(default)
    return float(numerator) / float(denominator)
