from __future__ import annotations

from typing import Any

from .controller import build_villain_feedback


def build_v8_workbench_preview(
    context: dict[str, object],
    *,
    preview_enabled: bool = True,
) -> dict[str, object]:
    if not preview_enabled or context.get("v8_enabled") is False:
        return {
            "enabled": False,
            "fallback_reason": "v8-preview-disabled",
            "decision_mode": None,
            "primary_knife_id": None,
            "secondary_knife_id": None,
            "fallback_action": None,
            "next_control_state": None,
            "transition": None,
            "explanation": {},
            "future_hooks": [],
            "risk_if_exposed": [],
            "v8_input_profile": {},
        }

    request_payload, input_profile = _build_v8_preview_input(context)
    result = build_villain_feedback(request_payload)
    packet = result.packet
    return {
        "enabled": True,
        "fallback_reason": None,
        "decision_mode": packet.decision.selection_mode,
        "primary_knife_id": packet.decision.primary_knife_id,
        "secondary_knife_id": packet.decision.secondary_knife_id,
        "fallback_action": packet.decision.fallback_action,
        "next_control_state": result.next_control_state,
        "transition": packet.transition.model_dump(),
        "explanation": packet.explanation.model_dump(),
        "future_hooks": [hook.model_dump() for hook in packet.future_hooks],
        "risk_if_exposed": list(packet.risk_if_exposed),
        "v8_input_profile": input_profile,
    }


def _build_v8_preview_input(context: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    state = context.get("state") if isinstance(context.get("state"), dict) else {}
    profile = context.get("v8_preview_profile") if isinstance(context.get("v8_preview_profile"), dict) else {}
    context_id = str(context.get("id", "workbench-context"))
    chapter_number = int(
        context.get("chapterNumber")
        if isinstance(context.get("chapterNumber"), int)
        else state.get("chapter_index", 1)
    )
    stage = str(context.get("stage") or state.get("stage") or "middle")
    tags = _string_list(state.get("tags"))
    visibility = str(profile.get("visibility") or _derive_visibility(stage=stage, tags=tags, state=state))
    arena = str(profile.get("arena") or ("chaotang" if visibility == "public" else "qingzhai"))
    stake = str(profile.get("stake") or ("reputation" if visibility == "public" else "bond"))
    current_control_state = str(
        profile.get("current_control_state")
        or ("suspicious" if _safe_float(state.get("conflict_intensity"), default=0.0) >= 0.5 else "harmless")
    )
    control_preference = str(
        profile.get("control_preference")
        or ("public_rewrite" if visibility == "public" else "private_invasion")
    )
    preferred_knives = tuple(
        _string_list(profile.get("preferred_knives"))
        or _default_preferred_knives(control_preference=control_preference)
    )
    secondary_knives = tuple(
        _string_list(profile.get("secondary_knives"))
        or _default_secondary_knives(control_preference=control_preference)
    )
    observer_roles = _string_list(profile.get("observer_roles")) or (
        ["judge", "witness"] if visibility == "public" else []
    )
    witness_sensitivity = str(
        profile.get("target_witness_sensitivity")
        or ("high" if visibility == "public" else "low")
    )
    target_weak_points = tuple(
        _string_list(profile.get("target_weak_points"))
        or ["protector_complex", "debt_sensitive", "old_wound"]
    )
    target_core_need = str(profile.get("target_core_need") or ("connection" if visibility == "public" else "distance"))
    target_social_priorities = tuple(
        _string_list(profile.get("target_social_priorities"))
        or (["status"] if visibility == "public" else ["bond"])
    )
    target_identity_anchor = str(
        profile.get("target_identity_anchor")
        or ("必须维护长者体面" if visibility == "public" else "不想失去唯一的亲密锚点")
    )
    current_phase = _derive_current_phase(stage)

    request_payload = {
        "villain": {
            "id": f"{context_id}-villain",
            "archetype": "workbench-v8-villain",
            "core_wound": "曾在公开秩序里失去解释权",
            "core_belief": "叙事先于关系",
            "psychology_literacy": "systematic",
            "preferred_knives": preferred_knives,
            "secondary_knives": secondary_knives,
            "forbidden_moves": tuple(_string_list(profile.get("forbidden_moves")) or ["relationship_withdrawal"]),
            "public_mask": ("克制", "体贴"),
            "private_drive": ("解释权", "绑定"),
            "time_horizon": "long",
            "blind_spot": "把礼法外壳等同于稳定",
            "escalation_rule": "公开受挫时升级到更精细的秩序施压",
            "shame_relation": "weaponized",
            "witness_need": str(profile.get("witness_need") or ("high" if visibility == "public" else "low")),
            "flavor_profile": {
                "temperature": str(profile.get("temperature") or ("cold" if visibility == "public" else "soft")),
                "rituality": "high" if visibility == "public" else "mid",
                "sensuality": "low",
                "theatricality": "mid",
                "cruelty_visibility": str(profile.get("cruelty_visibility") or "hidden"),
                "witness_dependence": "public" if visibility == "public" else "private",
                "control_preference": control_preference,
            },
        },
        "target": {
            "id": f"{context_id}-target",
            "self_image": "守礼而不愿失态的人" if visibility == "public" else "需要亲密确认的人",
            "core_need": target_core_need,
            "core_fear": "在众人面前丢掉体面" if visibility == "public" else "被悄无声息地丢下",
            "weak_points": target_weak_points,
            "defense_style": str(profile.get("target_defense_style") or "ceremonial"),
            "resistance_style": str(profile.get("target_resistance_style") or "measured"),
            "witness_sensitivity": witness_sensitivity,
            "identity_anchor": target_identity_anchor,
            "social_priorities": target_social_priorities,
        },
        "scene": {
            "arena": arena,
            "stake": stake,
            "observers": _build_observers(observer_roles),
            "power_topology": (
                {
                    "source": f"{context_id}-villain",
                    "target": f"{context_id}-target",
                    "relation": "ritual_seniority" if visibility == "public" else "emotional_leverage",
                    "asymmetry": 2,
                },
            ),
            "relationship_distance": "formal" if visibility == "public" else "personal",
            "visibility": visibility,
            "time_pressure": str(profile.get("time_pressure") or ("mid" if visibility == "public" else "low")),
            "current_phase": current_phase,
            "current_control_state": current_control_state,
            "existing_state": profile.get("existing_state") or {},
        },
    }
    input_profile = {
        "chapter_number": chapter_number,
        "stage": stage,
        "visibility": visibility,
        "arena": arena,
        "stake": stake,
        "current_control_state": current_control_state,
        "control_preference": control_preference,
        "observer_roles": observer_roles,
        "preferred_knives": list(preferred_knives),
    }
    return request_payload, input_profile


def _derive_visibility(*, stage: str, tags: list[str], state: dict[str, object]) -> str:
    lowered = {item.lower() for item in tags}
    if lowered.intersection({"private", "bond", "intimacy", "healer"}):
        return "private"
    if lowered.intersection({"court", "sect", "public", "reputation", "pressure", "plotpilot"}):
        return "public"
    if _safe_float(state.get("conflict_intensity"), default=0.0) >= 0.6:
        return "public"
    return "public" if stage in {"opening", "middle"} else "private"


def _derive_current_phase(stage: str) -> str:
    mapping = {
        "opening": "probe",
        "middle": "pressure_test",
        "late": "containment",
        "ending": "harvest",
    }
    return mapping.get(stage, "pressure_test")


def _default_preferred_knives(*, control_preference: str) -> tuple[str, ...]:
    mapping = {
        "public_rewrite": ("self_image_feeding", "courteous_humiliation"),
        "private_invasion": ("fake_vulnerability", "gentle_absorption"),
        "resource_cut": ("baited_concession", "delayed_asking"),
        "emotional_absorption": ("gentle_absorption", "fake_vulnerability"),
    }
    return mapping.get(control_preference, ("self_image_feeding", "baited_concession"))


def _default_secondary_knives(*, control_preference: str) -> tuple[str, ...]:
    mapping = {
        "public_rewrite": ("baited_concession",),
        "private_invasion": ("delayed_asking",),
        "resource_cut": ("self_image_feeding",),
        "emotional_absorption": ("delayed_asking",),
    }
    return mapping.get(control_preference, ("delayed_asking",))


def _build_observers(observer_roles: list[str]) -> tuple[dict[str, object], ...]:
    role_defaults: dict[str, tuple[str, int, int]] = {
        "judge": ("unknown", 3, 3),
        "witness": ("mixed", 2, 2),
        "transmitter": ("volatile", 2, 3),
        "buffer": ("mixed", 1, 1),
        "recovery_node": ("target", 2, 1),
    }
    observers: list[dict[str, object]] = []
    for index, role in enumerate(observer_roles, start=1):
        alignment, importance, visibility_impact = role_defaults.get(role, ("unknown", 1, 0))
        observers.append(
            {
                "id": f"observer-{role}-{index}",
                "role": role,
                "alignment": alignment,
                "importance": importance,
                "visibility_impact": visibility_impact,
            }
        )
    return tuple(observers)


def _string_list(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default
