from __future__ import annotations

from fastapi.testclient import TestClient

import backend.app.api.routes.workbench_v2 as workbench_v2_route
from backend.app.main import create_app
from backend.app.services.narrative.history_service import HistoryService
from backend.app.services.narrative_v2.workbench_service import NarrativeV2WorkbenchService


def test_v2_workbench_context_route_returns_live_backend_context(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        workbench_v2_route,
        "service",
        NarrativeV2WorkbenchService(
            history_service=HistoryService(),
            imported_context_path=tmp_path / "missing-workbench-contexts.json",
        ),
    )
    client = TestClient(create_app())

    response = client.get("/api/v2/workbench/contexts")

    assert response.status_code == 200

    body = response.json()
    assert body["contexts"]
    assert body["contexts"][0]["state"]["chapter_index"] == 18
    assert body["contexts"][0]["state"]["stage"] == "middle"
    assert "history" in body["contexts"][0]["summary"].lower()
