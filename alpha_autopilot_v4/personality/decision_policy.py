from __future__ import annotations

from .models import ActionPreference, DecisionBias, PersonalityProfile


def _to_float(value: object, default: float = 0.5) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _genre_delta(genre: str) -> dict[str, float]:
    normalized = genre.strip().lower()
    if normalized in {"power_fantasy", "wuxia", "xianxia", "cultivation"}:
        return {
            "directness": 0.08,
            "assertiveness": 0.08,
            "risk_appetite": 0.06,
            "avoidance": -0.06,
        }
    if normalized in {"mystery", "detective"}:
        return {
            "calmness": 0.08,
            "pragmatism": 0.06,
            "impulsiveness": -0.06,
        }
    if normalized in {"romance", "drama"}:
        return {
            "sacrifice_tendency": 0.08,
            "self_protection": -0.05,
            "directness": -0.04,
        }
    if normalized in {"thriller", "survival"}:
        return {
            "risk_appetite": 0.1,
            "resilience": 0.05,
            "calmness": -0.05,
        }
    return {}


def _genre_bias_overrides(genre_profile: dict[str, object]) -> dict[str, float]:
    overrides: dict[str, float] = {}
    for raw_key, raw_value in genre_profile.items():
        if not isinstance(raw_key, str) or not raw_key.endswith("_bias"):
            continue
        try:
            number = float(raw_value)  # type: ignore[arg-type]
        except Exception:
            continue
        field_name = raw_key[:-5]
        overrides[field_name] = number
    return overrides


def _apply_genre_calibration(
    *,
    bias: DecisionBias,
    genre_profile: dict[str, object] | None,
) -> tuple[DecisionBias, str | None]:
    if not isinstance(genre_profile, dict):
        return bias, None

    genre = str(genre_profile.get("genre", "")).strip()
    if not genre:
        return bias, None

    deltas = _genre_delta(genre)
    deltas.update(_genre_bias_overrides(genre_profile))

    return DecisionBias(
        impulsiveness=_clip01(bias.impulsiveness + deltas.get("impulsiveness", 0.0)),
        calmness=_clip01(bias.calmness + deltas.get("calmness", 0.0)),
        resilience=_clip01(bias.resilience + deltas.get("resilience", 0.0)),
        directness=_clip01(bias.directness + deltas.get("directness", 0.0)),
        pragmatism=_clip01(bias.pragmatism + deltas.get("pragmatism", 0.0)),
        idealism=_clip01(bias.idealism + deltas.get("idealism", 0.0)),
        assertiveness=_clip01(bias.assertiveness + deltas.get("assertiveness", 0.0)),
        avoidance=_clip01(bias.avoidance + deltas.get("avoidance", 0.0)),
        self_protection=_clip01(bias.self_protection + deltas.get("self_protection", 0.0)),
        sacrifice_tendency=_clip01(
            bias.sacrifice_tendency + deltas.get("sacrifice_tendency", 0.0)
        ),
        risk_appetite=_clip01(bias.risk_appetite + deltas.get("risk_appetite", 0.0)),
    ), genre.lower()


def analyze_personality(
    character: dict[str, object],
    genre_profile: dict[str, object] | None = None,
) -> PersonalityProfile:
    bias = DecisionBias(
        impulsiveness=_clip01(_to_float(character.get("impulsiveness"))),
        calmness=_clip01(_to_float(character.get("calmness"))),
        resilience=_clip01(_to_float(character.get("resilience"))),
        directness=_clip01(_to_float(character.get("directness"))),
        pragmatism=_clip01(_to_float(character.get("pragmatism"))),
        idealism=_clip01(_to_float(character.get("idealism"))),
        assertiveness=_clip01(_to_float(character.get("assertiveness"))),
        avoidance=_clip01(_to_float(character.get("avoidance"))),
        self_protection=_clip01(_to_float(character.get("self_protection"))),
        sacrifice_tendency=_clip01(_to_float(character.get("sacrifice_tendency"))),
        risk_appetite=_clip01(_to_float(character.get("risk_appetite"))),
    )
    calibrated_bias, genre_calibration = _apply_genre_calibration(
        bias=bias,
        genre_profile=genre_profile,
    )
    bias = calibrated_bias
    if bias.pragmatism >= bias.idealism:
        pressure_response = "calculate-and-counter"
        preferred_moves = ["set-trap", "use-leverage", "counter-attack"]
    elif bias.self_protection >= bias.sacrifice_tendency:
        pressure_response = "protect-and-withhold"
        preferred_moves = ["withdraw", "hide-weakness", "wait-for-opportunity"]
    elif bias.impulsiveness >= 0.7:
        pressure_response = "react-first"
        preferred_moves = ["explode", "hit-back", "escalate"]
    else:
        pressure_response = "balance-and-choose"
        preferred_moves = ["test-boundary", "delay-reveal", "seek-advantage"]

    action_preference = ActionPreference(
        pressure_response=pressure_response,
        preferred_moves=preferred_moves,
        risk_level=_clip01((bias.risk_appetite + bias.impulsiveness) / 2),
    )
    return PersonalityProfile(
        character_id=str(character.get("id", "")),
        bias=bias,
        action_preference=action_preference,
        genre_calibration=genre_calibration,
    )
