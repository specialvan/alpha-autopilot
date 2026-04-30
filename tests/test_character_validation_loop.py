from __future__ import annotations

from copy import deepcopy

from backend.app.services.narrative_v4.bridge import build_v4_bridge_payload_with_memory
from backend.app.services.narrative_v4.character_validation import (
    CharacterValidationIssue,
    CharacterValidationIssueList,
    run_character_validation_loop,
)
from backend.app.services.narrative_v4.memory_store import V4MemoryStore


def _validation_input_characters() -> list[dict[str, object]]:
    return [
        {
            "id": "hero",
            "status": 0.2,
            "knowledge": 0.4,
            "emotion": 0.7,
            "interest_conflict": 0.6,
            "control": 0.5,
            "dependency": 0.3,
            "trust": 0.4,
            "impulsiveness": 0.8,
            "calmness": 0.9,
            "resilience": 0.7,
            "directness": 0.9,
            "pragmatism": 0.7,
            "idealism": 0.2,
            "assertiveness": 0.8,
            "avoidance": 0.1,
            "self_protection": 0.4,
            "sacrifice_tendency": 0.3,
            "risk_appetite": 0.8,
            "function_type": "disguise",
            "emotion_slider_map": {
                "baseline": {"stress_baseline": 8.0},
                "scene_overrides": {},
            },
        }
    ]


def test_character_validation_loop_serializes_issue_list_and_modifies_only_issue_fields() -> None:
    original = _validation_input_characters()
    baseline = deepcopy(original)
    fixed, log = run_character_validation_loop(original, enabled=True)

    assert log["enabled"] is True
    assert log["issue_count"] >= 1
    assert log["llm_calls"]["targeted_fix"] == 1
    assert log["inspector_mode"] == "heuristic"
    assert log["fixer_mode"] == "deterministic_patch"
    assert log["llm_mode"] == "simulated"
    issue_list = log["issue_list"]
    assert isinstance(issue_list, dict)
    assert isinstance(issue_list["issues"], list)

    assert fixed[0]["surface_relation"] == "unknown"
    assert fixed[0]["actual_relation"] == "unknown"
    assert fixed[0]["calmness"] == 0.65
    # Ensure unrelated fields remain unchanged.
    assert fixed[0]["status"] == baseline[0]["status"]
    assert fixed[0]["knowledge"] == baseline[0]["knowledge"]
    assert fixed[0]["risk_appetite"] == baseline[0]["risk_appetite"]


def test_character_validation_loop_skips_targeted_fix_when_issue_list_empty() -> None:
    characters = [
        {
            "id": "hero",
            "status": 0.2,
            "knowledge": 0.4,
            "emotion": 0.7,
            "interest_conflict": 0.6,
            "control": 0.5,
            "dependency": 0.3,
            "trust": 0.4,
            "impulsiveness": 0.8,
            "calmness": 0.5,
            "resilience": 0.7,
            "directness": 0.9,
            "pragmatism": 0.7,
            "idealism": 0.2,
            "assertiveness": 0.8,
            "avoidance": 0.1,
            "self_protection": 0.4,
            "sacrifice_tendency": 0.3,
            "risk_appetite": 0.8,
            "function_type": "anchor",
        }
    ]
    fixed, log = run_character_validation_loop(characters, enabled=True)

    assert log["issue_count"] == 0
    assert log["llm_calls"]["targeted_fix"] == 0
    assert log["fixer_mode"] == "skipped"
    assert log["llm_mode"] == "simulated"
    assert fixed == characters


def test_character_validation_loop_default_enabled_in_v4_bridge_and_runtime_logged(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-validation-loop",
            "chapter_index": 18,
            "v4_enabled": True,
            "characters": _validation_input_characters(),
            "pressure_items": [{"type": "survival", "intensity": 0.8}],
        },
        memory_store=memory_store,
        context_id="ctx-validation-loop",
        history_window=20,
    )

    validation_log = payload["character_validation"]
    assert validation_log["enabled"] is True
    assert validation_log["llm_calls"]["generate"] == 1
    assert isinstance(validation_log["issue_list"]["issues"], list)
    assert payload["memory_summary"]["character_validation_elapsed_ms"] >= 0


def test_character_validation_loop_bypasses_when_v4_disabled(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-validation-disabled",
            "chapter_index": 18,
            "v4_enabled": False,
            "characters": _validation_input_characters(),
            "pressure_items": [{"type": "survival", "intensity": 0.8}],
        },
        memory_store=memory_store,
        context_id="ctx-validation-disabled",
        history_window=20,
    )

    validation_log = payload["character_validation"]
    assert validation_log["enabled"] is False
    assert validation_log["skipped"] is True
    assert validation_log["llm_calls"]["generate"] == 0
    assert validation_log["inspector_mode"] == "heuristic"
    assert validation_log["fixer_mode"] == "skipped"
    assert validation_log["llm_mode"] == "simulated"


def test_character_validation_loop_supports_external_inspector_and_fixer_hooks() -> None:
    characters = _validation_input_characters()

    def external_inspector(
        generated: list[dict[str, object]],
    ) -> CharacterValidationIssueList:
        assert len(generated) == 1
        return CharacterValidationIssueList(
            issues=[
                CharacterValidationIssue(
                    field_path="0.surface_relation",
                    description="external check suggests explicit surface relation",
                    suggested_value="ally",
                ),
            ],
        )

    def external_fixer(
        generated: list[dict[str, object]],
        issue_list: CharacterValidationIssueList,
    ) -> list[dict[str, object]]:
        fixed = deepcopy(generated)
        for issue in issue_list.issues:
            if issue.field_path == "0.surface_relation":
                fixed[0]["surface_relation"] = issue.suggested_value
        return fixed

    fixed, log = run_character_validation_loop(
        characters,
        enabled=True,
        inspector=external_inspector,
        fixer=external_fixer,
    )

    assert fixed[0]["surface_relation"] == "ally"
    assert log["inspector_mode"] == "external_judge"
    assert log["fixer_mode"] == "external_fixer"
    assert log["llm_mode"] == "external"


def test_bridge_supports_external_character_validation_mode_with_injected_hooks(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )

    def external_inspector(
        generated: list[dict[str, object]],
    ) -> CharacterValidationIssueList:
        return CharacterValidationIssueList(
            issues=[
                CharacterValidationIssue(
                    field_path="0.surface_relation",
                    description="inject external correction",
                    suggested_value="mentor",
                ),
            ],
        )

    def external_fixer(
        generated: list[dict[str, object]],
        issue_list: CharacterValidationIssueList,
    ) -> list[dict[str, object]]:
        fixed = deepcopy(generated)
        for issue in issue_list.issues:
            if issue.field_path == "0.surface_relation":
                fixed[0]["surface_relation"] = issue.suggested_value
        return fixed

    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-validation-external",
            "chapter_index": 18,
            "v4_enabled": True,
            "character_validation_mode": "external",
            "_character_validation_inspector": external_inspector,
            "_character_validation_fixer": external_fixer,
            "characters": _validation_input_characters(),
            "pressure_items": [{"type": "survival", "intensity": 0.8}],
        },
        memory_store=memory_store,
        context_id="ctx-validation-external",
        history_window=20,
    )

    validation_log = payload["character_validation"]
    assert validation_log["inspector_mode"] == "external_judge"
    assert validation_log["fixer_mode"] == "external_fixer"
    assert validation_log["llm_mode"] == "external"
    assert validation_log["mode_requested"] == "external"
    assert validation_log["mode_effective"] == "external"
    summary = payload["memory_summary"]
    assert summary["character_validation_mode_requested"] == "external"
    assert summary["character_validation_mode_effective"] == "external"
