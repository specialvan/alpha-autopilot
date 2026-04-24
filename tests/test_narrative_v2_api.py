from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.app.api.routes.recommendation_v2 as recommendation_v2_route
from backend.app.services.narrative_v2.preview_service import NarrativeV2PreviewService


def _preview_payload(case_id: str = "case-001") -> dict[str, object]:
    return {
        "case_id": case_id,
        "state": {
            "chapter_index": 5,
            "stage": "middle",
            "mainline_progress": 0.42,
            "sideplot_progress": 0.2,
            "conflict_intensity": 0.61,
            "emotional_temperature": 0.58,
            "pacing_speed": 0.47,
            "foreshadowing_load": 0.34,
            "payoff_pressure": 0.29,
            "tags": ["power"],
            "characters": {
                "hero": {
                    "name": "hero",
                    "presence": 0.8,
                    "consistency_risk": 0.1,
                    "relationship_tension": 0.5,
                    "arc_progress": 0.25,
                }
            },
        },
    }


def test_v2_preview_route_returns_pipeline_payload(tmp_path, monkeypatch) -> None:
    service = NarrativeV2PreviewService(ledger_path=tmp_path / "api-preview-ledger.jsonl")
    monkeypatch.setattr(recommendation_v2_route, "service_factory", lambda: service)

    app = FastAPI()
    app.include_router(recommendation_v2_route.router)
    client = TestClient(app)

    response = client.post("/api/v2/recommendation/preview", json=_preview_payload())

    assert response.status_code == 200

    body = response.json()
    assert body["case_id"] == "case-001"
    assert body["state"]["stage"] == "middle"
    assert len(body["rule_checks"]) == 5
    assert body["recommendations"]
    assert body["recommendations"][0]["action"]["action"] == body["validation"]["top_action"]
    assert body["validation"]["case_id"] == "case-001"
    assert body["validation"]["top_action"] == "push_conflict"
    assert body["evaluation_summary"]["count"] == len(body["recommendations"])

    entries = service.validation_service.read_ledger(path=tmp_path / "api-preview-ledger.jsonl")
    assert len(entries) == 1
    assert entries[0].case_id == "case-001"
    assert entries[0].source == "preview"


def test_v2_preview_route_keeps_success_when_ledger_write_fails(tmp_path, monkeypatch) -> None:
    blocked_ledger_path = tmp_path / "api-preview-ledger-dir"
    blocked_ledger_path.mkdir(parents=True, exist_ok=True)
    service = NarrativeV2PreviewService(ledger_path=blocked_ledger_path)
    monkeypatch.setattr(recommendation_v2_route, "service_factory", lambda: service)

    app = FastAPI()
    app.include_router(recommendation_v2_route.router)
    client = TestClient(app)

    response = client.post("/api/v2/recommendation/preview", json=_preview_payload(case_id="case-002"))

    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == "case-002"
    assert body["recommendations"]
    assert body["decision"]["selected_action"] == body["validation"]["top_action"]
    assert "ledger_warning" in body
