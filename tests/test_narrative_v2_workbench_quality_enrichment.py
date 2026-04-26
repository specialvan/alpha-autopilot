from __future__ import annotations

import json

from backend.app.services.narrative.history_service import HistoryService
from backend.app.services.narrative_v2.workbench_service import NarrativeV2WorkbenchService


def test_workbench_service_enriches_imported_contexts_with_sibling_v3_records(tmp_path) -> None:
    imported_path = tmp_path / "plotpilot" / "workbench_contexts.json"
    imported_path.parent.mkdir(parents=True, exist_ok=True)
    imported_path.write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "id": "plotpilot-chapter-02",
                        "chapterNumber": 2,
                        "title": "guest from medicine valley",
                        "stage": "opening",
                        "summary": "Imported PlotPilot context",
                        "state": {
                            "chapter_index": 2,
                            "stage": "opening",
                            "mainline_progress": 0.19,
                            "sideplot_progress": 0.26,
                            "conflict_intensity": 0.64,
                            "emotional_temperature": 0.56,
                            "pacing_speed": 0.55,
                            "foreshadowing_load": 0.27,
                            "payoff_pressure": 0.27,
                            "characters": {},
                            "tags": ["plotpilot_import", "opening"],
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
        "\n".join(
            [
                json.dumps(
                    {
                        "chapter_number": 2,
                        "title": "guest from medicine valley",
                        "admission": "provisional",
                        "primary_function": "information-reveal",
                        "style_dna": {
                            "pace": "brisk",
                            "dialogue_reliance": "medium",
                            "emotional_directness": "balanced",
                        },
                        "checkpoints": [
                            {
                                "name": "chapter-function-fit",
                                "status": "pass",
                                "evidence": "Primary function resolved cleanly.",
                                "implication": "Stable enough for downstream use.",
                            }
                        ],
                        "workbench_context": {
                            "recommended_stage": "opening",
                            "notes": "Derived from 1 paragraphs with information-reveal.",
                        },
                    },
                    ensure_ascii=False,
                )
            ]
        ),
        encoding="utf-8",
    )

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )

    result = service.list_contexts()

    context = result["contexts"][0]
    assert context["id"] == "plotpilot-chapter-02"
    assert context["primary_function"] == "information-reveal"
    assert context["admission"] == "provisional"
    assert context["style_dna"]["pace"] == "brisk"
    assert context["checkpoints"][0]["status"] == "pass"
    assert "information-reveal" in context["quality_notes"]
    assert context["v4_preview"]["enabled"] is True
    assert context["v4_preview"]["candidate_count"] >= 2
    assert context["v4_preview"]["selected_candidate"]["predicted_action"]
    assert context["v4_preview"]["relationship_graph"]["edge_count"] >= 1


def test_workbench_service_keeps_live_history_context_when_imported_source_missing(tmp_path) -> None:
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=tmp_path / "missing-workbench-contexts.json",
    )

    result = service.list_contexts()

    context = result["contexts"][0]
    assert context["id"] == "live-chapter-18"
    assert context["state"]["chapter_index"] == 18
    assert "history" in context["summary"].lower()
    assert "primary_function" not in context
    assert context["v4_preview"]["enabled"] is True
    assert context["v4_preview"]["candidate_count"] >= 2
    assert context["v4_preview"]["top_candidates"]
    assert context["v4_preview"]["relationship_graph"]["edge_count"] >= 1
    assert context["v4_preview"]["retention_writeback"]["feedback_count"] >= 1


def test_workbench_service_keeps_imported_contexts_when_quality_jsonl_is_corrupted(tmp_path) -> None:
    imported_path = tmp_path / "plotpilot" / "workbench_contexts.json"
    imported_path.parent.mkdir(parents=True, exist_ok=True)
    imported_path.write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "id": "plotpilot-chapter-03",
                        "chapterNumber": 3,
                        "title": "corrupted quality input",
                        "stage": "middle",
                        "summary": "Imported PlotPilot context",
                        "state": {
                            "chapter_index": 3,
                            "stage": "middle",
                            "mainline_progress": 0.33,
                            "sideplot_progress": 0.28,
                            "conflict_intensity": 0.53,
                            "emotional_temperature": 0.49,
                            "pacing_speed": 0.45,
                            "foreshadowing_load": 0.29,
                            "payoff_pressure": 0.26,
                            "characters": {},
                            "tags": ["plotpilot_import", "middle"],
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
    (quality_dir / "reverse_outline_records.jsonl").write_text("{bad json}\n", encoding="utf-8")

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )

    result = service.list_contexts()

    context = result["contexts"][0]
    assert context["id"] == "plotpilot-chapter-03"
    assert context["summary"] == "Imported PlotPilot context"
    assert context["v4_preview"]["enabled"] is True
    assert context["v4_preview"]["candidate_count"] >= 2
    assert context["v4_preview"]["relationship_graph"]["edge_count"] >= 1
