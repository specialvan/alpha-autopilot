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
    assert result["decision"]["selected_action"] == result["recommendations"][0]["action"]["action"]
    assert result["decision"]["selected_score"] == result["recommendations"][0]["score"]
    assert result["decision"]["accepted_actions"] == result["validation"]["accepted_actions"]
    assert result["decision"]["blocked_actions"] == result["validation"]["blocked_actions"]
    assert result["decision"]["prerequisite_missing_actions"] == ["close_sideplot"]
    assert result["decision"]["validation_case_id"] == result["validation"]["case_id"]
    assert result["decision"]["rule_status_summary"] == {
        "legal_count": 3,
        "blocked_count": 1,
        "prerequisite_missing_count": 1,
    }
    assert result["decision"]["constraint_hint"] == "mixed_constraints"
    assert result["decision"]["quality_hint"] == "review"
    assert result["decision"]["retention_driver"]["target_function"] == "reader-retention"
    assert result["decision"]["retention_driver"]["selected_final_score"] == result["decision"]["selected_score"]
    assert result["evaluation_summary"]["top_action"] == result["recommendations"][0]["action"]["action"]
    assert result["evaluation_summary"]["top_action"] == result["decision"]["selected_action"]
    assert result["evaluation_summary"]["top_score"] == result["decision"]["selected_score"]
    assert len(entries) == 1
    assert entries[0].case_id == "case-100"
    assert entries[0].source == "preview"
    assert entries[0].top_action == result["validation"]["top_action"]


def test_v2_preview_service_keeps_preview_available_when_ledger_write_fails(tmp_path) -> None:
    blocked_path = tmp_path / "preview-ledger-dir"
    blocked_path.mkdir(parents=True, exist_ok=True)
    service = NarrativeV2PreviewService(ledger_path=blocked_path)
    payload = NarrativeV2PreviewRequest.model_validate(
        {
            "case_id": "case-101",
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

    assert result["rule_checks"]
    assert result["recommendations"]
    assert result["decision"]["selected_action"]
    assert "ledger_warning" in result


def test_v2_preview_service_injects_plot_unit_scaffold_into_system_prompt_constraints(tmp_path) -> None:
    service = NarrativeV2PreviewService(ledger_path=tmp_path / "preview-ledger.jsonl")
    payload = NarrativeV2PreviewRequest.model_validate(
        {
            "case_id": "case-plot-unit-001",
            "state": {
                "chapter_index": 8,
                "stage": "middle",
                "mainline_progress": 0.45,
                "sideplot_progress": 0.22,
                "conflict_intensity": 0.64,
                "emotional_temperature": 0.58,
                "pacing_speed": 0.50,
                "foreshadowing_load": 0.38,
                "payoff_pressure": 0.32,
                "tags": ["power"],
                "characters": {},
            },
            "plot_unit_scaffold": {
                "encounter_event": "A public accusation breaks the truce.",
                "desire_goal": "Protect the ally and preserve legitimacy.",
                "obstacle": "Evidence appears to confirm the accusation.",
                "solution_method": "Expose the manipulated witness ledger.",
                "action_climax": {
                    "node": "The witness retracts and reveals coercion.",
                    "turn_type": "goal_inversion",
                },
                "resolution": "Temporary trust is restored but a deeper enemy is exposed.",
            },
        }
    )

    result = service.build_preview(payload)

    constraints = result.get("system_prompt_constraints")
    assert isinstance(constraints, dict)
    assert "plot_unit_scaffold" in constraints
    assert "system_prompt_paragraph" in constraints
    paragraph = str(constraints["system_prompt_paragraph"])
    assert "Follow this six-step plot scaffold" in paragraph
    assert "turn=goal_inversion" in paragraph


def test_v2_preview_request_turn_type_enum_supports_three_values() -> None:
    base_payload = {
        "case_id": "case-plot-turn-enum",
        "state": {
            "chapter_index": 8,
            "stage": "middle",
            "mainline_progress": 0.45,
            "sideplot_progress": 0.22,
            "conflict_intensity": 0.64,
            "emotional_temperature": 0.58,
            "pacing_speed": 0.50,
            "foreshadowing_load": 0.38,
            "payoff_pressure": 0.32,
            "tags": ["power"],
            "characters": {},
        },
        "plot_unit_scaffold": {
            "encounter_event": "trigger",
            "desire_goal": "goal",
            "obstacle": "obstacle",
            "solution_method": "method",
            "action_climax": {"node": "node", "turn_type": "obstacle_shift"},
            "resolution": "resolution",
        },
    }

    turn_types = {"obstacle_shift", "goal_inversion", "character_contrast"}
    for turn_type in turn_types:
        payload = {
            **base_payload,
            "plot_unit_scaffold": {
                **base_payload["plot_unit_scaffold"],
                "action_climax": {"node": "node", "turn_type": turn_type},
            },
        }
        model = NarrativeV2PreviewRequest.model_validate(payload)
        assert model.plot_unit_scaffold is not None
        assert model.plot_unit_scaffold.action_climax.turn_type.value == turn_type
