from __future__ import annotations

from fastapi.testclient import TestClient

import backend.app.api.routes.narrative_v4 as narrative_v4_route
import backend.app.services.narrative_v4.alert_channel as alert_channel_module
from backend.app.main import create_app
from backend.app.services.narrative_v4.alert_channel import V4AlertChannel
from backend.app.services.narrative_v4.memory_store import V4MemoryStore


def _payload() -> dict[str, object]:
    return {
        "characters": [
            {
                "id": "hero",
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
                "id": "rival",
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
        "pressure_items": [
            {"type": "survival", "intensity": 0.8},
            {"type": "humiliation", "intensity": 0.6},
        ],
    }


def _isolated_memory_store(tmp_path) -> V4MemoryStore:  # noqa: ANN001
    return V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )


def _isolated_alert_channel(tmp_path) -> V4AlertChannel:  # noqa: ANN001
    return V4AlertChannel(
        sink_path=tmp_path / "v4_observability_alerts.jsonl",
        state_path=tmp_path / "v4_observability_alerts.state.json",
        cooldown_seconds=600,
    )


def test_v4_plot_preview_endpoint_returns_payload_with_candidates_and_qc(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post(
        "/api/v4/plot/preview",
        json={
            **_payload(),
            "genre": "power_fantasy",
            "genre_profile": {"genre": "power_fantasy"},
            "v3_feedback_history": [
                {"accepted": False, "retention_delta": -0.18, "abandonment_delta": 0.2},
                {"accepted": True, "retention_delta": 0.06, "abandonment_delta": -0.03},
                {"accepted": True, "retention_delta": 0.11, "abandonment_delta": 0.0},
                {"accepted": True, "retention_delta": 0.09, "abandonment_delta": -0.02},
            ],
            "relationship_history": [
                {
                    "source_character": "hero",
                    "target_character": "rival",
                    "tension_score": 0.31,
                    "dominant_gap": "emotion",
                    "chapter_index": 17,
                }
            ],
            "chapter_index": 18,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["candidate_count"] >= 2
    assert payload["selected_candidate"] is not None
    assert payload["plot_candidates"]
    assert payload["qc_summary"]
    assert "warnings" in payload["qc_summary"]
    assert payload["relationship_graph"]["edge_count"] >= 1
    assert isinstance(payload["relationship_displacements"], list)
    assert payload["retention_writeback"]["feedback_count"] == 4
    assert payload["retention_writeback"]["adaptation_mode"] == "feedback-driven-multi-window"
    assert payload["retention_writeback"]["aggregation_strategy"] == "multi-window-decay-denoise"
    assert isinstance(payload["character_behavior_constraints"], list)
    assert payload["memory_summary"]["context_id"] == "api-v4-plot"
    assert isinstance(payload["relationship_timeline"], list)
    assert isinstance(payload["candidate_timeline"], list)
    assert payload["memory_summary"]["relationship_timeline_count"] >= 1
    assert payload["memory_summary"]["candidate_timeline_count"] >= 1
    assert all("displacement_count" in item for item in payload["relationship_timeline"])
    assert all("peak_delta_tension" in item for item in payload["relationship_timeline"])
    assert payload["memory_summary"]["relationship_timeline_displacement_count"] >= 0
    assert payload["memory_summary"]["memory_strategy"] == "append-window-decay-denoise-v2"
    assert payload["genre_calibration"]["genre"] == "power_fantasy"
    assert str(payload["genre_calibration"]["learning_mode"]).startswith("feedback-adaptive-v1")
    assert str(payload["memory_summary"]["genre_auto_learning_mode"]).startswith("feedback-adaptive-v1")
    assert payload["memory_summary"]["genre_auto_learning_sample_count"] >= 4
    assert isinstance(payload["memory_summary"]["genre_auto_learning_guard_profile"], dict)


def test_v4_plot_preview_endpoint_injects_behavior_constraints_for_high_stress_slider(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post(
        "/api/v4/plot/preview",
        json={
            "scene_id": "chapter-18",
            "chapter_index": 18,
            "characters": [
                {
                    "id": "hero",
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
                    "emotion_slider_map": {
                        "baseline": {"stress_baseline": 6.5},
                        "scene_overrides": {},
                    },
                },
                {
                    "id": "rival",
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
        },
    )
    assert response.status_code == 200
    payload = response.json()
    constraints = payload["character_behavior_constraints"]
    assert isinstance(constraints, list)
    assert constraints
    assert constraints[0]["character_id"] == "hero"
    assert constraints[0]["merged_sliders"]["stress_baseline"] == 6.5
    assert "High stress response" in constraints[0]["system_prompt_constraint"]


def test_v4_plot_preview_endpoint_accepts_relationship_graph_input_with_filtering(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post(
        "/api/v4/plot/preview",
        json={
            **_payload(),
            "chapter_index": 5,
            "relationship_graph_input": {
                "characters": ["hero", "rival"],
                "edges": [
                    {
                        "from": "hero",
                        "to": "rival",
                        "relation_type": "mentor",
                        "intensity": 0.8,
                        "bidirectional": True,
                        "hidden": True,
                        "chapter_range": [1, None],
                    },
                    {
                        "from": "hero",
                        "to": "rival",
                        "relation_type": "ally",
                        "intensity": 0.6,
                        "bidirectional": False,
                        "hidden": False,
                        "chapter_range": [1, 5],
                    },
                ],
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    constraints = payload["relationship_graph_constraints"]
    assert isinstance(constraints, dict)
    assert len(constraints["edges"]) == 1
    assert constraints["edges"][0]["relation_type"] == "ally"
    assert payload["memory_summary"]["relationship_graph_input_edges_total"] == 2
    assert payload["memory_summary"]["relationship_graph_input_edges_filtered"] == 1


def test_v4_plot_preview_endpoint_can_disable_v4_for_rollback(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post("/api/v4/plot/preview", json={**_payload(), "v4_enabled": False})
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["fallback_reason"] == "v4_disabled"
    assert payload["candidate_count"] == 0
    assert payload["v3_context"]["fallback_to_v3"] is True


def test_v4_workbench_preview_endpoint_returns_structured_preview(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post(
        "/api/v4/workbench/preview",
        json={
            "id": "live-chapter-18",
            "state": {
                "chapter_index": 18,
                "stage": "middle",
                "mainline_progress": 0.61,
                "sideplot_progress": 0.37,
                "conflict_intensity": 0.64,
                "emotional_temperature": 0.53,
                "pacing_speed": 0.49,
                "foreshadowing_load": 0.36,
                "payoff_pressure": 0.31,
                "characters": {},
                "tags": ["power", "middle"],
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["candidate_count"] >= 2
    assert payload["selected_candidate"] is not None
    assert payload["top_candidates"]
    assert payload["v4_input_profile"]["chapter_index"] == 18
    assert payload["relationship_graph"]["edge_count"] >= 1
    assert "retention_writeback" in payload
    assert "genre_calibration" in payload
    assert payload["memory_summary"]["context_id"] == "live-chapter-18"
    assert isinstance(payload["relationship_timeline"], list)
    assert isinstance(payload["candidate_timeline"], list)
    if payload["relationship_timeline"]:
        assert "displacement_count" in payload["relationship_timeline"][0]
        assert "peak_delta_tension" in payload["relationship_timeline"][0]


def test_v4_workbench_preview_endpoint_returns_fallback_when_state_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    response = client.post("/api/v4/workbench/preview", json={"id": "live-chapter-18"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["fallback_reason"] == "missing-state"
    assert payload["candidate_count"] == 0
    assert payload["candidate_timeline"] == []


def test_v4_workbench_preview_endpoint_reads_persisted_memory_on_next_call(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(narrative_v4_route, "memory_store", _isolated_memory_store(tmp_path))
    client = TestClient(create_app())
    context = {
        "id": "memory-case",
        "state": {
            "chapter_index": 18,
            "stage": "middle",
            "mainline_progress": 0.61,
            "sideplot_progress": 0.37,
            "conflict_intensity": 0.64,
            "emotional_temperature": 0.53,
            "pacing_speed": 0.49,
            "foreshadowing_load": 0.36,
            "payoff_pressure": 0.31,
            "characters": {},
            "tags": ["power", "middle"],
        },
        "v3_feedback_history": [
            {"accepted": False, "retention_delta": -0.2, "abandonment_delta": 0.18},
            {"accepted": True, "retention_delta": 0.07, "abandonment_delta": -0.03},
        ],
    }
    first = client.post("/api/v4/workbench/preview", json=context)
    assert first.status_code == 200

    second = client.post(
        "/api/v4/workbench/preview",
        json={
            **context,
            "v3_feedback_history": [],
        },
    )
    assert second.status_code == 200
    payload = second.json()
    assert payload["memory_summary"]["feedback_history_count"] >= 2
    assert payload["retention_writeback"]["feedback_count"] >= 2
    assert payload["retention_writeback"]["aggregation_strategy"] == "multi-window-decay-denoise"
    assert payload["memory_summary"]["feedback_denoised_count"] >= 0
    assert payload["memory_summary"]["candidate_timeline_count"] >= 1


def test_dashboard_endpoint_exposes_v4_observability_snapshot() -> None:
    client = TestClient(create_app())
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert "v4Observability" in payload
    snapshot = payload["v4Observability"]
    assert isinstance(snapshot.get("enabled"), bool)
    assert isinstance(snapshot.get("relationshipRows"), int)
    assert isinstance(snapshot.get("feedbackRows"), int)
    assert isinstance(snapshot.get("topGenres"), list)
    assert isinstance(snapshot.get("trend"), list)
    assert isinstance(snapshot.get("alerts"), list)
    assert isinstance(snapshot.get("alertCount"), int)
    assert isinstance(snapshot.get("criticalAlertCount"), int)
    assert isinstance(snapshot.get("runtimeRows"), int)
    assert isinstance(snapshot.get("latencyP95Ms"), float)
    assert isinstance(snapshot.get("errorRate"), float)
    assert isinstance(snapshot.get("fallbackRate"), float)
    assert isinstance(snapshot.get("runtimeThresholds"), dict)
    assert isinstance(snapshot.get("alertRouting"), dict)
    assert isinstance(snapshot.get("unifiedEnvelope"), dict)
    assert snapshot["unifiedEnvelope"]["schemaVersion"] == "obs-envelope.v1"
    assert snapshot["unifiedEnvelope"]["layer"] == "v4"


def test_v4_observability_snapshot_endpoint_returns_snapshot_and_routing(tmp_path, monkeypatch) -> None:
    memory_store = _isolated_memory_store(tmp_path)
    monkeypatch.setattr(narrative_v4_route, "memory_store", memory_store)
    monkeypatch.setattr(
        narrative_v4_route,
        "alert_channel",
        _isolated_alert_channel(tmp_path),
    )
    client = TestClient(create_app())

    # Seed memory rows so snapshot metrics are not empty.
    seeded = client.post(
        "/api/v4/plot/preview",
        json={
            **_payload(),
            "genre": "power_fantasy",
            "v3_feedback_history": [
                {"accepted": True, "retention_delta": 0.08, "abandonment_delta": -0.02},
                {"accepted": False, "retention_delta": -0.03, "abandonment_delta": 0.04},
            ],
            "chapter_index": 21,
        },
    )
    assert seeded.status_code == 200

    response = client.get("/api/v4/observability/snapshot?limit=200")
    assert response.status_code == 200
    snapshot = response.json()
    assert isinstance(snapshot.get("enabled"), bool)
    assert isinstance(snapshot.get("activeContexts"), int)
    assert isinstance(snapshot.get("relationshipRows"), int)
    assert isinstance(snapshot.get("feedbackRows"), int)
    assert isinstance(snapshot.get("runtimeRows"), int)
    assert snapshot.get("runtimeRows", 0) >= 1
    assert isinstance(snapshot.get("latencyP95Ms"), float)
    assert isinstance(snapshot.get("errorRate"), float)
    assert isinstance(snapshot.get("fallbackRate"), float)
    assert isinstance(snapshot.get("runtimeThresholds"), dict)
    assert isinstance(snapshot.get("alerts"), list)
    assert isinstance(snapshot.get("alertRouting"), dict)
    assert isinstance(snapshot.get("unifiedEnvelope"), dict)
    assert snapshot["unifiedEnvelope"]["schemaVersion"] == "obs-envelope.v1"
    assert snapshot["unifiedEnvelope"]["layer"] == "v4"
    assert "reason" in snapshot["alertRouting"]


def test_v4_observability_snapshot_endpoint_emits_runtime_threshold_alerts(tmp_path, monkeypatch) -> None:
    memory_store = _isolated_memory_store(tmp_path)
    monkeypatch.setattr(narrative_v4_route, "memory_store", memory_store)
    monkeypatch.setattr(
        narrative_v4_route,
        "alert_channel",
        _isolated_alert_channel(tmp_path),
    )
    client = TestClient(create_app())

    for index in range(12):
        memory_store.append_runtime_metric(
            route="/api/v4/plot/preview",
            status="error" if index < 2 else "fallback",
            latency_ms=1150 + index * 12,
            fallback_reason="v4_disabled" if index >= 2 else None,
            error_type="RuntimeError" if index < 2 else None,
            context_id=f"ctx-runtime-{index}",
        )

    response = client.get("/api/v4/observability/snapshot?limit=200")
    assert response.status_code == 200
    snapshot = response.json()
    assert snapshot["runtimeRows"] >= 12
    assert snapshot["latencyP95Ms"] >= 1100
    assert snapshot["errorRate"] >= 0.1
    assert snapshot["fallbackRate"] >= 0.7
    alert_codes = {
        str(item.get("code"))
        for item in snapshot["alerts"]
        if isinstance(item, dict)
    }
    assert "runtime-latency-p95-high" in alert_codes
    assert "runtime-error-rate-high" in alert_codes
    assert "runtime-fallback-rate-high" in alert_codes


def test_v4_observability_alert_route_endpoint_applies_cooldown(tmp_path, monkeypatch) -> None:
    memory_store = _isolated_memory_store(tmp_path)
    monkeypatch.setattr(narrative_v4_route, "memory_store", memory_store)
    monkeypatch.setattr(
        narrative_v4_route,
        "alert_channel",
        _isolated_alert_channel(tmp_path),
    )
    client = TestClient(create_app())

    # Seed critical condition: >= 12 feedback rows and low accept rate.
    memory_store.append_feedback_history(
        "ctx-alerts",
        [
            {
                "accepted": False,
                "retention_delta": -0.2,
                "abandonment_delta": 0.3,
                "chapter_index": 22,
            }
            for _ in range(12)
        ],
        source="test-critical",
        chapter_index=22,
        genre="power_fantasy",
    )

    first = client.post("/api/v4/observability/alerts/route?limit=200")
    assert first.status_code == 200
    first_body = first.json()
    assert isinstance(first_body.get("snapshot"), dict)
    assert isinstance(first_body.get("routing"), dict)
    assert first_body["routing"]["routed"] is True
    assert first_body["routing"]["reason"] == "routed-critical-alert"

    second = client.post("/api/v4/observability/alerts/route?limit=200")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["routing"]["routed"] is False
    assert second_body["routing"]["reason"] == "cooldown-active"


def test_v4_observability_alert_route_endpoint_routes_remote_targets(tmp_path, monkeypatch) -> None:
    delivered_urls: list[str] = []

    class _FakeResponse:
        status = 200

        def __enter__(self):  # noqa: ANN001
            return self

        def __exit__(self, exc_type, exc, traceback):  # noqa: ANN001
            return False

    def fake_urlopen(request, timeout):  # noqa: ANN001
        delivered_urls.append(str(request.full_url))
        return _FakeResponse()

    monkeypatch.setattr(alert_channel_module.urllib.request, "urlopen", fake_urlopen)

    memory_store = _isolated_memory_store(tmp_path)
    monkeypatch.setattr(narrative_v4_route, "memory_store", memory_store)
    monkeypatch.setattr(
        narrative_v4_route,
        "alert_channel",
        V4AlertChannel(
            sink_path=tmp_path / "v4_observability_alerts.jsonl",
            state_path=tmp_path / "v4_observability_alerts.state.json",
            cooldown_seconds=600,
            remote_targets={"webhook": "https://ops.example.internal/v4-alert"},
            oncall_contacts=("alice", "bob"),
            remote_timeout_seconds=1.5,
        ),
    )
    client = TestClient(create_app())

    memory_store.append_feedback_history(
        "ctx-alerts-remote",
        [
            {
                "accepted": False,
                "retention_delta": -0.2,
                "abandonment_delta": 0.3,
                "chapter_index": 22,
            }
            for _ in range(12)
        ],
        source="test-critical-remote",
        chapter_index=22,
        genre="power_fantasy",
    )

    response = client.post("/api/v4/observability/alerts/route?limit=200")
    assert response.status_code == 200
    payload = response.json()
    assert payload["routing"]["routed"] is True
    assert payload["routing"]["reason"] == "routed-critical-alert"
    assert payload["routing"]["oncallValidation"]["valid"] is True
    assert payload["routing"]["remoteRouting"]["enabled"] is True
    assert payload["routing"]["remoteRouting"]["status"] == "ok"
    assert payload["routing"]["remoteRouting"]["deliveredCount"] == 1
    assert payload["routing"]["remoteRouting"]["failedCount"] == 0
    assert delivered_urls == ["https://ops.example.internal/v4-alert"]
