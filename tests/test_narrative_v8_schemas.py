from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.services.narrative_v8.schemas import (
    DecisionLayer,
    FlavorRender,
    FutureHook,
    HookLedgerShift,
    HookLedgerState,
    LedgerSnapshot,
    NarrativeLedgerShift,
    NarrativeLedgerState,
    PsychologicalLedgerShift,
    PsychologicalLedgerState,
    RelationshipLedgerShift,
    RelationshipLedgerState,
    SceneContext,
    StateLedgerShift,
    VillainFeedbackPacket,
    VillainProfile,
)


def build_flavor_profile() -> dict[str, str]:
    return {
        "temperature": "cold",
        "rituality": "high",
        "sensuality": "low",
        "theatricality": "mid",
        "cruelty_visibility": "hidden",
        "witness_dependence": "public",
        "control_preference": "public_rewrite",
    }


def build_villain_profile_payload() -> dict[str, object]:
    return {
        "id": "villain-luoxue",
        "archetype": "ritual_controller",
        "core_wound": "被师门公开羞辱",
        "core_belief": "必须先定义他人对我的解释权",
        "psychology_literacy": "systematic",
        "preferred_knives": ("self_image_feeding", "courteous_humiliation"),
        "secondary_knives": ("delayed_asking",),
        "forbidden_moves": ("relationship_withdrawal",),
        "public_mask": ("慈悲", "克制"),
        "private_drive": ("解释权", "债务绑定"),
        "time_horizon": "long",
        "blind_spot": "高估礼法会让人自动屈服",
        "escalation_rule": "一旦目标公开反驳就转向名誉围剿",
        "shame_relation": "weaponized",
        "witness_need": "high",
        "flavor_profile": build_flavor_profile(),
    }


def build_hook_payload() -> dict[str, str]:
    return {
        "id": "hook-public-ledger",
        "source_knife_id": "self_image_feeding",
        "description": "让众人默认目标欠下体面债",
        "payoff_window": "mid",
        "recovery_condition": "目标在更高位面前失态反驳",
    }


def build_snapshot_payload() -> dict[str, object]:
    return {
        "relationship": {
            "trust": 0,
            "debt": 1,
            "dependency": 0,
            "leverage": 1,
        },
        "narrative": {
            "suspicion": 0,
            "reputation": 1,
            "witness_alignment": 1,
            "explanation_control": 1,
        },
        "psychological": {
            "shame_load": 1,
            "wound_activation": 0,
            "protector_trigger": 0,
            "identity_destabilization": 0,
        },
        "hook": {
            "planted_hooks": (build_hook_payload(),),
            "armed_payoffs": (),
            "recovered_hooks": (),
        },
    }


def build_scene_payload(*, visibility: str = "public", observers: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {
        "arena": "chaotang",
        "stake": "reputation",
        "observers": observers,
        "power_topology": (
            {
                "source": "villain-luoxue",
                "target": "target-shenqiao",
                "relation": "ceremonial_seniority",
                "asymmetry": 2,
            },
        ),
        "relationship_distance": "formal",
        "visibility": visibility,
        "time_pressure": "mid",
        "current_phase": "pressure_test",
        "existing_state": build_snapshot_payload(),
    }


def build_selected_signal_payload() -> dict[str, object]:
    return {
        "knife_id": "self_image_feeding",
        "fit_score": 0.88,
        "reasons": ("public witness leverage", "identity anchor exposed"),
    }


def build_rejected_reason_payload() -> dict[str, str]:
    return {
        "knife_id": "relationship_withdrawal",
        "category": "forbidden_move",
        "detail": "villain profile forbids direct withdrawal plays",
    }


def build_state_shift_payload() -> dict[str, object]:
    return {
        "relationship": {
            "trust_delta": -1,
            "debt_delta": 1,
            "dependency_delta": 0,
            "leverage_delta": 1,
        },
        "narrative": {
            "suspicion_delta": 1,
            "reputation_delta": 2,
            "witness_alignment_delta": 1,
            "explanation_control_delta": 2,
        },
        "psychological": {
            "shame_load_delta": 1,
            "wound_activation_delta": 0,
            "protector_trigger_delta": 0,
            "identity_destabilization_delta": 1,
        },
        "hook": {
            "planted_hooks": (build_hook_payload(),),
            "armed_payoffs": (),
            "recovered_hooks": (),
        },
    }


def build_flavor_render_payload() -> dict[str, object]:
    return {
        "tone": "冷静收网",
        "aesthetic": ("礼法", "高台", "欠账"),
        "social_surface": ("克制劝诫", "替你着想"),
        "private_subtext": ("你会在众人面前替我完成自证",),
        "delivery_surface": "courteous_superiority",
        "pressure_channel": "witness_pressure",
        "witness_posture": "perform_for_judge",
        "cost_profile": "reputation_bet",
        "hook_style": "public_record_seed",
        "structural_targets": ("external_move", "future_hooks", "state_shift"),
        "state_shift_focus": "narrative",
    }


def build_packet_payload() -> dict[str, object]:
    return {
        "villain_id": "villain-luoxue",
        "target_id": "target-shenqiao",
        "scene_arena": "chaotang",
        "decision": {
            "selection_mode": "scored_fit",
            "primary_knife_id": "self_image_feeding",
            "secondary_knife_id": None,
            "fallback_action": None,
            "fallback_reason": None,
            "selected_signals": (build_selected_signal_payload(),),
            "rejected_knives": (build_rejected_reason_payload(),),
        },
        "explanation": {
            "external_move": "她借着替对方留体面的名义逼其认错",
            "inner_drive": "要在众目睽睽下夺回解释权",
            "target_misread": "目标以为礼貌就是让步",
            "why_now": "当前权力拓扑允许她借法统放大施压",
            "why_this_choice": "这把刀最能绑定目标的自我形象",
            "why_this_villain_style": "她更擅长把羞耻包装成秩序维护",
        },
        "state_shift": build_state_shift_payload(),
        "future_hooks": (build_hook_payload(),),
        "risk_if_exposed": ("若上位者识破，她会被视为操弄舆论",),
        "flavor_render": build_flavor_render_payload(),
    }


def test_schema_accepts_minimally_valid_villain_profile() -> None:
    profile = VillainProfile(**build_villain_profile_payload())

    assert profile.id == "villain-luoxue"
    assert profile.flavor_profile.temperature == "cold"
    assert len(profile.preferred_knives) == 2


def test_schema_rejects_preferred_and_forbidden_overlap() -> None:
    payload = build_villain_profile_payload()
    payload["forbidden_moves"] = ("self_image_feeding",)

    with pytest.raises(ValidationError):
        VillainProfile(**payload)


def test_schema_rejects_public_scene_without_observers() -> None:
    payload = build_scene_payload(visibility="public", observers=())

    with pytest.raises(ValidationError):
        SceneContext(**payload)


def test_schema_accepts_layered_state_ledger_shift() -> None:
    shift = StateLedgerShift(**build_state_shift_payload())

    assert shift.relationship.debt_delta == 1
    assert shift.hook.planted_hooks[0].source_knife_id == "self_image_feeding"


def test_schema_accepts_structured_villain_feedback_packet() -> None:
    packet = VillainFeedbackPacket(**build_packet_payload())

    assert packet.decision.primary_knife_id == "self_image_feeding"
    assert packet.flavor_render.state_shift_focus == "narrative"
    assert "state_shift" in packet.flavor_render.structural_targets


def test_schema_rejects_flat_old_style_packet_payload() -> None:
    with pytest.raises(ValidationError):
        VillainFeedbackPacket(
            villain_id="villain-luoxue",
            target_id="target-shenqiao",
            scene_arena="chaotang",
            external_move="旧结构只有一句叙述",
            state_delta={"trust_delta": 1},
            selected_knife_id="self_image_feeding",
        )


def test_schema_rejects_fallback_packet_that_pretends_to_have_a_selected_knife() -> None:
    with pytest.raises(ValidationError):
        DecisionLayer(
            selection_mode="fallback",
            primary_knife_id="self_image_feeding",
            fallback_action="hold_position",
            fallback_reason="no viable knife survived hard filters",
            selected_signals=(build_selected_signal_payload(),),
            rejected_knives=(build_rejected_reason_payload(),),
        )


def test_schema_rejects_flavor_render_without_enough_structural_targets() -> None:
    payload = build_flavor_render_payload()
    payload["structural_targets"] = ("external_move",)

    with pytest.raises(ValidationError):
        FlavorRender(**payload)
