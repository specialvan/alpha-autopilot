from __future__ import annotations

from unittest.mock import patch

from backend.app.services.narrative_v8.controller import build_villain_feedback
from backend.app.services.narrative_v8.knife_library import build_default_knife_library
from backend.app.services.narrative_v8.schemas import BuildVillainFeedbackInput


def build_input() -> BuildVillainFeedbackInput:
    return BuildVillainFeedbackInput(
        villain={
            "id": "villain-controller",
            "archetype": "ritual-controller",
            "core_wound": "曾在公开场合被夺走解释权",
            "core_belief": "只要先控制叙事，就能控制关系",
            "psychology_literacy": "systematic",
            "preferred_knives": ("self_image_feeding", "courteous_humiliation"),
            "secondary_knives": ("baited_concession",),
            "forbidden_moves": ("relationship_withdrawal",),
            "public_mask": ("克制", "体贴"),
            "private_drive": ("解释权", "绑定"),
            "time_horizon": "long",
            "blind_spot": "高估礼法外壳的稳定性",
            "escalation_rule": "遭遇反抗就升级到公开秩序控制",
            "shame_relation": "weaponized",
            "witness_need": "high",
            "flavor_profile": {
                "temperature": "cold",
                "rituality": "high",
                "sensuality": "low",
                "theatricality": "mid",
                "cruelty_visibility": "hidden",
                "witness_dependence": "public",
                "control_preference": "public_rewrite",
            },
        },
        target={
            "id": "target-controller",
            "self_image": "守礼而不愿失态的人",
            "core_need": "connection",
            "core_fear": "在众人面前丢掉体面",
            "weak_points": ("protector_complex", "debt_sensitive", "old_wound"),
            "defense_style": "ceremonial",
            "resistance_style": "measured",
            "witness_sensitivity": "high",
            "identity_anchor": "必须维护长者形象",
            "social_priorities": ("status",),
        },
        scene={
            "arena": "chaotang",
            "stake": "reputation",
            "observers": (
                {
                    "id": "observer-judge",
                    "role": "judge",
                    "alignment": "unknown",
                    "importance": 3,
                    "visibility_impact": 3,
                },
                {
                    "id": "observer-witness",
                    "role": "witness",
                    "alignment": "mixed",
                    "importance": 2,
                    "visibility_impact": 2,
                },
            ),
            "power_topology": (
                {
                    "source": "villain-controller",
                    "target": "target-controller",
                    "relation": "ritual_seniority",
                    "asymmetry": 2,
                },
            ),
            "relationship_distance": "formal",
            "visibility": "public",
            "time_pressure": "mid",
            "current_phase": "pressure_test",
            "existing_state": {},
        },
        knife_library=build_default_knife_library(),
    )


def test_controller_returns_structured_packet_plus_next_snapshot() -> None:
    result = build_villain_feedback(build_input())

    assert result.packet.villain_id == "villain-controller"
    assert result.packet.target_id == "target-controller"
    assert result.next_snapshot.narrative.explanation_control >= 0


def test_controller_emits_decision_explanation_state_shift_and_future_hooks_as_separate_layers() -> None:
    result = build_villain_feedback(build_input())

    assert result.packet.decision.selection_mode == "scored_fit"
    assert result.packet.explanation.external_move
    assert result.packet.state_shift.narrative.explanation_control_delta >= 0
    assert result.packet.future_hooks


def test_controller_carries_rejected_knife_reasons_forward_from_selection_layer() -> None:
    result = build_villain_feedback(build_input())

    assert any(
        reason.knife_id == "relationship_withdrawal" and reason.category == "forbidden_move"
        for reason in result.packet.decision.rejected_knives
    )


def test_controller_produces_stable_outputs_for_same_deterministic_input() -> None:
    first = build_villain_feedback(build_input())
    second = build_villain_feedback(build_input())

    assert first.model_dump() == second.model_dump()


def test_controller_delegates_hard_filtering_to_selection_helpers() -> None:
    with patch("backend.app.services.narrative_v8.controller.select_knives", wraps=build_villain_feedback.__globals__["select_knives"]) as spy:
        build_villain_feedback(build_input())

    assert spy.call_count == 1


def test_controller_delegates_state_application_to_ledger_helpers() -> None:
    with patch("backend.app.services.narrative_v8.controller.apply_state_shift", wraps=build_villain_feedback.__globals__["apply_state_shift"]) as spy:
        build_villain_feedback(build_input())

    assert spy.call_count == 1
