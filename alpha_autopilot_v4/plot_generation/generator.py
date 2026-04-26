from __future__ import annotations

from ..personality.analyzer import analyze_personalities
from ..pressure.analyzer import analyze_pressure
from ..relations.analyzer import analyze_relationships
from .candidate_builder import build_plot_candidate
from .candidate_ranker import apply_retention_feedback_writeback, rank_plot_candidates
from .cardinality import ensure_candidate_cardinality
from .models import PlotGenerationResult


def _score_candidate(tension: float, pressure: float, risk: float, relation: float) -> tuple[float, float]:
    retention_score = max(
        0.0,
        min(1.0, round(0.35 * tension + 0.3 * pressure + 0.2 * relation - 0.1 * risk, 4)),
    )
    tension_score = max(
        0.0,
        min(1.0, round(0.5 * tension + 0.3 * relation + 0.2 * pressure, 4)),
    )
    return retention_score, tension_score


def _conflict_type(status_gap: float, info_gap: float, emotion_gap: float) -> str:
    if status_gap >= info_gap and status_gap >= emotion_gap:
        return "status-clash"
    if info_gap >= emotion_gap:
        return "information-reveal"
    return "emotion-laceration"


def _base_action_and_turn(pressure_total: float, survival_pressure: float, relation_break_pressure: float) -> tuple[str, str, str]:
    if survival_pressure >= 0.6:
        return "survive-first", "forced-choice-under-pressure", "survival-breakthrough"
    if relation_break_pressure >= 0.5:
        return "break-the-balance", "relationship-shift", "relationship-reversal"
    if pressure_total >= 0.5:
        return "test-and-counter", "pressure-driven-turn", "pressure-reveal"
    return "evaluate-and-act", "preference-driven-turn", "choice-reveal"


def _resolve_genre_profile(context: dict[str, object]) -> dict[str, object] | None:
    profile = context.get("genre_profile")
    if isinstance(profile, dict):
        return profile
    genre = context.get("genre")
    if isinstance(genre, str) and genre.strip():
        return {"genre": genre.strip()}
    return None


def generate_plot_candidates(context: dict[str, object]) -> PlotGenerationResult:
    characters = context.get("characters", [])
    if not isinstance(characters, list):
        characters = []
    characters = [item for item in characters if isinstance(item, dict)]
    v3_retention_context = context.get("v3_retention_context", {})
    if not isinstance(v3_retention_context, dict):
        v3_retention_context = {}
    feedback_history = context.get("v3_feedback_history", [])
    if isinstance(feedback_history, list):
        v3_retention_context = {**v3_retention_context, "retention_feedback_history": feedback_history}
    adjusted_retention_context = apply_retention_feedback_writeback(v3_retention_context)

    relation_history = context.get("relationship_history", [])
    relation_result = analyze_relationships(
        characters,
        history=relation_history if isinstance(relation_history, list) else None,
        chapter_index=_safe_int(context.get("chapter_index")),
    )
    pressure_profile = analyze_pressure(context)
    personalities = analyze_personalities(
        characters,
        genre_profile=_resolve_genre_profile(context),
    )

    candidates: list = []
    relation_profiles = relation_result.profiles[:3] if relation_result.profiles else [None]
    for index, relation_profile in enumerate(relation_profiles):
        primary_personality = personalities[index % len(personalities)] if personalities else None
        secondary_personality = (
            personalities[(index + 1) % len(personalities)]
            if len(personalities) > 1
            else primary_personality
        )
        triggering_personalities = [item for item in [primary_personality, secondary_personality] if item is not None]
        risk_level = (
            sum(item.action_preference.risk_level for item in triggering_personalities)
            / len(triggering_personalities)
            if triggering_personalities
            else 0.5
        )

        if relation_profile is None:
            relation_tension = relation_result.aggregate_tension
            relation_velocity = relation_result.aggregate_tension
            conflict_type = "latent-conflict"
            relation_payload: list = []
        else:
            relation_tension = relation_profile.tension_score
            relation_velocity = relation_profile.relationship_velocity
            conflict_type = _conflict_type(
                relation_profile.delta.status_gap,
                relation_profile.delta.info_gap,
                relation_profile.delta.emotion_gap,
            )
            relation_payload = [relation_profile]

        retention_score, tension_score = _score_candidate(
            relation_tension,
            pressure_profile.intensity.total,
            risk_level,
            relation_velocity,
        )
        predicted_action, predicted_turning_point, predicted_payoff_type = _base_action_and_turn(
            pressure_profile.intensity.total,
            pressure_profile.intensity.survival_pressure,
            pressure_profile.intensity.relationship_break_pressure,
        )
        if triggering_personalities and pressure_profile.intensity.total < 0.5:
            predicted_action = triggering_personalities[0].action_preference.pressure_response

        risk_flags: list[str] = []
        if tension_score < 0.35:
            risk_flags.append("weak-tension")
        if retention_score < 0.4:
            risk_flags.append("weak-retention")
        if pressure_profile.intensity.total < 0.3:
            risk_flags.append("weak-pressure")
        if len(relation_payload) == 0:
            risk_flags.append("relation-sparse")

        candidates.append(
            build_plot_candidate(
                candidate_id=f"candidate-{index + 1}",
                triggering_relationships=relation_payload,
                triggering_personalities=triggering_personalities,
                triggering_pressure=pressure_profile,
                predicted_action=predicted_action,
                predicted_turning_point=predicted_turning_point,
                predicted_conflict_type=conflict_type,
                predicted_payoff_type=predicted_payoff_type,
                retention_score=retention_score,
                tension_score=tension_score,
                explanation=(
                    f"Relationship tension {relation_tension} and pressure {pressure_profile.intensity.total} "
                    f"drive {conflict_type} with action {predicted_action}."
                ),
                risk_flags=risk_flags,
            )
        )

    candidates = ensure_candidate_cardinality(
        candidates,
        minimum=2,
        personalities=personalities,
        pressure_profile=pressure_profile,
    )
    ranked_candidates = rank_plot_candidates(candidates, retention_context=adjusted_retention_context)
    selected_candidate = ranked_candidates[0] if ranked_candidates else None
    return PlotGenerationResult(
        source_context=context,
        plot_candidates=ranked_candidates,
        selected_candidate=selected_candidate,
        selection_reason="v3-retention-ranked" if selected_candidate else "no-candidate",
        generation_notes=(
            f"Generated {len(ranked_candidates)} candidates from {len(relation_result.profiles)} relation pairs."
        ),
        retention_context_used=adjusted_retention_context,
        relationship_graph=relation_result.relationship_graph,
        relationship_displacements=relation_result.displacement_events,
    )


def _safe_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None
