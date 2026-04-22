from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_v2_preview_route_is_wired_into_main_app() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v2/recommendation/preview",
        json={
            "case_id": "wired-001",
            "state": {
                "chapter_index": 8,
                "stage": "middle",
                "mainline_progress": 0.45,
                "sideplot_progress": 0.25,
                "conflict_intensity": 0.64,
                "emotional_temperature": 0.57,
                "pacing_speed": 0.5,
                "foreshadowing_load": 0.37,
                "payoff_pressure": 0.33,
                "tags": ["power"],
                "characters": {},
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["case_id"] == "wired-001"
