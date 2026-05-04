from __future__ import annotations

from .flavor import (
    build_external_move_envelope,
    build_hook_seed,
    build_risk_if_exposed,
    build_state_shift_emphasis,
    render_flavor,
)
from .knife_library import build_compatibility_graph, build_default_knife_library, get_knife_by_id
from .ledger import apply_state_shift
from .schemas import (
    BuildVillainFeedbackInput,
    BuildVillainFeedbackOutput,
    DecisionLayer,
    ExplanationLayer,
    FutureHook,
    StateLedgerShift,
    VillainFeedbackPacket,
)
from .selection import select_knives


def build_villain_feedback(
    payload: BuildVillainFeedbackInput | dict[str, object],
) -> BuildVillainFeedbackOutput:
    request = (
        payload
        if isinstance(payload, BuildVillainFeedbackInput)
        else BuildVillainFeedbackInput.model_validate(payload)
    )
    library = request.knife_library or build_default_knife_library()
    compatibility_graph = build_compatibility_graph()

    selection_result = select_knives(
        request.villain,
        request.target,
        request.scene,
        library=library,
        compatibility_graph=compatibility_graph,
    )

    reference_knife_id = selection_result.decision.primary_knife_id or request.villain.preferred_knives[0]
    reference_knife = get_knife_by_id(reference_knife_id, library=library)
    flavor = render_flavor(request.villain, reference_knife, request.scene)

    if selection_result.decision.selection_mode == "fallback":
        future_hooks: tuple[FutureHook, ...] = ()
        state_shift = StateLedgerShift()
    else:
        future_hooks = _build_future_hooks(
            knife=reference_knife,
            flavor=flavor,
            villain=request.villain,
            scene=request.scene,
        )
        state_shift = _build_state_shift(
            flavor=flavor,
            future_hooks=future_hooks,
        )

    explanation = _build_explanation(
        decision=selection_result.decision,
        knife=reference_knife,
        flavor=flavor,
        villain=request.villain,
        scene=request.scene,
    )
    risk_if_exposed = build_risk_if_exposed(reference_knife, flavor)
    next_snapshot = apply_state_shift(request.scene.existing_state, state_shift)

    packet = VillainFeedbackPacket(
        villain_id=request.villain.id,
        target_id=request.target.id,
        scene_arena=request.scene.arena,
        decision=selection_result.decision,
        explanation=explanation,
        state_shift=state_shift,
        future_hooks=future_hooks,
        risk_if_exposed=risk_if_exposed,
        flavor_render=flavor,
    )
    return BuildVillainFeedbackOutput(packet=packet, next_snapshot=next_snapshot)


def _build_explanation(
    *,
    decision: DecisionLayer,
    knife,
    flavor,
    villain,
    scene,
) -> ExplanationLayer:
    if decision.selection_mode == "fallback":
        return ExplanationLayer(
            external_move=_build_fallback_external_move(decision, scene),
            inner_drive=f"{villain.private_drive[0]} 仍然主导她的判断，但她选择暂不落刀",
            target_misread="目标误以为场面暂时平稳，却没有意识到反派正在换轨观察",
            why_now=f"当前 {scene.visibility} 场域与 {scene.stake} 利害不支持稳定出刀",
            why_this_choice=decision.fallback_reason or "没有足够稳的刀法可用，只能先收势",
            why_this_villain_style=(
                f"她依然维持 {villain.public_mask[0]} 的外壳，只是把主动权转成延迟控制"
            ),
        )

    primary_signal = decision.selected_signals[0]
    return ExplanationLayer(
        external_move=build_external_move_envelope(knife, flavor),
        inner_drive=f"{villain.private_drive[0]} 与 {villain.private_drive[-1]} 共同驱动了这次选择",
        target_misread=_describe_target_misread(flavor),
        why_now=f"{scene.visibility} 场域下的 {scene.stake} 利害让 {knife.name} 的窗口已经打开",
        why_this_choice="; ".join(primary_signal.reasons),
        why_this_villain_style=(
            f"{villain.public_mask[0]} 的表层姿态与 {flavor.delivery_surface} 的投放方式保持一致"
        ),
    )


def _build_future_hooks(*, knife, flavor, villain, scene) -> tuple[FutureHook, ...]:
    hook_id = f"{villain.id}-{knife.id}-{flavor.hook_style}-{scene.current_phase}"
    recovery_condition = (
        "等到见证者重新解释这次互动，或目标试图追索体面账时回收"
        if scene.visibility == "public"
        else "等到目标重新确认依赖边界时回收"
    )
    return (
        FutureHook(
            id=hook_id,
            source_knife_id=knife.id,
            description=build_hook_seed(knife, flavor),
            payoff_window=_resolve_payoff_window(villain.time_horizon),
            recovery_condition=recovery_condition,
        ),
    )


def _build_state_shift(*, flavor, future_hooks: tuple[FutureHook, ...]) -> StateLedgerShift:
    emphasis = build_state_shift_emphasis(flavor)
    focus = max(emphasis, key=emphasis.get)

    relationship: dict[str, object] = {}
    narrative: dict[str, object] = {}
    psychological: dict[str, object] = {}
    hook: dict[str, object] = {}

    if focus == "relationship":
        relationship = {"debt_delta": 2, "dependency_delta": 1}
        if flavor.pressure_channel == "guilt_pull":
            relationship["trust_delta"] = -1
    elif focus == "narrative":
        narrative = {"explanation_control_delta": 2, "witness_alignment_delta": 1}
        if flavor.pressure_channel in {"self_image", "status_gap", "witness_pressure"}:
            narrative["reputation_delta"] = 1
    elif focus == "psychological":
        psychological = {"identity_destabilization_delta": 2, "shame_load_delta": 1}
        if flavor.pressure_channel == "memory_reframe":
            psychological["wound_activation_delta"] = 1
    else:
        hook = {"planted_hooks": future_hooks}
        relationship = {"debt_delta": 1}

    if future_hooks and focus != "hook":
        hook = {"planted_hooks": future_hooks}

    return StateLedgerShift(
        relationship=relationship,
        narrative=narrative,
        psychological=psychological,
        hook=hook,
    )


def _build_fallback_external_move(decision: DecisionLayer, scene) -> str:
    action = decision.fallback_action or "gather_information"
    if action == "reduce_exposure":
        return f"她收回公开动作，只留下最难被追责的 {scene.stake} 姿态。"
    if action == "defer_to_public_mask":
        return "她暂时把动作退回到最安全的公共面具，不给对手抓住明证。"
    if action == "hold_position":
        return "她维持现位不再加码，等待更稳的切口出现。"
    return "她先不落刀，只把场面导向更有利的信息收集位置。"


def _describe_target_misread(flavor) -> str:
    mapping = {
        "self_image": "目标误把体面维护当成了自己的主动选择",
        "witness_pressure": "目标误以为旁观者只是在看热闹，而不是在参与裁决",
        "guilt_pull": "目标误把内疚当成了必须立即偿还的责任",
        "status_gap": "目标误以为让一步就能换来真正的平衡",
        "dependency_pull": "目标误以为被安抚就是被理解",
        "memory_reframe": "目标误以为旧伤被理解，其实只是被重新定价",
    }
    return mapping[flavor.pressure_channel]


def _resolve_payoff_window(time_horizon: str) -> str:
    mapping = {
        "short": "near",
        "mid": "mid",
        "long": "long",
    }
    return mapping[time_horizon]
