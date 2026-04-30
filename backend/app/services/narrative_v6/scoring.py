from __future__ import annotations

from typing import Any


DEFAULT_RETENTION_VECTOR: dict[str, float] = {
    "hook_strength": 0.32,
    "suspense": 0.24,
    "relationship_tension": 0.24,
    "coherence": 0.2,
}

_V5_DESIRE_KEYS: tuple[str, ...] = (
    "primal_desire",
    "value_recognition",
    "knowledge_curiosity",
    "information_gap",
)

_V5_TO_V6_WEIGHT_PROFILES: dict[str, dict[str, float]] = {
    "primal_desire": {
        "hook_strength": 0.1,
        "suspense": 0.3,
        "relationship_tension": 0.5,
        "coherence": 0.1,
    },
    "value_recognition": {
        "hook_strength": 0.15,
        "suspense": 0.1,
        "relationship_tension": 0.4,
        "coherence": 0.35,
    },
    "knowledge_curiosity": {
        "hook_strength": 0.4,
        "suspense": 0.25,
        "relationship_tension": 0.05,
        "coherence": 0.3,
    },
    "information_gap": {
        "hook_strength": 0.3,
        "suspense": 0.55,
        "relationship_tension": 0.05,
        "coherence": 0.1,
    },
}

_DOMINANT_BOOST = 1.2


def score_simulation_path(
    *,
    strategy: str,
    plot_outline: list[str],
    relationship_deltas: list[dict[str, Any]],
    consistency_issues: list[str],
    risk_flags: list[str],
    retention_desire_vector: dict[str, Any] | None = None,
) -> tuple[float, dict[str, float]]:
    weights = _resolve_weights(retention_desire_vector)

    hook_strength = min(1.0, 0.25 + len(plot_outline) / 8.0)
    suspense = _strategy_suspense(strategy)
    relationship_tension = min(1.0, 0.2 + len(relationship_deltas) / 5.0)
    coherence = max(0.0, 1.0 - min(0.8, len(consistency_issues) * 0.25))
    risk_penalty = min(0.6, len(risk_flags) * 0.12)

    weighted_score = (
        hook_strength * weights["hook_strength"]
        + suspense * weights["suspense"]
        + relationship_tension * weights["relationship_tension"]
        + coherence * weights["coherence"]
    )
    final_score = max(0.0, min(1.0, weighted_score - risk_penalty))

    breakdown = {
        "hook_strength": round(hook_strength, 4),
        "suspense": round(suspense, 4),
        "relationship_tension": round(relationship_tension, 4),
        "coherence": round(coherence, 4),
        "risk_penalty": round(risk_penalty, 4),
        "weighted_score": round(weighted_score, 4),
        "final_score": round(final_score, 4),
    }
    return round(final_score, 4), breakdown


def normalize_retention_vector_weights(custom_weights: dict[str, Any] | None) -> dict[str, float]:
    weights = dict(DEFAULT_RETENTION_VECTOR)
    if not custom_weights:
        return weights

    mapped_weights = _map_v5_desire_vector_to_v6(custom_weights)
    if mapped_weights is not None:
        weights.update(mapped_weights)

    for key in DEFAULT_RETENTION_VECTOR:
        raw = _to_float(custom_weights.get(key))
        if raw is None:
            continue
        weights[key] = max(0.0, raw)

    total = sum(weights.values())
    if total <= 0:
        return dict(DEFAULT_RETENTION_VECTOR)
    return {key: value / total for key, value in weights.items()}


def _resolve_weights(custom_weights: dict[str, Any] | None) -> dict[str, float]:
    return normalize_retention_vector_weights(custom_weights)


def _map_v5_desire_vector_to_v6(custom_weights: dict[str, Any]) -> dict[str, float] | None:
    desire_weights: dict[str, float] = {}
    for key in _V5_DESIRE_KEYS:
        raw = _to_float(custom_weights.get(key))
        if raw is None:
            continue
        desire_weights[key] = max(0.0, raw)

    if not desire_weights:
        return None

    dominant = _resolve_dominant(custom_weights)
    if dominant in desire_weights:
        desire_weights[dominant] = desire_weights[dominant] * _DOMINANT_BOOST

    total_desire = sum(desire_weights.values())
    if total_desire <= 0:
        return None

    normalized_desires = {
        key: value / total_desire
        for key, value in desire_weights.items()
    }
    mapped = {
        "hook_strength": 0.0,
        "suspense": 0.0,
        "relationship_tension": 0.0,
        "coherence": 0.0,
    }
    for desire_key, desire_weight in normalized_desires.items():
        profile = _V5_TO_V6_WEIGHT_PROFILES.get(desire_key)
        if profile is None:
            continue
        for target_key, target_ratio in profile.items():
            mapped[target_key] += desire_weight * target_ratio
    return mapped


def _resolve_dominant(custom_weights: dict[str, Any]) -> str | None:
    for key in ("dominant_override", "dominant"):
        raw = custom_weights.get(key)
        if not isinstance(raw, str):
            continue
        normalized = raw.strip().lower()
        if normalized in _V5_DESIRE_KEYS:
            return normalized
    return None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return None


def _strategy_suspense(strategy: str) -> float:
    mapping = {
        "retention_first": 0.74,
        "suspense_first": 0.91,
        "relationship_burst": 0.78,
        "balanced": 0.7,
    }
    return mapping.get(strategy, 0.68)
