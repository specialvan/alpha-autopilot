from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import json
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


def test_v7_api_supports_benchmark_version_repair() -> None:
    client = _create_v7_only_client()
    ingest = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-repair-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.71},
        },
    )
    assert ingest.status_code == 200
    version = ingest.json()["version"]

    store = narrative_v7_route._benchmark_store
    tampered_path = store.version_root / f"{version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.02
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (store.version_root / "api-malformed.json").write_text("{bad-json", encoding="utf-8")

    dry_run_response = client.post("/api/narrative/v7/benchmark/versions/repair?dry_run=true")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["candidate_failed_count"] >= 1
    assert dry_run["candidate_malformed_count"] >= 1
    assert dry_run["moved_count"] == 0

    apply_response = client.post("/api/narrative/v7/benchmark/versions/repair?dry_run=false")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["moved_count"] >= 2


def test_v7_api_supports_benchmark_maintenance_report() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-maint-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.76},
        },
    )
    response = client.get("/api/narrative/v7/benchmark/maintenance/report?limit=20")
    assert response.status_code == 200
    body = response.json()
    assert "audit" in body
    assert "health" in body
    assert body["severity"] in {"ok", "warn", "critical"}


def test_v7_api_supports_benchmark_auto_remediate() -> None:
    client = _create_v7_only_client()
    ingest = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-auto-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.67},
        },
    )
    assert ingest.status_code == 200
    version = ingest.json()["version"]

    store = narrative_v7_route._benchmark_store
    tampered_path = store.version_root / f"{version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.03
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (store.version_root / "auto-api-malformed.json").write_text("{bad-json", encoding="utf-8")

    dry_run_response = client.post("/api/narrative/v7/benchmark/versions/auto-remediate?dry_run=true&keep_last=1")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["repair"]["candidate_failed_count"] >= 1
    assert dry_run["repair"]["candidate_malformed_count"] >= 1

    apply_response = client.post("/api/narrative/v7/benchmark/versions/auto-remediate?dry_run=false&keep_last=1")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["repair"]["moved_count"] >= 2
    assert applied["health_after"]["failed_integrity_count"] == 0


def test_v7_api_supports_benchmark_maintenance_alert() -> None:
    client = _create_v7_only_client()
    ingest = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.66},
        },
    )
    assert ingest.status_code == 200
    version = ingest.json()["version"]

    store = narrative_v7_route._benchmark_store
    tampered_path = store.version_root / f"{version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.02
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    response = client.get("/api/narrative/v7/benchmark/maintenance/alert?limit=20")
    assert response.status_code == 200
    body = response.json()
    assert body["level"] in {"ok", "warn", "critical"}
    assert "policy" in body
    assert "report" in body
    assert "breaches" in body


def test_v7_api_supports_maintenance_alert_emit_and_list() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-list-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.65},
        },
    )

    emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
    assert emit_response.status_code == 200
    event_id = emit_response.json()["event"]["event_id"]
    assert event_id

    list_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=20")
    assert list_response.status_code == 200
    alerts = list_response.json()["alerts"]
    assert alerts
    assert alerts[0]["event_id"] == event_id


def test_v7_api_supports_maintenance_alert_prune() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-prune-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.69},
        },
    )

    for _ in range(3):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    store = narrative_v7_route._benchmark_store
    with (store.version_root / "_maintenance_alerts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/prune?keep_last=1&dry_run=true")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["candidate_count"] >= 2
    assert dry_run["pruned_count"] == 0
    assert dry_run["malformed_candidate_count"] >= 1

    apply_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/prune?keep_last=1&dry_run=false")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["kept_count"] == 1
    assert applied["pruned_count"] >= 2
    assert applied["malformed_dropped_count"] >= 1

    list_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=20")
    assert list_response.status_code == 200
    assert len(list_response.json()["alerts"]) == 1


def test_v7_api_supports_maintenance_alert_summary() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-summary-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.68},
        },
    )

    for _ in range(3):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    store = narrative_v7_route._benchmark_store
    with (store.version_root / "_maintenance_alerts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    summary_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts/summary?limit=2")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["window_event_count"] == 2
    assert summary["total_valid_events"] >= 3
    assert summary["malformed_line_count"] >= 1
    assert summary["latest_event"] is not None
    assert (
        summary["ok_count"] + summary["warn_count"] + summary["critical_count"]
    ) == summary["window_event_count"]


def test_v7_api_supports_maintenance_alert_digest() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-digest-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.67},
        },
    )
    emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
    assert emit_response.status_code == 200

    digest_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts/digest?limit=20")
    assert digest_response.status_code == 200
    digest = digest_response.json()
    assert digest["current_alert"]["level"] in {"ok", "warn", "critical"}
    assert digest["summary"]["total_valid_events"] >= 1
    assert digest["stale_threshold_seconds"] >= 0
    assert digest["recommended_action"] in {
        "observe",
        "emit_fresh_alert",
        "create_ticket",
        "page_oncall",
        "clean_alert_log",
    }


def test_v7_api_supports_maintenance_alert_export() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-export-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.71},
        },
    )
    emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
    assert emit_response.status_code == 200

    export_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts/export?limit=20")
    assert export_response.status_code == 200
    exported = export_response.json()
    assert exported["limit"] == 20
    assert exported["digest"]["current_alert"]["level"] in {"ok", "warn", "critical"}
    assert exported["digest"]["summary"]["total_valid_events"] >= 1
    assert exported["alerts"]


def test_v7_api_supports_maintenance_alert_cursor_paging() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-cursor-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.70},
        },
    )

    for _ in range(5):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    first_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=2")
    assert first_response.status_code == 200
    first = first_response.json()
    assert len(first["alerts"]) == 2
    assert first["has_more"] is True
    assert first["next_cursor"]

    second_response = client.get(
        f"/api/narrative/v7/benchmark/maintenance/alerts?limit=2&cursor={first['next_cursor']}"
    )
    assert second_response.status_code == 200
    second = second_response.json()
    assert len(second["alerts"]) == 2
    assert second["cursor"] == first["next_cursor"]

    export_response = client.get(
        f"/api/narrative/v7/benchmark/maintenance/alerts/export?limit=2&cursor={first['next_cursor']}"
    )
    assert export_response.status_code == 200
    exported = export_response.json()
    assert len(exported["alerts"]) == 2
    assert exported["cursor"] == first["next_cursor"]
    assert exported["total_valid_events"] >= 5


def test_v7_api_supports_maintenance_alert_archive() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-archive-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.72},
        },
    )

    for _ in range(5):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    store = narrative_v7_route._benchmark_store
    with (store.version_root / "_maintenance_alerts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/archive?keep_last=2&shard_size=2&dry_run=true"
    )
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["kept_count"] == 2
    assert dry_run["candidate_count"] >= 3
    assert dry_run["archive_shard_count"] == 0
    assert dry_run["malformed_candidate_count"] >= 1

    apply_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/archive?keep_last=2&shard_size=2&dry_run=false"
    )
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["kept_count"] == 2
    assert applied["archived_count"] >= 3
    assert applied["archive_shard_count"] >= 2
    assert applied["malformed_dropped_count"] >= 1
    assert applied["archive_files"]

    list_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=20")
    assert list_response.status_code == 200
    assert len(list_response.json()["alerts"]) == 2


def test_v7_api_supports_maintenance_alert_archive_file_listing_and_read() -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-archive-read-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.65},
        },
    )

    for _ in range(5):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    apply_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/archive?keep_last=2&shard_size=2&dry_run=false"
    )
    assert apply_response.status_code == 200
    assert apply_response.json()["archived_count"] >= 3

    files_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts/archive/files?limit=20")
    assert files_response.status_code == 200
    files_body = files_response.json()
    assert files_body["total_files"] >= 2
    assert files_body["files"]
    first_file = files_body["files"][0]["file_name"]

    read_response = client.get(
        f"/api/narrative/v7/benchmark/maintenance/alerts/archive/read?file_name={first_file}&limit=1"
    )
    assert read_response.status_code == 200
    read_body = read_response.json()
    assert read_body["message"] == "ok"
    assert read_body["total_valid_events"] >= 1
    assert len(read_body["alerts"]) == 1

    invalid_response = client.get(
        "/api/narrative/v7/benchmark/maintenance/alerts/archive/read?file_name=../bad.jsonl&limit=1"
    )
    assert invalid_response.status_code == 200
    assert invalid_response.json()["message"] == "invalid_file_name"


def test_v7_api_supports_maintenance_alert_auto_archive(monkeypatch) -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-auto-archive-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.66},
        },
    )

    for _ in range(4):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")

    dry_run_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/auto-archive?dry_run=true")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["should_archive"] is True
    assert dry_run["archive"] is not None
    assert dry_run["archive"]["dry_run"] is True

    apply_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/auto-archive?dry_run=false")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["should_archive"] is True
    assert applied["archive"] is not None
    assert applied["archive"]["dry_run"] is False
    assert applied["archive"]["kept_count"] == 1

    list_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=20")
    assert list_response.status_code == 200
    assert len(list_response.json()["alerts"]) == 1


def test_v7_api_supports_maintenance_alert_archive_cleanup(monkeypatch) -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-archive-cleanup-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.62},
        },
    )

    for _ in range(6):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    archive_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/archive?keep_last=1&shard_size=1&dry_run=false"
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["archive_shard_count"] >= 5

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "2")

    dry_run_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/archive/cleanup?dry_run=true")
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["candidate_count"] >= 3
    assert dry_run["max_shard_candidate_count"] >= 3

    apply_response = client.post("/api/narrative/v7/benchmark/maintenance/alerts/archive/cleanup?dry_run=false")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["removed_count"] >= 3
    assert applied["kept_count"] <= 2

    files_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts/archive/files?limit=20")
    assert files_response.status_code == 200
    assert files_response.json()["total_files"] <= 2


def test_v7_api_supports_maintenance_alert_governance_report_and_run(monkeypatch) -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-governance-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.69},
        },
    )

    for _ in range(5):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    report_response = client.get(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/report?alert_limit=20&archive_limit=20"
    )
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["policy"]["archive_trigger_count"] == 2
    assert report["projected_auto_archive"]["should_archive"] is True

    dry_run_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run?dry_run=true&alert_limit=20&archive_limit=20"
    )
    assert dry_run_response.status_code == 200
    dry_run = dry_run_response.json()
    assert dry_run["dry_run"] is True
    assert dry_run["auto_archive"]["should_archive"] is True
    assert dry_run["performed_steps"]

    apply_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run?dry_run=false&alert_limit=20&archive_limit=20"
    )
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["dry_run"] is False
    assert applied["auto_archive"]["should_archive"] is True
    assert applied["active_summary_after"]["total_valid_events"] <= 1

    list_response = client.get("/api/narrative/v7/benchmark/maintenance/alerts?limit=20")
    assert list_response.status_code == 200
    assert len(list_response.json()["alerts"]) <= 1


def test_v7_api_supports_governance_run_idempotency_and_history(monkeypatch) -> None:
    client = _create_v7_only_client()
    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-governance-idempotency-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.74},
        },
    )
    for _ in range(5):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    first_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run"
        "?dry_run=true&alert_limit=20&archive_limit=20&idempotency_key=governance-idem-001"
    )
    assert first_response.status_code == 200
    first = first_response.json()
    assert first["idempotency_reused"] is False
    assert first["run_id"]

    replay_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run"
        "?dry_run=true&alert_limit=20&archive_limit=20&idempotency_key=governance-idem-001"
    )
    assert replay_response.status_code == 200
    replay = replay_response.json()
    assert replay["idempotency_reused"] is True
    assert replay["run_id"] == first["run_id"]
    assert replay["request_fingerprint"] == first["request_fingerprint"]

    conflict_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run"
        "?dry_run=false&alert_limit=20&archive_limit=20&idempotency_key=governance-idem-001"
    )
    assert conflict_response.status_code == 409
    assert conflict_response.json()["detail"] == "idempotency_key_reused_with_different_request"

    history_response = client.get(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/runs?limit=20"
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total_records"] == 1
    assert history["records"][0]["status"] == "succeeded"


def test_v7_api_records_governance_failure_and_supports_retry(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(narrative_v7_router)
    client = TestClient(app, raise_server_exceptions=False)

    _ = client.post(
        "/api/narrative/v7/benchmark/ingest",
        json={
            "book_id": "book-alert-governance-retry-api",
            "channel": "fantasy",
            "genre_track": "fast",
            "sample_payload": {"nqm_mean": 0.70},
        },
    )
    for _ in range(4):
        emit_response = client.post("/api/narrative/v7/benchmark/maintenance/alert/emit?limit=20")
        assert emit_response.status_code == 200

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    store = narrative_v7_route._benchmark_store
    original_auto_archive = store.auto_archive_maintenance_alerts
    call_counter = {"value": 0}

    def flaky_auto_archive(*, dry_run: bool = True):
        call_counter["value"] += 1
        if call_counter["value"] == 1:
            raise RuntimeError("forced_governance_auto_archive_failure_api")
        return original_auto_archive(dry_run=dry_run)

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", flaky_auto_archive)

    failed_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run"
        "?dry_run=true&alert_limit=20&archive_limit=20&idempotency_key=governance-retry-seed-api"
    )
    assert failed_response.status_code == 500

    history_after_fail = client.get(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/runs?limit=20"
    )
    assert history_after_fail.status_code == 200
    failed_body = history_after_fail.json()
    assert failed_body["total_records"] == 1
    assert failed_body["records"][0]["status"] == "failed"
    failed_run_id = failed_body["records"][0]["run_id"]

    retry_response = client.post(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/run"
        f"?dry_run=true&alert_limit=20&archive_limit=20&retry_run_id={failed_run_id}&idempotency_key=governance-retry-001-api"
    )
    assert retry_response.status_code == 200
    retry_body = retry_response.json()
    assert retry_body["retry_run_id"] == failed_run_id
    assert retry_body["attempt"] == 2
    assert retry_body["idempotency_reused"] is False

    history_after_retry = client.get(
        "/api/narrative/v7/benchmark/maintenance/alerts/governance/runs?limit=20"
    )
    assert history_after_retry.status_code == 200
    final_history = history_after_retry.json()
    assert final_history["total_records"] == 2
    assert final_history["records"][0]["status"] == "succeeded"
    assert final_history["records"][0]["attempt"] == 2
    assert final_history["records"][1]["status"] == "failed"


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

