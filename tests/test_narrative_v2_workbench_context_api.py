from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import backend.app.api.routes.workbench_v2 as workbench_v2_route
from backend.app.main import create_app
from backend.app.services.narrative.history_service import HistoryService
from backend.app.services.narrative_v2.workbench_service import NarrativeV2WorkbenchService


def test_v2_workbench_service_default_history_service_is_not_shared() -> None:
    service_a = NarrativeV2WorkbenchService()
    service_b = NarrativeV2WorkbenchService()

    assert service_a.history_service is not service_b.history_service


def test_v2_workbench_context_route_returns_live_backend_context(tmp_path, monkeypatch) -> None:
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=tmp_path / "missing-workbench-contexts.json",
    )
    monkeypatch.setattr(
        workbench_v2_route,
        "service_factory",
        lambda: service,
    )
    client = TestClient(create_app())

    response = client.get("/api/v2/workbench/contexts")

    assert response.status_code == 200

    body = response.json()
    assert body["contexts"]
    assert body["contexts"][0]["state"]["chapter_index"] == 18
    assert body["contexts"][0]["state"]["stage"] == "middle"
    assert "history" in body["contexts"][0]["summary"].lower()
    assert body["contexts"][0]["v4_preview"]["enabled"] is True
    assert body["contexts"][0]["v4_preview"]["candidate_count"] >= 2
    assert body["contexts"][0]["v4_preview"]["relationship_graph"]["edge_count"] >= 1
    assert "retention_writeback" in body["contexts"][0]["v4_preview"]
    assert body["contexts"][0]["v4_preview"]["retention_writeback"]["feedback_count"] >= 1
    assert body["contexts"][0]["v8_preview"]["enabled"] is True
    assert body["contexts"][0]["v8_preview"]["next_control_state"]
    assert body["contexts"][0]["v8_preview"]["transition"]["next_state"]


def test_v2_workbench_context_route_returns_imported_quality_enrichment(tmp_path, monkeypatch) -> None:
    imported_path = tmp_path / "plotpilot" / "workbench_contexts.json"
    imported_path.parent.mkdir(parents=True, exist_ok=True)
    imported_path.write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "id": "plotpilot-chapter-01",
                        "chapterNumber": 1,
                        "title": "black jade awakens",
                        "stage": "opening",
                        "summary": "Imported PlotPilot fixture",
                        "state": {
                            "chapter_index": 1,
                            "stage": "opening",
                            "mainline_progress": 0.12,
                            "sideplot_progress": 0.04,
                            "conflict_intensity": 0.62,
                            "emotional_temperature": 0.48,
                            "pacing_speed": 0.58,
                            "foreshadowing_load": 0.22,
                            "payoff_pressure": 0.14,
                            "characters": {},
                            "tags": ["plotpilot"],
                        },
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    quality_dir = imported_path.parent / "v3_records"
    quality_dir.mkdir(parents=True, exist_ok=True)
    (quality_dir / "reverse_outline_records.jsonl").write_text(
        json.dumps(
            {
                "chapter_number": 1,
                "title": "black jade awakens",
                "admission": "provisional",
                "primary_function": "transition-breathing",
                "style_dna": {
                    "pace": "brisk",
                    "dialogue_reliance": "medium",
                    "emotional_directness": "balanced",
                },
                "checkpoints": [
                    {
                        "name": "continuity-stability",
                        "status": "pass",
                        "evidence": "Chapter identity and opening beat detected.",
                        "implication": "Context can be projected safely.",
                    }
                ],
                "workbench_context": {
                    "notes": "Derived from 1 paragraphs with transition-breathing."
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )
    monkeypatch.setattr(
        workbench_v2_route,
        "service_factory",
        lambda: service,
    )
    client = TestClient(create_app())

    response = client.get("/api/v2/workbench/contexts")

    assert response.status_code == 200
    body = response.json()
    assert body["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert body["contexts"][0]["admission"] == "provisional"
    assert body["contexts"][0]["primary_function"] == "transition-breathing"
    assert body["contexts"][0]["checkpoints"][0]["name"] == "continuity-stability"
    assert body["contexts"][0]["v4_preview"]["enabled"] is True
    assert body["contexts"][0]["v4_preview"]["candidate_count"] >= 2
    assert body["contexts"][0]["v4_preview"]["relationship_graph"]["edge_count"] >= 1
    assert body["contexts"][0]["v8_preview"]["enabled"] is True
    assert body["contexts"][0]["v8_preview"]["decision_mode"] in {"scored_fit", "fallback"}


def test_v2_workbench_context_route_falls_back_to_live_context_when_imported_json_is_corrupted(
    tmp_path,
    monkeypatch,
) -> None:
    imported_path = tmp_path / "plotpilot" / "workbench_contexts.json"
    imported_path.parent.mkdir(parents=True, exist_ok=True)
    imported_path.write_text("{bad-json", encoding="utf-8")

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )
    monkeypatch.setattr(workbench_v2_route, "service_factory", lambda: service)
    client = TestClient(create_app())

    response = client.get("/api/v2/workbench/contexts")

    assert response.status_code == 200
    body = response.json()
    assert body["contexts"]
    assert body["contexts"][0]["id"] == "live-chapter-18"
    assert body["source_diagnostics"]["local_report"]["status"] == "not-found"


def test_v2_workbench_context_route_prefers_real_chapter_report_contract(tmp_path, monkeypatch) -> None:
    plotpilot_root = tmp_path / "plotpilot"
    report_path = plotpilot_root / "raw" / "model_switch_tests" / "run-01" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "model": "gpt-5.4",
                "results": [
                    {
                        "chapter": 1,
                        "title": "black_jade_awakens",
                        "success": True,
                        "chars": 3100,
                        "preview": "A wounded cultivator escapes into the sword valley.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=plotpilot_root / "workbench_contexts.json",
    )
    monkeypatch.setattr(workbench_v2_route, "service_factory", lambda: service)
    client = TestClient(create_app())

    response = client.get("/api/v2/workbench/contexts")

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "plotpilot_report"
    assert body["context_contract"] == "real_chapter_context_v2"
    assert body["report_path"].endswith("report.json")
    assert "source_diagnostics" in body
    assert body["source_diagnostics"]["local_report"]["status"] == "ok"
    assert body["contexts"]
    assert body["contexts"][0]["id"] == "plotpilot-chapter-01"


def test_v2_workbench_context_route_openapi_exposes_explicit_response_model() -> None:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v2/workbench/contexts"]["get"]
    schema_ref = operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert schema_ref.endswith("/NarrativeV2WorkbenchContextsResponsePayload")


def test_v2_workbench_refresh_route_openapi_exposes_online_only_query_param() -> None:
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v2/workbench/contexts/refresh"]["post"]
    parameter_names = [item["name"] for item in operation.get("parameters", [])]
    assert "online_only" in parameter_names
    schema_ref = operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert schema_ref.endswith("/NarrativeV2WorkbenchContextsResponsePayload")


def test_v2_workbench_refresh_route_returns_contexts_payload(tmp_path, monkeypatch) -> None:
    report_path = tmp_path / "plotpilot" / "raw" / "model_switch_tests" / "run-01" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "model": "gpt-5.4",
                "results": [
                    {
                        "chapter": 1,
                        "title": "black_jade_awakens",
                        "success": True,
                        "chars": 3100,
                        "preview": "A wounded cultivator escapes into the sword valley.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=tmp_path / "plotpilot" / "workbench_contexts.json",
    )
    monkeypatch.setattr(workbench_v2_route, "service_factory", lambda: service)
    client = TestClient(create_app())

    response = client.post("/api/v2/workbench/contexts/refresh")

    assert response.status_code == 200
    body = response.json()
    assert body["context_contract"] == "real_chapter_context_v2"
    assert body["contexts"]
    assert "source_diagnostics" in body


def test_v2_workbench_refresh_route_supports_online_only_guard(monkeypatch) -> None:
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        online_report_api_url="https://plotpilot.example/api/latest-report",
        imported_context_path=Path("D:/non-existent/workbench_contexts.json"),
    )

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.workbench_service.probe_online_plotpilot_report_contexts",
        lambda **kwargs: {
            "payload": None,
            "diagnostics": {"status": "http-error", "attempted": True},
        },
    )
    monkeypatch.setattr(workbench_v2_route, "service_factory", lambda: service)
    client = TestClient(create_app())

    response = client.post("/api/v2/workbench/contexts/refresh?online_only=true")

    assert response.status_code == 200
    body = response.json()
    assert body["contexts"] == []
    assert body["fallback_reason"] == "online-report-unavailable"
    assert body["source"] == "plotpilot_api"
    assert body["source_diagnostics"]["online_report"]["status"] == "http-error"
