from __future__ import annotations

import json
from pathlib import Path

from backend.app.services.narrative.history_service import HistoryService
from backend.app.services.narrative_v2.imported_contexts import (
    build_workbench_contexts_from_plotpilot_report,
)
from backend.app.services.narrative_v2.workbench_service import NarrativeV2WorkbenchService


def test_build_workbench_contexts_from_plotpilot_report_creates_stageful_contexts() -> None:
    payload = {
        "model": "gpt-5.4",
        "results": [
            {
                "chapter": 1,
                "title": "black_jade_awakens",
                "success": True,
                "chars": 3354,
                "preview": "A young cultivator escapes into a sword valley.",
            },
            {
                "chapter": 6,
                "title": "secret_realm_opening",
                "success": True,
                "chars": 3167,
                "preview": "The prince blocks the road to the black market.",
            },
            {
                "chapter": 10,
                "title": "battle_of_broken_road",
                "success": True,
                "chars": 3265,
                "preview": "The tide tower archive opens under siege.",
            },
        ],
    }

    contexts = build_workbench_contexts_from_plotpilot_report(payload)

    assert [item["chapterNumber"] for item in contexts] == [1, 6, 10]
    assert contexts[0]["stage"] == "opening"
    assert contexts[1]["stage"] == "mid_late"
    assert contexts[2]["stage"] == "late"
    assert "gpt-5.4" in contexts[0]["summary"]


def test_workbench_service_prefers_imported_context_file(tmp_path) -> None:
    imported_path = tmp_path / "workbench_contexts.json"
    imported_path.write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "id": "plotpilot-chapter-01",
                        "chapterNumber": 1,
                        "title": "black_jade_awakens",
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

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )

    result = service.list_contexts()

    assert result["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert result["contexts"][0]["summary"] == "Imported PlotPilot fixture"
