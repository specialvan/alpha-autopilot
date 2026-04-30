from __future__ import annotations

from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.conflict_probe import EmergentConflictProbeService
from backend.app.services.narrative_v6.schemas import (
    CharacterParameterizeRequest,
    EmergentConflictProbeRequest,
    NarrativeSeedExtractionRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _build_profiles_and_graph():
    seed_response = NarrativeSeedExtractor().extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {
                    "chapter_number": 31,
                    "text": "林墨说要夺回城门。苏澈点头。",
                },
                {
                    "chapter_number": 32,
                    "text": "苏澈背叛了林墨，北城宣战。",
                },
            ]
        )
    )
    profiles = CharacterParameterizer().parameterize(
        CharacterParameterizeRequest(seed=seed_response.seed)
    ).profiles
    graph = {
        "characters": [profile.character_id for profile in profiles],
        "edges": [
            {
                "from": profiles[0].character_id,
                "to": profiles[1].character_id,
                "relation_type": "enemy",
                "intensity": 0.92,
                "bidirectional": True,
                "hidden": False,
                "chapter_range": [1, None],
            }
        ],
    }
    return profiles, graph


def test_conflict_probe_generates_candidates_and_round_logs() -> None:
    profiles, graph = _build_profiles_and_graph()
    service = EmergentConflictProbeService()

    result = service.probe(
        EmergentConflictProbeRequest(
            characters=profiles,
            relationship_graph_input=graph,
            scene_constraints={"current_event": "siege"},
            rounds=3,
        )
    )

    assert len(result.interaction_rounds) == 3
    assert result.interaction_rounds[0].exchanges
    assert result.conflict_candidates
    candidate = result.conflict_candidates[0]
    assert candidate.trigger_characters
    assert candidate.trigger_relationship in {"enemy", "rival", "ally"}
    assert candidate.trigger_pressure
    assert candidate.trigger_personality
    assert result.recommended_plot_hooks
    assert "encounter_event" in result.six_step_binding_suggestions


def test_conflict_probe_respects_group_memory_and_emits_risk_flags() -> None:
    profiles, graph = _build_profiles_and_graph()
    service = EmergentConflictProbeService()

    payload = EmergentConflictProbeRequest(
        characters=profiles,
        relationship_graph_input=graph,
        group_memory_graph={
            "groups": [{"group_id": "g1", "name": "北城守军", "description": ""}],
            "memberships": [
                {"group_id": "g1", "character_id": profiles[0].character_id, "role": "member"}
            ],
            "group_memories": [],
            "behavior_effects": [
                {
                    "group_id": "g1",
                    "character_id": profiles[0].character_id,
                    "effect": {"alertness": 0.5},
                    "source_memory_id": "gm-1",
                    "hidden": False,
                }
            ],
            "propagation_logs": [],
            "reversible_patches": [],
        },
        scene_constraints={"current_event": "checkpoint"},
        rounds=2,
    )

    result = service.probe(payload)

    assert len(result.interaction_rounds) == 2
    assert any("group_alert" in item["pressure"] for item in result.interaction_rounds[0].exchanges)
    assert isinstance(result.risk_flags, list)
