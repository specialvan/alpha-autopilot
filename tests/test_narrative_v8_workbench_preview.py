from __future__ import annotations

from backend.app.services.narrative_v8.workbench_bridge import build_v8_workbench_preview


def build_context(
    *,
    context_id: str,
    stage: str = "middle",
    tags: list[str] | None = None,
    profile: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "id": context_id,
        "chapterNumber": 12,
        "title": "court wind enters the inner chamber",
        "stage": stage,
        "summary": "fixture context for V8 workbench preview",
        "state": {
            "chapter_index": 12,
            "stage": stage,
            "mainline_progress": 0.46,
            "sideplot_progress": 0.21,
            "conflict_intensity": 0.72,
            "emotional_temperature": 0.58,
            "pacing_speed": 0.61,
            "foreshadowing_load": 0.33,
            "payoff_pressure": 0.37,
            "characters": {},
            "tags": tags or ["court", "pressure"],
        },
        "v8_preview_profile": profile or {},
    }


def test_v8_workbench_preview_builds_public_networked_upgrade_path() -> None:
    preview = build_v8_workbench_preview(
        build_context(
            context_id="context-public-network",
            profile={
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "suspicious",
                "observer_roles": ["judge", "witness", "transmitter"],
            },
        )
    )

    assert preview["enabled"] is True
    assert preview["decision_mode"] == "scored_fit"
    assert preview["transition"]["next_state"] == "upgraded"
    assert preview["transition"]["upgrade_path"] == "more_systemic"
    assert preview["v8_input_profile"]["observer_roles"] == ["judge", "witness", "transmitter"]


def test_v8_workbench_preview_builds_private_recovery_fallback_path() -> None:
    preview = build_v8_workbench_preview(
        build_context(
            context_id="context-private-fallback",
            stage="late",
            tags=["bond", "private"],
            profile={
                "visibility": "private",
                "arena": "qingzhai",
                "stake": "bond",
                "current_control_state": "suspicious",
                "preferred_knives": ["courteous_humiliation"],
                "secondary_knives": [],
                "target_weak_points": ["certainty"],
                "target_witness_sensitivity": "low",
                "target_core_need": "distance",
                "target_social_priorities": [],
                "target_identity_anchor": "模糊",
            },
        )
    )

    assert preview["enabled"] is True
    assert preview["decision_mode"] == "fallback"
    assert preview["fallback_action"] == "hold_position"
    assert preview["transition"]["next_state"] == "repair_attempt"
    assert preview["next_control_state"] == "repair_attempt"


def test_v8_workbench_preview_can_disable_output_for_rollback_gate() -> None:
    preview = build_v8_workbench_preview(
        build_context(context_id="context-disabled"),
        preview_enabled=False,
    )

    assert preview["enabled"] is False
    assert preview["fallback_reason"] == "v8-preview-disabled"
    assert preview["transition"] is None
