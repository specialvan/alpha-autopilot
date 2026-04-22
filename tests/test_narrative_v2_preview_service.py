from __future__ import annotations

from backend.app.services.narrative_v2.preview_service import NarrativeV2PreviewService
from backend.app.services.narrative_v2.schemas import NarrativeV2PreviewRequest


def test_v2_preview_service_writes_validation_record_to_ledger(tmp_path) -> None:
    service = NarrativeV2PreviewService(ledger_path=tmp_path / "preview-ledger.jsonl")
    payload = NarrativeV2PreviewRequest.model_validate(
        {
            "case_id": "case-100",
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
    )

    result = service.build_preview(payload)
    entries = service.validation_service.read_ledger(path=tmp_path / "preview-ledger.jsonl")

    assert result["rule_checks"]
    assert result["recommendations"]
    assert result["evaluation_summary"]["top_action"] == result["recommendations"][0]["action"]["action"]
    assert len(entries) == 1
    assert entries[0].case_id == "case-100"
    assert entries[0].source == "preview"
    assert entries[0].top_action == result["validation"]["top_action"]
