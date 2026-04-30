from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

import backend.app.api.routes.narrative_v7 as narrative_v7_route
from backend.app.api.routes.narrative_v7 import router as narrative_v7_router
from backend.app.core.config import settings
from backend.app.services.narrative_v7.benchmark_library import BenchmarkLibrary
from backend.app.services.narrative_v7.benchmark_store import V7BenchmarkStore
from backend.app.services.narrative_v7.observability import V7RuntimeMetricsStore


@pytest.fixture(autouse=True)
def _isolated_benchmark_store(tmp_path, monkeypatch) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    monkeypatch.setattr(narrative_v7_route, "_benchmark_store", store)
    monkeypatch.setattr(narrative_v7_route, "_benchmark_library", BenchmarkLibrary(store=store))
    monkeypatch.setattr(
        narrative_v7_route,
        "_runtime_metrics_store",
        V7RuntimeMetricsStore(path=tmp_path / "v7_runtime_metrics.jsonl"),
    )
    monkeypatch.setattr(settings, "v7_enabled", True)
    monkeypatch.setattr(settings, "v7_opening_gate_enabled", True)
    monkeypatch.setattr(settings, "v7_antipattern_guard_enabled", True)
    monkeypatch.setattr(settings, "v7_deadlock_router_enabled", True)


def _create_v7_only_client() -> TestClient:
    app = FastAPI()
    app.include_router(narrative_v7_router)
    return TestClient(app)


def _sample_text() -> str:
    return "主角今晚必须守住北门，反派围剿逼近。真相到底是什么？众人注视他的选择。"


def test_v7_api_supports_sampling_and_threshold_preview() -> None:
    client = _create_v7_only_client()

    sample_response = client.post(
        "/api/narrative/v7/sample",
        json={
            "text": _sample_text(),
            "story_state": {"chapter_index": 1, "prev_nqm_close": 0.63},
            "character_states": [{"id": "c1"}, {"id": "c2"}],
        },
    )
    assert sample_response.status_code == 200
    sample_body = sample_response.json()
    assert sample_body["vector"]["composite"] >= 0.0

    threshold_response = client.post(
        "/api/narrative/v7/thresholds/preview",
        json={
            "vector": sample_body["vector"],
            "ohlcv": sample_body["ohlcv"],
            "benchmark_parameters": {
                "channel": "fantasy",
                "genre_track": "fast",
                "sample_count": 5,
                "nqm_mean": 0.7,
                "nqm_std": 0.08,
                "high_threshold": 0.78,
                "low_threshold": 0.52,
                "opening_gate_t8": 0.6,
            },
        },
    )
    assert threshold_response.status_code == 200
    assert threshold_response.json()["zone"] in {
        "hard_intervention",
        "elastic_injection",
        "free_generation",
    }


def test_v7_api_supports_opening_gate_and_decision_routes() -> None:
    client = _create_v7_only_client()

    gate_response = client.post(
        "/api/narrative/v7/opening-gate",
        json={
            "text": "我起床洗漱吃早饭，想了很多人生道理。",
            "chapter_index": 1,
            "allow_override": False,
        },
    )
    assert gate_response.status_code == 200
    assert gate_response.json()["blocked"] is True

    decision_response = client.post(
        "/api/narrative/v7/decision",
        json={
            "market_state": {
                "project_state": {
                    "project_id": "demo",
                    "platform": "qidian",
                    "genre_track": "fast",
                    "reader_profile": "male",
                    "ip_flavor_tag": "xuanhuan",
                    "selling_point_contract": "高压逆袭",
                },
                "story_state": {"chapter_index": 1},
                "benchmark_state": {
                    "book_id": "",
                    "channel": "fantasy",
                    "genre_track": "fast",
                    "sample_count": 5,
                    "nqm_mean": 0.68,
                    "nqm_std": 0.09,
                    "high_threshold": 0.78,
                    "low_threshold": 0.52,
                    "opening_gate_t8": 0.6,
                },
                "metric_state": {},
                "kline_state": {},
                "threshold_state": {},
                "decision_state": {
                    "last_decision_type": "observe",
                    "last_composite": 0.62,
                    "deviation": 0.0,
                    "available_position": 1.0,
                },
            },
            "vector": {
                "metrics": {
                    "P1": 0.5,
                    "P2": 0.5,
                    "P3": 0.5,
                    "P4": 0.5,
                    "P5": 0.5,
                    "P6": 0.5,
                    "P7": 0.5,
                    "T1": 0.5,
                    "T2": 0.5,
                    "T3": 0.5,
                    "T4": 0.5,
                    "T5": 0.5,
                    "T6": 0.5,
                    "T7": 0.5,
                    "T8": 0.4,
                    "T9": 0.5,
                    "T10": 0.5,
                    "W1": 0.5,
                    "W2": 0.5,
                    "W3": 0.5,
                    "W4": 0.5,
                    "W5": 0.5,
                    "W6": 0.5,
                    "A1": 0.5,
                    "A2": 0.5,
                    "A3": 0.5,
                    "A4": 0.5,
                    "A5": 0.5,
                    "A6": 0.5,
                },
                "composite": 0.55,
            },
            "ohlcv": {"open": 0.6, "high": 0.62, "low": 0.5, "close": 0.55, "volume": 650},
            "override_confirmed": False,
        },
    )

    assert decision_response.status_code == 200
    body = decision_response.json()
    assert body["decision"]["route_id"] == "R-04"
    assert body["decision"]["decision_type"] == "stop_loss"


def test_v7_api_exposes_decision_rules() -> None:
    client = _create_v7_only_client()
    response = client.get("/api/narrative/v7/decision/rules")
    assert response.status_code == 200
    body = response.json()
    assert "source" in body
    assert "rules" in body
    assert "opening_t8_gate" in body["rules"]


def test_v7_api_supports_benchmark_ingest_query_and_retract() -> None:
    client = _create_v7_only_client()

    ingest_response = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-100",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.74},
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["accepted"] is True

    query_response = client.post(
        "/api/narrative/v7/benchmark/query",
        json={"channel": "fantasy", "genre_track": "fast"},
    )
    assert query_response.status_code == 200
    assert query_response.json()["source_count"] == 1
    assert query_response.json()["corridor_ready"] is False
    assert "insufficient_samples_for_corridor" in query_response.json()["warnings"]

    retract_response = client.delete("/api/narrative/v7/benchmark/book-100")
    assert retract_response.status_code == 200
    assert retract_response.json()["retracted"] is True


def test_v7_api_supports_benchmark_versions_and_restore() -> None:
    client = _create_v7_only_client()
    for index in range(2):
        response = client.post(
            "/api/narrative/v7/benchmark/ingest",
            json={
                "book_id": f"book-v{index}",
                "channel": "fantasy",
                "genre_track": "fast",
                "sample_payload": {"nqm_mean": 0.70 + index * 0.05},
            },
        )
        assert response.status_code == 200

    versions_response = client.get("/api/narrative/v7/benchmark/versions?limit=20")
    assert versions_response.status_code == 200
    versions = versions_response.json()["versions"]
    assert len(versions) >= 2

    restore_response = client.post(f"/api/narrative/v7/benchmark/restore/{versions[0]['version']}")
    assert restore_response.status_code == 200
    restore_body = restore_response.json()
    assert restore_body["restored"] is True
    assert restore_body["requested_version"] == versions[0]["version"]


def test_v7_api_supports_benchmark_diff_and_audit_export() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-diff-a",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.65},
        },
    )
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-diff-b",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.77},
        },
    )
    _ = client.delete("/api/narrative/v7/benchmark/book-diff-b")

    versions_response = client.get("/api/narrative/v7/benchmark/versions?limit=10")
    assert versions_response.status_code == 200
    versions = versions_response.json()["versions"]
    assert len(versions) >= 2

    diff_response = client.get(
        "/api/narrative/v7/benchmark/versions/diff",
        params={"base_version": versions[1]["version"], "target_version": versions[0]["version"]},
    )
    assert diff_response.status_code == 200
    diff = diff_response.json()
    assert diff["comparable"] is True
    assert diff["deactivated_count"] >= 1

    audit_response = client.get("/api/narrative/v7/benchmark/audit/export?limit=20")
    assert audit_response.status_code == 200
    audit = audit_response.json()
    assert audit["version_count"] >= 1
    assert "generated_at" in audit


def test_v7_api_returns_404_for_missing_benchmark_diff_version() -> None:
    client = _create_v7_only_client()
    response = client.get(
        "/api/narrative/v7/benchmark/versions/diff",
        params={"base_version": "missing-a", "target_version": "missing-b"},
    )
    assert response.status_code == 404


def test_v7_api_supports_benchmark_version_prune() -> None:
    client = _create_v7_only_client()
    for index in range(3):
        _ = client.post(
            "/api/narrative/v7/benchmark/ingest",
            json={
                "book_id": f"book-prune-{index}",
                "channel": "fantasy",
                "genre_track": "fast",
                "sample_payload": {"nqm_mean": 0.60 + index * 0.1},
            },
        )

    dry_run_response = client.post("/api/narrative/v7/benchmark/versions/prune?keep_last=1&dry_run=true")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["pruned_count"] == 0
    assert dry_run["candidate_count"] >= 2

    apply_response = client.post("/api/narrative/v7/benchmark/versions/prune?keep_last=1&dry_run=false")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["pruned_count"] >= 2


def test_v7_api_supports_benchmark_version_health_scan() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-health-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.73},
        },
    )
    response = client.get("/api/narrative/v7/benchmark/versions/health")
    assert response.status_code == 200
    body = response.json()
    assert body["total_files"] >= 1
    assert "generated_at" in body


def test_v7_api_returns_conflict_for_duplicate_benchmark_ingest() -> None:
    client = _create_v7_only_client()
    payload = {
        "book_id": "book-dup",
        "channel": "fantasy",
        "genre_track": "fast",
        "sample_payload": {"nqm_mean": 0.71},
    }

    first = client.post("/api/narrative/v7/benchmark/ingest", json=payload)
    assert first.status_code == 200

    duplicate = client.post("/api/narrative/v7/benchmark/ingest", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "duplicate_book_id"


def test_v7_api_respects_feature_flag_for_opening_gate(monkeypatch) -> None:
    monkeypatch.setattr(settings, "v7_opening_gate_enabled", False)
    client = _create_v7_only_client()
    response = client.post(
        "/api/narrative/v7/opening-gate",
        json={"text": "主角必须活下来。", "chapter_index": 1, "allow_override": False},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "opening_gate_disabled"


def test_v7_api_respects_global_v7_feature_flag(monkeypatch) -> None:
    monkeypatch.setattr(settings, "v7_enabled", False)
    client = _create_v7_only_client()
    response = client.post(
        "/api/narrative/v7/sample",
        json={"text": _sample_text(), "story_state": {}, "character_states": []},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "v7_disabled"


def test_v7_api_exposes_observability_snapshot() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/sample",
        json={
            "text": _sample_text(),
            "story_state": {"chapter_index": 1, "prev_nqm_close": 0.63},
            "character_states": [{"id": "c1"}],
        },
    )
    _ = client.post(
        "/api/narrative/v7/benchmark/query",
        json={"channel": "fantasy", "genre_track": "fast"},
    )

    response = client.get("/api/narrative/v7/observability?limit=200")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["runtimeRows"] >= 2
    routes = {item["route"] for item in body["routes"]}
    assert "/api/narrative/v7/sample" in routes
    assert "/api/narrative/v7/benchmark/query" in routes
    assert "thresholds" in body
    assert body["thresholds"]["latencyP95Ms"] > 0
    assert body["thresholds"]["errorRate"] >= 0


def test_v7_api_rejects_empty_benchmark_payload() -> None:
    client = _create_v7_only_client()
    response = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={"book_id": "book-empty", "channel": "fantasy", "genre_track": "fast", "sample_payload": {}},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "empty_sample_payload"
