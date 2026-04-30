from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RELATIONSHIP_TYPES: tuple[str, ...] = (
    "friend",
    "rival",
    "lover",
    "mentor",
    "enemy",
    "ally",
)


class RelationshipEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_character: str = Field(alias="from")
    to_character: str = Field(alias="to")
    relation_type: Literal["friend", "rival", "lover", "mentor", "enemy", "ally"]
    intensity: float = Field(ge=0.0, le=1.0)
    bidirectional: bool = True
    hidden: bool = False
    chapter_range: tuple[int | None, int | None] = (1, None)


class RelationshipGraphInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    characters: list[str] = Field(default_factory=list)
    edges: list[RelationshipEdge] = Field(default_factory=list)


def relationship_graph_json_schema() -> dict[str, object]:
    return RelationshipGraphInput.model_json_schema(by_alias=True)


def validate_relationship_graph_schema(payload: object) -> RelationshipGraphInput:
    return RelationshipGraphInput.model_validate(payload)


def filter_relationship_edges(
    graph: RelationshipGraphInput,
    *,
    current_chapter: int | None,
    reveal_disguise: bool,
) -> list[RelationshipEdge]:
    filtered: list[RelationshipEdge] = []
    for edge in graph.edges:
        if edge.hidden and not reveal_disguise:
            continue
        if not _in_chapter_range(edge.chapter_range, current_chapter=current_chapter):
            continue
        filtered.append(edge)
    return filtered


def relationship_edges_to_history_rows(
    edges: list[RelationshipEdge],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for edge in edges:
        rows.append(
            {
                "source_character": edge.from_character,
                "target_character": edge.to_character,
                "tension_score": round(float(edge.intensity), 4),
                "dominant_gap": "emotion",
                "relation_type": edge.relation_type,
                "hidden": edge.hidden,
                "chapter_index": None,
            }
        )
        if edge.bidirectional:
            rows.append(
                {
                    "source_character": edge.to_character,
                    "target_character": edge.from_character,
                    "tension_score": round(float(edge.intensity), 4),
                    "dominant_gap": "emotion",
                    "relation_type": edge.relation_type,
                    "hidden": edge.hidden,
                    "chapter_index": None,
                }
            )
    return rows


def export_relationship_graph_from_triples(
    triples: object,
) -> dict[str, object]:
    rows = triples if isinstance(triples, list) else []
    characters: set[str] = set()
    edges: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        source = str(
            row.get("subject")
            or row.get("source")
            or row.get("head")
            or "",
        ).strip()
        target = str(
            row.get("object")
            or row.get("target")
            or row.get("tail")
            or "",
        ).strip()
        if not source or not target:
            continue
        predicate = str(row.get("predicate") or row.get("relation_type") or "ally").strip().lower()
        relation_type = predicate if predicate in RELATIONSHIP_TYPES else "ally"
        intensity = _safe_float(row.get("intensity"), default=0.5)
        intensity = max(0.0, min(1.0, round(intensity, 4)))
        chapter_range = row.get("chapter_range")
        if isinstance(chapter_range, (list, tuple)) and len(chapter_range) == 2:
            chapter_range_pair = [
                _safe_int(chapter_range[0]),
                _safe_int(chapter_range[1]),
            ]
        else:
            chapter_range_pair = [1, None]
        edges.append(
            {
                "from": source,
                "to": target,
                "relation_type": relation_type,
                "intensity": intensity,
                "bidirectional": bool(row.get("bidirectional", True)),
                "hidden": bool(row.get("hidden", False)),
                "chapter_range": chapter_range_pair,
            }
        )
        characters.add(source)
        characters.add(target)
    return {
        "characters": sorted(characters),
        "edges": edges,
    }


def _in_chapter_range(
    chapter_range: tuple[int | None, int | None],
    *,
    current_chapter: int | None,
) -> bool:
    if current_chapter is None:
        return True
    start, end = chapter_range
    start_value = 1 if start is None else int(start)
    end_value = end
    if current_chapter < start_value:
        return False
    if end_value is not None and current_chapter > int(end_value):
        return False
    return True


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _safe_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None
