from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

import backend.app.api.routes.narrative_v6 as narrative_v6_route
from backend.app.core.config import settings
from backend.app.main import create_app
from backend.app.services.narrative_v6.graph_memory_store import PersistentGraphMemoryStore
from backend.app.services.narrative_v6.observability import V6RuntimeMetricsStore
from backend.app.services.narrative_v6.state_store import PersistentSimulationStore


@pytest.fixture(autouse=True)
def _isolated_simulation_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        narrative_v6_route,
        "simulation_store",
        PersistentSimulationStore(path=tmp_path / "v6_simulation_store.jsonl"),
    )
    monkeypatch.setattr(
        narrative_v6_route,
        "runtime_metrics_store",
        V6RuntimeMetricsStore(path=tmp_path / "v6_runtime_metrics.jsonl"),
    )
    monkeypatch.setattr(
        narrative_v6_route,
        "graph_memory_store",
        PersistentGraphMemoryStore(path=tmp_path / "v6_graph_memory.jsonl"),
    )


def _seed_request_payload() -> dict[str, object]:
    return {
        "chapters": [
            {
                "chapter_number": 5,
                "text": "林墨说我们必须守住北门。苏澈问是否要撤退。",
            },
            {
                "chapter_number": 6,
                "text": "苏澈背叛了林墨，北城宣战，失踪钥匙到底在哪？",
            },
        ],
        "mode": "full",
    }


def _prepare_simulation(client: TestClient) -> tuple[dict[str, object], list[dict[str, object]], str]:
    seed_response = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload())
    assert seed_response.status_code == 200
    seed_body = seed_response.json()

    parameterize_response = client.post(
        "/api/narrative/v6/characters/parameterize",
        json={
            "seed": seed_body["seed"],
            "selected_character_ids": [],
            "existing_profiles": [],
            "overrides": [],
        },
    )
    assert parameterize_response.status_code == 200
    profiles = parameterize_response.json()["profiles"]

    simulation_response = client.post(
        "/api/narrative/v6/simulations/parallel",
        json={
            "story_state": {"chapter_index": 6, "stage": "middle"},
            "narrative_seed": seed_body["seed"],
            "character_profiles": profiles,
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "path_count": 3,
            "strategies": ["retention_first", "suspense_first", "relationship_burst"],
        },
    )
    assert simulation_response.status_code == 200
    simulation_id = simulation_response.json()["simulation_id"]
    return seed_body, profiles, simulation_id


def test_v6_api_supports_seed_parameterization_and_parallel_simulation_flow() -> None:
    client = TestClient(create_app())

    seed_body, profiles, simulation_id = _prepare_simulation(client)
    assert seed_body["seed"]["characters"]
    assert profiles

    get_response = client.get(f"/api/narrative/v6/simulations/{simulation_id}")
    assert get_response.status_code == 200
    assert get_response.json()["simulation_id"] == simulation_id
    paths = get_response.json()["paths"]
    ok_paths = [path for path in paths if path["status"] == "ok"]
    assert ok_paths
    assert ok_paths[0]["graph_rag_hints"]


def test_v6_api_parallel_simulation_accepts_plot_unit_scaffold_contract() -> None:
    client = TestClient(create_app())

    seed_response = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload())
    assert seed_response.status_code == 200
    seed_body = seed_response.json()
    parameterize_response = client.post(
        "/api/narrative/v6/characters/parameterize",
        json={
            "seed": seed_body["seed"],
            "selected_character_ids": [],
            "existing_profiles": [],
            "overrides": [],
        },
    )
    assert parameterize_response.status_code == 200
    profiles = parameterize_response.json()["profiles"]

    simulation_response = client.post(
        "/api/narrative/v6/simulations/parallel",
        json={
            "story_state": {"chapter_index": 6, "stage": "middle"},
            "narrative_seed": seed_body["seed"],
            "character_profiles": profiles,
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "path_count": 3,
            "strategies": ["retention_first", "suspense_first", "relationship_burst"],
            "plot_unit_scaffold": {
                "encounter_event": "密钥暴露导致守军临时改道",
                "desire_goal": "保住密钥并维持北城同盟",
                "obstacle": "内应借补给线制造信息误导",
                "solution_method": "主角以假情报分流敌军注意力",
                "action_climax": {"node": "在补给站对峙中识破内应", "turn_type": "character_contrast"},
                "resolution": "同盟暂稳，但主角信任体系破裂",
            },
        },
    )
    assert simulation_response.status_code == 200
    body = simulation_response.json()
    ok_paths = [path for path in body["paths"] if path["status"] == "ok"]
    assert ok_paths
    mapping = ok_paths[0]["six_step_scaffold_mapping"]
    assert mapping["encounter_event"] == "密钥暴露导致守军临时改道"
    assert mapping["action_climax"] == "在补给站对峙中识破内应"
    assert mapping["action_climax_turn_type"] == "character_contrast"


def test_v6_api_returns_404_when_simulation_is_missing() -> None:
    client = TestClient(create_app())

    response = client.get("/api/narrative/v6/simulations/not-found-id")

    assert response.status_code == 404
    assert "simulation not found" in response.json()["detail"]


def test_v6_api_respects_global_feature_flag(monkeypatch) -> None:
    monkeypatch.setattr(settings, "v6_enabled", False)
    client = TestClient(create_app())

    response = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload())

    assert response.status_code == 503
    assert response.json()["detail"] == "v6_disabled"


def test_v6_api_supports_conflict_probe_and_group_memory() -> None:
    client = TestClient(create_app())
    seed_body, profiles, _simulation_id = _prepare_simulation(client)

    group_response = client.post(
        "/api/narrative/v6/group-memory/apply",
        json={
            "groups": [{"group_id": "g1", "name": "北城守军", "description": ""}],
            "memberships": [{"group_id": "g1", "character_id": profiles[0]["character_id"], "role": "member"}],
            "group_memories": [
                {
                    "memory_id": "gm-1",
                    "group_id": "g1",
                    "summary": "曾遭背叛",
                    "influence": {"alertness": 0.4},
                    "chapter_start": 1,
                    "chapter_end": 10,
                    "hidden": False,
                    "propagation_strength": 0.5,
                }
            ],
            "chapter_index": 6,
            "reveal_hidden": False,
        },
    )
    assert group_response.status_code == 200
    group_graph = group_response.json()
    assert isinstance(group_graph["behavior_effects"], list)

    probe_response = client.post(
        "/api/narrative/v6/conflicts/probe",
        json={
            "characters": profiles,
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "group_memory_graph": group_graph,
            "scene_constraints": {"current_event": "siege"},
            "rounds": 3,
        },
    )
    assert probe_response.status_code == 200
    probe_body = probe_response.json()
    assert len(probe_body["interaction_rounds"]) == 3
    assert "conflict_candidates" in probe_body


def test_v6_api_supports_event_injection_and_character_interview() -> None:
    client = TestClient(create_app())
    seed_body, profiles, simulation_id = _prepare_simulation(client)

    inject_response = client.post(
        f"/api/narrative/v6/simulations/{simulation_id}/inject-event",
        json={
            "injected_event": {
                "event_id": "evt-api-1",
                "event_type": "betrayal",
                "description": "关键角色倒戈",
                "affected_characters": [profiles[0]["character_id"]],
                "force_level": 0.9,
            },
            "author_intent": {"forbid_character_death": True},
            "macro_story_structure": "anthology",
        },
    )
    assert inject_response.status_code == 200
    inject_body = inject_response.json()
    assert inject_body["simulation_id"] == simulation_id
    assert inject_body["updated_paths"]
    assert inject_body["audit_log"]

    interview_response = client.post(
        f"/api/narrative/v6/characters/{profiles[0]['character_id']}/interview",
        json={
            "profile": profiles[0],
            "chapter_memory": ["第6章：北城冲突升级"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "user_message": "请用你的口吻回应我",
            "mode": "voice_test",
            "allow_hidden_info": False,
        },
    )
    assert interview_response.status_code == 200
    interview_body = interview_response.json()
    assert interview_body["character_id"] == profiles[0]["character_id"]
    assert interview_body["transcript"]
    assert "graph_rag_hints" in interview_body


def test_v6_api_exposes_observability_snapshot() -> None:
    client = TestClient(create_app())
    _seed_body, _profiles, simulation_id = _prepare_simulation(client)
    assert client.get(f"/api/narrative/v6/simulations/{simulation_id}").status_code == 200
    assert client.get("/api/narrative/v6/simulations/not-found-observe").status_code == 404
    graph_response = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={"query": "北城", "top_k": 2},
    )
    assert graph_response.status_code == 200

    observe_response = client.get("/api/narrative/v6/observability?limit=200")

    assert observe_response.status_code == 200
    body = observe_response.json()
    assert body["enabled"] is True
    assert body["runtimeRows"] >= 5
    assert "latencyP95Ms" in body
    assert "errorRate" in body
    assert "fallbackRate" in body
    routes = {item["route"] for item in body["routes"]}
    assert "/api/narrative/v6/simulations/parallel" in routes
    assert "/api/narrative/v6/simulations/{simulation_id}" in routes
    assert "/api/narrative/v6/graph/retrieve" in routes


def test_v6_api_supports_graph_rag_retrieval_endpoint() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    response = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "include_hidden": False,
            "chapter_index": 6,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["hits"]
    assert body["retrieval_mode"] == "deterministic"
    assert body["fallback_used"] in {True, False}


def test_v6_api_graph_retrieval_supports_cross_session_history_stitching() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    first = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "chapter_index": 6,
        },
    )
    assert first.status_code == 200
    assert first.json()["hits"]

    second = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "背叛",
            "top_k": 4,
            "chapter_index": 6,
        },
    )

    assert second.status_code == 200
    body = second.json()
    assert body["history_recall_used"] is True
    assert body["stitched_from_history_count"] >= 1
    assert body["hits"]
    assert any(item["node_type"] == "history_memory" for item in body["hits"])


def test_v6_api_supports_graph_memory_compaction_endpoint() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    first = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "chapter_index": 6,
        },
    )
    assert first.status_code == 200
    assert first.json()["hits"]

    compact_response = client.post("/api/narrative/v6/graph/memory/compact")

    assert compact_response.status_code == 200
    body = compact_response.json()
    assert body["before"] >= body["after"] >= 1
    assert body["removed"] == body["before"] - body["after"]


def test_v6_api_supports_graph_memory_audit_endpoint() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    retrieve_response = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "chapter_index": 6,
        },
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["hits"]

    audit_response = client.get("/api/narrative/v6/graph/memory/audit?limit=2")

    assert audit_response.status_code == 200
    body = audit_response.json()
    assert body["total_rows"] >= 1
    assert body["active_rows"] >= 1
    assert body["chapter_min"] == 6
    assert body["chapter_max"] == 6
    assert "/api/narrative/v6/graph/retrieve" in body["by_source_route"]
    assert "policy" in body
    assert len(body["latest_records"]) <= 2


def test_v6_api_supports_graph_memory_audit_snapshot_history() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    retrieve_response = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "chapter_index": 6,
        },
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["hits"]

    snapshot_response = client.post("/api/narrative/v6/graph/memory/audit/snapshot?limit=2")
    history_response = client.get("/api/narrative/v6/graph/memory/audit/history?limit=2")

    assert snapshot_response.status_code == 200
    snapshot = snapshot_response.json()
    assert snapshot["total_rows"] >= 1
    assert snapshot["audit_path"].endswith("v6_graph_memory_audit.jsonl")

    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["total_rows"] == snapshot["total_rows"]
    assert history[0]["audit_path"] == snapshot["audit_path"]


def test_v6_api_supports_graph_memory_audit_alerts_endpoint() -> None:
    client = TestClient(create_app())
    seed_body = client.post("/api/narrative/v6/seed/extract", json=_seed_request_payload()).json()

    retrieve_response = client.post(
        "/api/narrative/v6/graph/retrieve",
        json={
            "query": "苏澈 背叛 北城",
            "narrative_seed": seed_body["seed"],
            "relationship_graph_input": seed_body["relationship_graph_input"],
            "top_k": 4,
            "chapter_index": 6,
        },
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["hits"]
    assert client.post("/api/narrative/v6/graph/memory/audit/snapshot?limit=2").status_code == 200

    alerts_response = client.get("/api/narrative/v6/graph/memory/audit/alerts?limit=5")

    assert alerts_response.status_code == 200
    body = alerts_response.json()
    assert body["enabled"] is True
    assert body["history_count"] >= 1
    assert "thresholds" in body
    assert "alerts" in body
