from __future__ import annotations

import pytest

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
        "summary": "V8 benchmark matrix fixture",
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


@pytest.mark.parametrize(
    ("scenario_name", "stage", "tags", "profile", "expected"),
    (
        (
            "public_network_upgrade",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "suspicious",
                "observer_roles": ["judge", "witness", "transmitter"],
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "upgraded",
                "upgrade_path": "more_systemic",
            },
        ),
        (
            "judge_network_upgrade",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "suspicious",
                "observer_roles": ["judge", "witness"],
                "preferred_knives": ["self_image_feeding"],
                "secondary_knives": [],
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "upgraded",
                "upgrade_path": "outsourced_interpretation",
            },
        ),
        (
            "low_exposure_upgrade",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "ziyuan",
                "stake": "resource",
                "current_control_state": "suspicious",
                "control_preference": "resource_cut",
                "observer_roles": ["witness"],
                "preferred_knives": ["delayed_asking"],
                "secondary_knives": [],
                "target_weak_points": ["debt_sensitive"],
                "target_witness_sensitivity": "mid",
                "target_core_need": "distance",
                "target_social_priorities": ["status"],
                "target_identity_anchor": "stable identity",
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "upgraded",
                "upgrade_path": "more_hidden",
            },
        ),
        (
            "public_trace_exposure",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "harmless",
                "observer_roles": ["judge", "witness"],
                "preferred_knives": ["self_image_feeding"],
                "secondary_knives": [],
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "suspicious",
                "upgrade_path": None,
            },
        ),
        (
            "private_fallback_repair",
            "late",
            ["bond", "private"],
            {
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
                "target_identity_anchor": "blurred",
            },
            {
                "decision_mode": "fallback",
                "next_state": "repair_attempt",
                "upgrade_path": None,
            },
        ),
        (
            "public_fallback_collapse",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "distrusted",
                "control_preference": "public_rewrite",
                "observer_roles": ["transmitter"],
                "preferred_knives": ["courteous_humiliation"],
                "secondary_knives": [],
                "target_weak_points": ["certainty"],
                "target_witness_sensitivity": "low",
                "target_core_need": "distance",
                "target_social_priorities": [],
                "target_identity_anchor": "blurred",
            },
            {
                "decision_mode": "fallback",
                "next_state": "collapsed",
                "upgrade_path": None,
            },
        ),
        (
            "distrusted_hardening",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "distrusted",
                "observer_roles": ["judge", "witness"],
                "preferred_knives": ["self_image_feeding"],
                "secondary_knives": [],
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "hardened",
                "upgrade_path": None,
            },
        ),
        (
            "repair_attempt_restoration",
            "middle",
            ["court", "pressure"],
            {
                "visibility": "public",
                "arena": "chaotang",
                "stake": "reputation",
                "current_control_state": "repair_attempt",
                "observer_roles": ["judge", "witness"],
                "preferred_knives": ["self_image_feeding"],
                "secondary_knives": [],
            },
            {
                "decision_mode": "scored_fit",
                "next_state": "partially_restored",
                "upgrade_path": None,
            },
        ),
    ),
)
def test_v8_workbench_benchmark_matrix_covers_control_surface_paths(
    scenario_name: str,
    stage: str,
    tags: list[str],
    profile: dict[str, object],
    expected: dict[str, object],
) -> None:
    preview = build_v8_workbench_preview(
        build_context(
            context_id=f"benchmark-{scenario_name}",
            stage=stage,
            tags=tags,
            profile=profile,
        )
    )

    assert preview["enabled"] is True
    assert preview["decision_mode"] == expected["decision_mode"]
    assert preview["transition"]["next_state"] == expected["next_state"]
    assert preview["transition"]["upgrade_path"] == expected["upgrade_path"]
    assert preview["next_control_state"] == expected["next_state"]
