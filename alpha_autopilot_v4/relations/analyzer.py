from __future__ import annotations

from .models import (
    CharacterFunctionType,
    RelationshipDelta,
    RelationshipDisplacementEvent,
    RelationshipGraphSummary,
    RelationshipProfile,
    RelationshipTensionResult,
)
from .scoring import average_pair, clamp01, relationship_tension


def _to_float(value: object, default: float = 0.5) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _to_int(value: object, default: int | None = None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _pair_key(source_character: str, target_character: str) -> tuple[str, str]:
    return tuple(sorted((source_character, target_character)))


def _dominant_gap(status_gap: float, info_gap: float, emotion_gap: float) -> str:
    return max(
        (
            ("status", status_gap),
            ("info", info_gap),
            ("emotion", emotion_gap),
        ),
        key=lambda item: item[1],
    )[0]


def _history_index(history: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    indexed: dict[tuple[str, str], dict[str, object]] = {}
    for item in history:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source_character", ""))
        target = str(item.get("target_character", ""))
        if not source or not target:
            continue
        indexed[_pair_key(source, target)] = item
    return indexed


def _normalized_function_type(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    return normalized


def _relation_hint(
    source: dict[str, object],
    target: dict[str, object],
    *,
    reveal_disguise: bool,
) -> tuple[str, str]:
    source_function = _normalized_function_type(source.get("function_type"))
    target_function = _normalized_function_type(target.get("function_type"))
    is_disguise = source_function == CharacterFunctionType.DISGUISE.value or (
        target_function == CharacterFunctionType.DISGUISE.value
    )

    if not is_disguise:
        relation = source.get("relation") or target.get("relation") or "unknown"
        return "surface", str(relation)

    layer = "actual" if reveal_disguise else "surface"
    key = f"{layer}_relation"
    relation = (
        source.get(key)
        or target.get(key)
        or source.get("surface_relation")
        or target.get("surface_relation")
        or "unknown"
    )
    return layer, str(relation)


def analyze_relationships(
    characters: list[dict[str, object]],
    *,
    history: list[dict[str, object]] | None = None,
    chapter_index: int | None = None,
    reveal_disguise: bool = False,
) -> RelationshipTensionResult:
    profiles: list[RelationshipProfile] = []
    displacement_events: list[RelationshipDisplacementEvent] = []
    dominant_gap = "status"
    max_tension = 0.0
    history_map = _history_index(history or [])

    for index, source in enumerate(characters):
        for target in characters[index + 1 :]:
            source_character = str(source.get("id", ""))
            target_character = str(target.get("id", ""))
            relation_layer, relation_hint = _relation_hint(
                source,
                target,
                reveal_disguise=reveal_disguise,
            )
            status_gap = clamp01(abs(_to_float(source.get("status")) - _to_float(target.get("status"))))
            info_gap = clamp01(abs(_to_float(source.get("knowledge")) - _to_float(target.get("knowledge"))))
            emotion_gap = clamp01(abs(_to_float(source.get("emotion")) - _to_float(target.get("emotion"))))
            current_dominant_gap = _dominant_gap(status_gap, info_gap, emotion_gap)
            interest_conflict = average_pair(
                _to_float(source.get("interest_conflict"), default=0.0),
                _to_float(target.get("interest_conflict"), default=0.0),
            )
            control_dependency = clamp01(
                _to_float(source.get("control")) * _to_float(target.get("dependency"))
            )
            trust_state = clamp01(
                1.0 - abs(_to_float(source.get("trust")) - _to_float(target.get("trust")))
            )
            betrayal_risk = clamp01((1.0 - trust_state) * 0.7 + interest_conflict * 0.3)
            tension_score = relationship_tension(
                status_gap=status_gap,
                info_gap=info_gap,
                emotion_gap=emotion_gap,
                interest_conflict=interest_conflict,
                control_dependency=control_dependency,
                betrayal_risk=betrayal_risk,
            )
            profiles.append(
                RelationshipProfile(
                    source_character=source_character,
                    target_character=target_character,
                    delta=RelationshipDelta(
                        status_gap=status_gap,
                        info_gap=info_gap,
                        emotion_gap=emotion_gap,
                        interest_conflict=interest_conflict,
                        control_dependency=control_dependency,
                        trust_state=trust_state,
                        betrayal_risk=betrayal_risk,
                    ),
                    dominant_gap=current_dominant_gap,
                    relationship_velocity=clamp01(tension_score * 0.6 + betrayal_risk * 0.4),
                    tension_score=tension_score,
                    relation_layer=relation_layer,
                    relation_hint=relation_hint,
                )
            )
            previous = history_map.get(_pair_key(source_character, target_character))
            if previous is not None:
                previous_tension = clamp01(_to_float(previous.get("tension_score"), default=tension_score))
                previous_dominant_gap = str(previous.get("dominant_gap", current_dominant_gap))
                delta_tension = round(tension_score - previous_tension, 4)
                if abs(delta_tension) >= 0.08 or previous_dominant_gap != current_dominant_gap:
                    displacement_events.append(
                        RelationshipDisplacementEvent(
                            source_character=source_character,
                            target_character=target_character,
                            chapter_index=chapter_index,
                            previous_tension=previous_tension,
                            current_tension=tension_score,
                            delta_tension=delta_tension,
                            previous_dominant_gap=previous_dominant_gap,
                            current_dominant_gap=current_dominant_gap,
                            dominant_gap_shifted=previous_dominant_gap != current_dominant_gap,
                            relation_layer=relation_layer,
                            relation_hint=relation_hint,
                        )
                    )
            if tension_score > max_tension:
                max_tension = tension_score
                dominant_gap = current_dominant_gap

    aggregate_tension = (
        clamp01(sum(item.tension_score for item in profiles) / len(profiles))
        if profiles
        else 0.0
    )
    high_tension_edges = [
        {
            "source_character": item.source_character,
            "target_character": item.target_character,
            "tension_score": item.tension_score,
            "relationship_velocity": item.relationship_velocity,
            "dominant_gap": item.dominant_gap,
            "relation_layer": item.relation_layer,
            "relation_hint": item.relation_hint,
        }
        for item in sorted(profiles, key=lambda profile: profile.tension_score, reverse=True)[:3]
    ]
    graph_summary = RelationshipGraphSummary(
        node_count=len(
            {
                str(character.get("id", "")).strip()
                for character in characters
                if isinstance(character, dict) and str(character.get("id", "")).strip()
            }
        ),
        edge_count=len(profiles),
        displacement_count=len(displacement_events),
        high_tension_edges=high_tension_edges,
    )
    return RelationshipTensionResult(
        profiles=profiles,
        aggregate_tension=aggregate_tension,
        dominant_gap=dominant_gap,
        relationship_graph=graph_summary,
        displacement_events=displacement_events,
    )
