from __future__ import annotations

from .schemas import DecisionLayer, ExplanationLayer, FlavorRender, FutureHook, KnifePrimitive, SceneContext, VillainProfile


PUBLIC_PRESSURE_KNIVES = {"self_image_feeding", "courteous_humiliation", "high_ground_pity"}
PRIVATE_PRESSURE_KNIVES = {"fake_vulnerability", "gentle_absorption", "relationship_withdrawal"}
MEMORY_PRESSURE_KNIVES = {"old_wound_trigger", "memory_reframing"}


def render_flavor(
    villain: VillainProfile,
    knife: KnifePrimitive,
    scene: SceneContext,
) -> FlavorRender:
    delivery_surface = _select_delivery_surface(villain=villain, scene=scene)
    pressure_channel = _select_pressure_channel(villain=villain, knife=knife, scene=scene)
    witness_posture = _select_witness_posture(villain=villain, scene=scene)
    cost_profile = _select_cost_profile(villain=villain, knife=knife, scene=scene)
    hook_style = _select_hook_style(villain=villain, knife=knife)
    state_shift_focus = _select_state_shift_focus(villain=villain, knife=knife, scene=scene)
    structural_targets = _select_structural_targets(
        scene=scene,
        cost_profile=cost_profile,
        hook_style=hook_style,
        state_shift_focus=state_shift_focus,
    )

    return FlavorRender(
        tone=_build_tone(villain=villain, knife=knife, scene=scene),
        aesthetic=_build_aesthetic(villain=villain, knife=knife, scene=scene),
        social_surface=_build_social_surface(villain=villain, scene=scene),
        private_subtext=_build_private_subtext(villain=villain, knife=knife),
        delivery_surface=delivery_surface,
        pressure_channel=pressure_channel,
        witness_posture=witness_posture,
        cost_profile=cost_profile,
        hook_style=hook_style,
        structural_targets=structural_targets,
        state_shift_focus=state_shift_focus,
    )


def build_external_move_envelope(knife: KnifePrimitive, flavor: FlavorRender) -> str:
    surface_map = {
        "private_softness": "她用柔软而不留出口的语气包住真正的索取",
        "public_innocence": "她把动作包装成无害提醒，逼对方自己接住失态",
        "ritual_distance": "她借礼制与距离把操控伪装成秩序维护",
        "courteous_superiority": "她以极度周全的礼貌夺走对方的解释权",
        "fatigued_reserve": "她像是勉强维持克制，实则把节奏压回自己手里",
    }
    return f"{surface_map[flavor.delivery_surface]}；核心刀法是{knife.name}。"


def build_risk_if_exposed(knife: KnifePrimitive, flavor: FlavorRender) -> tuple[str, ...]:
    risks: list[str] = []
    if flavor.cost_profile == "reputation_bet":
        risks.append("一旦有更高位的解释者介入，公开记录会反咬反派本人")
    elif flavor.cost_profile == "high_backfire":
        risks.append("观察者会把这次动作读成赤裸操控而不是体面纠偏")
    elif flavor.cost_profile == "delayed_exposure":
        risks.append("眼下暂时安全，但后续对账时会暴露真实企图")
    else:
        risks.append("当场风险较低，但亲密圈可能在事后回收线索")

    if flavor.witness_posture == "perform_for_judge":
        risks.append("裁决型见证者可能倒向目标并改写现场结论")
    if flavor.hook_style == "debt_seed":
        risks.append("债务型钩子会留下可被清算的账目痕迹")
    if flavor.hook_style == "public_record_seed":
        risks.append("公开记录型钩子会在日后成为反证材料")
    if knife.risks:
        risks.append(f"基础刀法风险：{knife.risks[0]}")

    deduped: list[str] = []
    for risk in risks:
        if risk not in deduped:
            deduped.append(risk)
    return tuple(deduped[:3])


def build_hook_seed(knife: KnifePrimitive, flavor: FlavorRender) -> str:
    hook_map = {
        "debt_seed": "埋下一笔还未到期、但迟早要清算的人情债",
        "shame_seed": "埋下一次以后会反复回响的羞耻记忆",
        "misread_seed": "埋下一次日后才会被意识到的误判",
        "dependency_seed": "埋下一条看似安抚、实则加深依赖的回路",
        "public_record_seed": "埋下一条可在公开场合被翻出的秩序记录",
    }
    return f"{knife.name}之后，{hook_map[flavor.hook_style]}。"


def build_state_shift_emphasis(flavor: FlavorRender) -> dict[str, int]:
    emphasis = {
        "relationship": 1,
        "narrative": 1,
        "psychological": 1,
        "hook": 1,
    }
    emphasis[flavor.state_shift_focus] += 3

    if flavor.pressure_channel in {"self_image", "witness_pressure", "status_gap"}:
        emphasis["narrative"] += 1
    if flavor.pressure_channel in {"dependency_pull", "guilt_pull"}:
        emphasis["relationship"] += 1
    if flavor.pressure_channel == "memory_reframe":
        emphasis["psychological"] += 1
    if flavor.hook_style in {"dependency_seed", "public_record_seed", "debt_seed"}:
        emphasis["hook"] += 1

    return emphasis


def build_future_hooks(
    *,
    knife: KnifePrimitive,
    flavor: FlavorRender,
    villain: VillainProfile,
    scene: SceneContext,
) -> tuple[FutureHook, ...]:
    hook_id = f"{villain.id}-{knife.id}-{flavor.hook_style}-{scene.current_phase}"
    recovery_condition = (
        "wait for witnesses to reinterpret the exchange or for the target to defend face"
        if scene.visibility == "public"
        else "wait for the target to re-enter the dependency boundary"
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


def build_explanation(
    *,
    decision: DecisionLayer,
    knife: KnifePrimitive,
    flavor: FlavorRender,
    villain: VillainProfile,
    scene: SceneContext,
) -> ExplanationLayer:
    if decision.selection_mode == "fallback":
        return ExplanationLayer(
            external_move=_build_fallback_external_move(decision, scene),
            inner_drive=f"{villain.private_drive[0]} still dominates the read, but she chooses not to land a knife yet",
            target_misread="the target mistakes the pause for safety instead of a reset in control posture",
            why_now=f"the current {scene.visibility} arena and {scene.stake} pressure do not support a stable knife",
            why_this_choice=decision.fallback_reason or "no stable knife survived the control gates",
            why_this_villain_style=(
                f"she keeps the {villain.public_mask[0]} shell intact and converts initiative into delayed control"
            ),
        )

    primary_signal = decision.selected_signals[0]
    return ExplanationLayer(
        external_move=build_external_move_envelope(knife, flavor),
        inner_drive=f"{villain.private_drive[0]} and {villain.private_drive[-1]} jointly drive this move",
        target_misread=_describe_target_misread(flavor),
        why_now=f"the {scene.visibility} arena and {scene.stake} stakes open a real window for {knife.name}",
        why_this_choice="; ".join(primary_signal.reasons),
        why_this_villain_style=(
            f"the {villain.public_mask[0]} surface stays aligned with the {flavor.delivery_surface} delivery style"
        ),
    )


def _build_tone(villain: VillainProfile, knife: KnifePrimitive, scene: SceneContext) -> str:
    tone_parts = [villain.flavor_profile.temperature]
    if scene.visibility == "public":
        tone_parts.append("public")
    else:
        tone_parts.append("private")
    if knife.id in MEMORY_PRESSURE_KNIVES:
        tone_parts.append("memory")
    elif knife.id in PUBLIC_PRESSURE_KNIVES:
        tone_parts.append("pressure")
    else:
        tone_parts.append("binding")
    return "-".join(tone_parts)


def _build_aesthetic(
    villain: VillainProfile,
    knife: KnifePrimitive,
    scene: SceneContext,
) -> tuple[str, ...]:
    arena_surface = {
        "chaotang": "法统",
        "menpai": "门规",
        "shijia": "家格",
        "jianghu": "名望",
        "qingzhai": "亲密场",
        "ziyuan": "筹码",
        "mingsheng": "声名",
        "shitu": "辈分",
    }[scene.arena]
    return (
        arena_surface,
        villain.flavor_profile.temperature,
        villain.flavor_profile.rituality,
        knife.name,
    )


def _build_social_surface(villain: VillainProfile, scene: SceneContext) -> tuple[str, ...]:
    if scene.visibility == "public":
        return tuple(villain.public_mask[:2]) + ("你我都该体面一些",)
    return tuple(villain.public_mask[:2]) + ("我只是在替你收拾局面",)


def _build_private_subtext(villain: VillainProfile, knife: KnifePrimitive) -> tuple[str, ...]:
    return (
        villain.private_drive[0],
        villain.private_drive[-1],
        f"{knife.name}会把你的下一步也带回我的叙事里",
    )


def _select_delivery_surface(*, villain: VillainProfile, scene: SceneContext) -> str:
    if scene.visibility == "private" and villain.flavor_profile.control_preference in {
        "private_invasion",
        "emotional_absorption",
    }:
        return "private_softness"
    if villain.flavor_profile.temperature == "faded":
        return "fatigued_reserve"
    if scene.visibility == "public" and villain.flavor_profile.control_preference == "public_rewrite":
        return "courteous_superiority"
    if villain.flavor_profile.rituality == "high" and scene.arena in {"chaotang", "menpai", "shijia"}:
        return "ritual_distance"
    return "public_innocence" if scene.visibility == "public" else "private_softness"


def _select_pressure_channel(
    *, villain: VillainProfile, knife: KnifePrimitive, scene: SceneContext
) -> str:
    if knife.id == "self_image_feeding":
        return "self_image"
    if knife.id in {"courteous_humiliation", "high_ground_pity"}:
        return "witness_pressure" if scene.visibility == "public" else "status_gap"
    if knife.id in {"fake_vulnerability", "gentle_absorption"}:
        return "dependency_pull"
    if knife.id == "delayed_asking":
        return "guilt_pull"
    if knife.id in MEMORY_PRESSURE_KNIVES:
        return "memory_reframe"
    if villain.flavor_profile.control_preference == "resource_cut":
        return "status_gap"
    return "guilt_pull"


def _select_witness_posture(*, villain: VillainProfile, scene: SceneContext) -> str:
    if scene.visibility == "private":
        if any(observer.role == "recovery_node" for observer in scene.observers):
            return "hide_from_recovery_node"
        return "avoid_witness"
    if any(observer.role == "judge" for observer in scene.observers):
        return "perform_for_judge"
    if any(observer.role == "transmitter" for observer in scene.observers):
        return "seed_for_transmitter"
    if villain.flavor_profile.witness_dependence == "private":
        return "avoid_witness"
    return "use_witness"


def _select_cost_profile(
    *,
    villain: VillainProfile,
    knife: KnifePrimitive,
    scene: SceneContext,
) -> str:
    if scene.visibility == "public" and villain.flavor_profile.control_preference == "public_rewrite":
        return "reputation_bet"
    if scene.visibility == "public" and villain.flavor_profile.cruelty_visibility in {"mixed", "open"}:
        return "high_backfire"
    if "public_backfire" in knife.risks or "status_bet" in knife.risks:
        return "delayed_exposure"
    return "low_exposure"


def _select_hook_style(*, villain: VillainProfile, knife: KnifePrimitive) -> str:
    if villain.flavor_profile.control_preference == "public_rewrite":
        return "public_record_seed"
    if villain.flavor_profile.control_preference == "resource_cut":
        return "debt_seed"
    if villain.flavor_profile.control_preference == "emotional_absorption":
        return "dependency_seed"
    if knife.id in MEMORY_PRESSURE_KNIVES:
        return "misread_seed"
    return "shame_seed"


def _select_structural_targets(
    *,
    scene: SceneContext,
    cost_profile: str,
    hook_style: str,
    state_shift_focus: str,
) -> tuple[str, ...]:
    targets: list[str] = ["external_move", "state_shift"]
    if cost_profile in {"reputation_bet", "high_backfire", "delayed_exposure"} or scene.visibility == "public":
        targets.append("risk_if_exposed")
    if hook_style in {"debt_seed", "dependency_seed", "public_record_seed", "misread_seed"}:
        targets.append("future_hooks")
    if state_shift_focus == "hook" and "future_hooks" not in targets:
        targets.append("future_hooks")

    deduped: list[str] = []
    for target in targets:
        if target not in deduped:
            deduped.append(target)
    return tuple(deduped)


def _select_state_shift_focus(
    *,
    villain: VillainProfile,
    knife: KnifePrimitive,
    scene: SceneContext,
) -> str:
    if knife.id in MEMORY_PRESSURE_KNIVES:
        return "psychological"
    if villain.flavor_profile.control_preference == "public_rewrite" or knife.id in PUBLIC_PRESSURE_KNIVES:
        return "narrative"
    if villain.flavor_profile.control_preference == "resource_cut":
        return "hook" if scene.visibility == "public" else "relationship"
    if villain.flavor_profile.control_preference in {"private_invasion", "emotional_absorption"}:
        return "relationship"
    return "relationship"


def _build_fallback_external_move(decision: DecisionLayer, scene: SceneContext) -> str:
    action = decision.fallback_action or "gather_information"
    if action == "reduce_exposure":
        return f"she retracts the public motion and leaves only the least actionable {scene.stake} posture behind"
    if action == "defer_to_public_mask":
        return "she retreats into the safest public mask and leaves no clean proof of intent"
    if action == "hold_position":
        return "she holds position without adding force and waits for a steadier opening"
    return "she does not land a knife yet and instead redirects the room toward safer information gathering"


def _describe_target_misread(flavor: FlavorRender) -> str:
    mapping = {
        "self_image": "the target mistakes face maintenance for self-directed choice",
        "witness_pressure": "the target reads observers as passive onlookers instead of active judges",
        "guilt_pull": "the target mistakes guilt for a debt that must be paid immediately",
        "status_gap": "the target mistakes a concession for real balance",
        "dependency_pull": "the target mistakes soothing for understanding",
        "memory_reframe": "the target mistakes reframing for genuine recognition of old hurt",
    }
    return mapping[flavor.pressure_channel]


def _resolve_payoff_window(time_horizon: str) -> str:
    mapping = {
        "short": "near",
        "mid": "mid",
        "long": "long",
    }
    return mapping[time_horizon]
