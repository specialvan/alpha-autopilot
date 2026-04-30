from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from backend.app.services.narrative_v4.bridge import build_v4_bridge_payload_with_memory
from backend.app.services.narrative_v4.memory_store import V4MemoryStore
from backend.app.services.narrative_v4.relationship_graph import (
    export_relationship_graph_from_triples,
    filter_relationship_edges,
    relationship_graph_json_schema,
    validate_relationship_graph_schema,
)


def test_relationship_graph_schema_validation_and_filtering() -> None:
    graph = validate_relationship_graph_schema(
        {
            "characters": ["A", "B"],
            "edges": [
                {
                    "from": "A",
                    "to": "B",
                    "relation_type": "mentor",
                    "intensity": 0.8,
                    "bidirectional": True,
                    "hidden": True,
                    "chapter_range": [1, None],
                },
                {
                    "from": "A",
                    "to": "B",
                    "relation_type": "rival",
                    "intensity": 0.4,
                    "bidirectional": False,
                    "hidden": False,
                    "chapter_range": [5, 6],
                },
            ],
        }
    )

    no_reveal = filter_relationship_edges(
        graph,
        current_chapter=5,
        reveal_disguise=False,
    )
    reveal = filter_relationship_edges(
        graph,
        current_chapter=5,
        reveal_disguise=True,
    )
    assert len(no_reveal) == 1
    assert no_reveal[0].relation_type == "rival"
    assert len(reveal) == 2


def test_relationship_graph_schema_rejects_invalid_relation_type() -> None:
    with pytest.raises(ValidationError):
        validate_relationship_graph_schema(
            {
                "characters": ["A", "B"],
                "edges": [
                    {
                        "from": "A",
                        "to": "B",
                        "relation_type": "family",
                        "intensity": 0.7,
                        "bidirectional": True,
                        "hidden": False,
                        "chapter_range": [1, None],
                    }
                ],
            }
        )


def test_relationship_graph_exposes_json_schema_contract() -> None:
    schema = relationship_graph_json_schema()

    assert schema["type"] == "object"
    assert "properties" in schema
    properties = schema["properties"]
    assert "characters" in properties
    assert "edges" in properties
    dumped = json.dumps(schema)
    assert '"relation_type"' in dumped
    assert '"chapter_range"' in dumped
    assert '"mentor"' in dumped


def test_export_relationship_graph_from_existing_triples() -> None:
    graph = export_relationship_graph_from_triples(
        [
            {"subject": "Hero", "predicate": "mentor", "object": "Junior", "intensity": 0.9},
            {"source": "Hero", "relation_type": "enemy", "target": "Rival", "hidden": True},
        ]
    )

    assert sorted(graph["characters"]) == ["Hero", "Junior", "Rival"]
    assert len(graph["edges"]) == 2
    assert graph["edges"][0]["relation_type"] in {"mentor", "enemy", "ally"}


def test_bridge_filters_hidden_and_chapter_range_edges_from_relationship_graph_input(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-graph-input",
            "chapter_index": 5,
            "v4_enabled": True,
            "characters": [
                {
                    "id": "A",
                    "status": 0.2,
                    "knowledge": 0.4,
                    "emotion": 0.7,
                    "interest_conflict": 0.6,
                    "control": 0.5,
                    "dependency": 0.3,
                    "trust": 0.4,
                    "impulsiveness": 0.8,
                    "calmness": 0.3,
                    "resilience": 0.7,
                    "directness": 0.9,
                    "pragmatism": 0.7,
                    "idealism": 0.2,
                    "assertiveness": 0.8,
                    "avoidance": 0.1,
                    "self_protection": 0.4,
                    "sacrifice_tendency": 0.3,
                    "risk_appetite": 0.8,
                },
                {
                    "id": "B",
                    "status": 0.8,
                    "knowledge": 0.7,
                    "emotion": 0.2,
                    "interest_conflict": 0.8,
                    "control": 0.7,
                    "dependency": 0.2,
                    "trust": 0.1,
                    "impulsiveness": 0.3,
                    "calmness": 0.8,
                    "resilience": 0.5,
                    "directness": 0.4,
                    "pragmatism": 0.8,
                    "idealism": 0.2,
                    "assertiveness": 0.6,
                    "avoidance": 0.2,
                    "self_protection": 0.8,
                    "sacrifice_tendency": 0.2,
                    "risk_appetite": 0.4,
                },
            ],
            "pressure_items": [{"type": "survival", "intensity": 0.8}],
            "relationship_graph_input": {
                "characters": ["A", "B"],
                "edges": [
                    {
                        "from": "A",
                        "to": "B",
                        "relation_type": "mentor",
                        "intensity": 0.8,
                        "bidirectional": True,
                        "hidden": True,
                        "chapter_range": [1, None],
                    },
                    {
                        "from": "A",
                        "to": "B",
                        "relation_type": "rival",
                        "intensity": 0.5,
                        "bidirectional": False,
                        "hidden": False,
                        "chapter_range": [6, None],
                    },
                    {
                        "from": "A",
                        "to": "B",
                        "relation_type": "ally",
                        "intensity": 0.6,
                        "bidirectional": False,
                        "hidden": False,
                        "chapter_range": [1, 5],
                    },
                ],
            },
        },
        memory_store=memory_store,
        context_id="ctx-graph-input",
        history_window=20,
    )

    constraints = payload["relationship_graph_constraints"]
    assert isinstance(constraints, dict)
    assert len(constraints["edges"]) == 1
    assert constraints["edges"][0]["relation_type"] == "ally"
    summary = payload["memory_summary"]
    assert summary["relationship_graph_input_edges_total"] == 3
    assert summary["relationship_graph_input_edges_filtered"] == 1
    assert summary["relationship_graph_hidden_filtered_count"] >= 1
