from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

import backend.app.api.routes.narrative_v7 as narrative_v7_route
from backend.app.api.routes.narrative_v7 import router as narrative_v7_router
from backend.app.services.narrative_v7.benchmark_library import BenchmarkLibrary
from backend.app.services.narrative_v7.benchmark_store import V7BenchmarkStore


@pytest.fixture(autouse=True)
def _isolated_benchmark_store(tmp_path, monkeypatch) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    monkeypatch.setattr(narrative_v7_route, "_benchmark_store", store)
    monkeypatch.setattr(narrative_v7_route, "_benchmark_library", BenchmarkLibrary(store=store))


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

    retract_response = client.delete("/api/narrative/v7/benchmark/book-100")
    assert retract_response.status_code == 200
    assert retract_response.json()["retracted"] is True
