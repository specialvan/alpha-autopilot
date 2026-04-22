from __future__ import annotations

from fastapi.testclient import TestClient

from backend_app import app


def test_v2_preview_route_is_available_on_legacy_backend_app() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v2/recommendation/preview",
        json={
            "case_id": "legacy-v2-001",
            "state": {
                "chapter_index": 9,
                "stage": "middle",
                "mainline_progress": 0.43,
                "sideplot_progress": 0.23,
                "conflict_intensity": 0.62,
                "emotional_temperature": 0.57,
                "pacing_speed": 0.5,
                "foreshadowing_load": 0.35,
                "payoff_pressure": 0.31,
                "tags": ["power"],
                "characters": {},
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["case_id"] == "legacy-v2-001"
