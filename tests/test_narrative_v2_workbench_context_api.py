from __future__ import annotations

import json

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
