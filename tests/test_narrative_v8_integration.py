from __future__ import annotations

from backend.app.services.narrative_v8.controller import build_villain_feedback
from backend.app.services.narrative_v8.knife_library import build_default_knife_library
from backend.app.services.narrative_v8.schemas import BuildVillainFeedbackInput


def build_villain(
    *,
    villain_id: str,
    preferred: tuple[str, ...],
    secondary: tuple[str, ...] = (),
    forbidden: tuple[str, ...] = ("relationship_withdrawal",),
    psychology_literacy: str = "systematic",
    witness_need: str = "high",
    control_preference: str = "public_rewrite",
    witness_dependence: str = "public",
    temperature: str = "cold",
    cruelty_visibility: str = "hidden",
) -> dict[str, object]:
    return {
        "id": villain_id,
        "archetype": "integration-villain",
        "core_wound": "曾在公开秩序里失去解释权",
        "core_belief": "叙事先于关系",
        "psychology_literacy": psychology_literacy,
        "preferred_knives": preferred,
        "secondary_knives": secondary,
        "forbidden_moves": forbidden,
        "public_mask": ("克制", "体贴"),
        "private_drive": ("解释权", "绑定"),
        "time_horizon": "long",
        "blind_spot": "把礼法外壳等同于稳定",
        "escalation_rule": "公开受挫时升级到更精细的秩序施压",
        "shame_relation": "weaponized",
        "witness_need": witness_need,
        "flavor_profile": {
            "temperature": temperature,
            "rituality": "high",
            "sensuality": "low",
            "theatricality": "mid",
            "cruelty_visibility": cruelty_visibility,
            "witness_dependence": witness_dependence,
            "control_preference": control_preference,
        },
    }


def build_target(
    *,
    defense_style: str = "ceremonial",
    resistance_style: str = "measured",
    witness_sensitivity: str = "high",
    weak_points: tuple[str, ...] = ("protector_complex", "debt_sensitive", "old_wound"),
    core_need: str = "connection",
    social_priorities: tuple[str, ...] = ("status",),
    identity_anchor: str = "必须维护长者体面",
) -> dict[str, object]:
    return {
        "id": "target-integration",
        "self_image": "守礼而不愿失态的人",
        "core_need": core_need,
        "core_fear": "在众目睽睽下丢掉体面",
        "weak_points": weak_points,
        "defense_style": defense_style,
        "resistance_style": resistance_style,
        "witness_sensitivity": witness_sensitivity,
        "identity_anchor": identity_anchor,
        "social_priorities": social_priorities,
    }


def build_scene(
    *,
    villain_id: str,
    arena: str = "chaotang",
    stake: str = "reputation",
    visibility: str = "public",
    observers: tuple[dict[str, object], ...],
    current_control_state: str = "harmless",
    existing_state: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "arena": arena,
        "stake": stake,
        "observers": observers,
        "power_topology": (
            {
                "source": villain_id,
                "target": "target-integration",
                "relation": "ritual_seniority",
                "asymmetry": 2,
            },
        ),
        "relationship_distance": "formal" if visibility == "public" else "personal",
        "visibility": visibility,
        "time_pressure": "mid",
        "current_phase": "pressure_test",
        "current_control_state": current_control_state,
        "existing_state": existing_state or {},
    }


def judge_observers() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "observer-judge",
            "role": "judge",
            "alignment": "unknown",
            "importance": 3,
            "visibility_impact": 3,
        },
    )


def networked_observers() -> tuple[dict[str, object], ...]:
    return (
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
        {
            "id": "observer-transmitter",
            "role": "transmitter",
            "alignment": "volatile",
            "importance": 2,
            "visibility_impact": 3,
        },
    )


def build_input(villain: dict[str, object], target: dict[str, object], scene: dict[str, object]) -> BuildVillainFeedbackInput:
    return BuildVillainFeedbackInput(
        villain=villain,
        target=target,
        scene=scene,
        knife_library=build_default_knife_library(),
    )


def layer_totals(packet) -> dict[str, int]:
    return {
        "relationship": sum(
            abs(value)
            for value in (
                packet.state_shift.relationship.trust_delta,
                packet.state_shift.relationship.debt_delta,
                packet.state_shift.relationship.dependency_delta,
                packet.state_shift.relationship.leverage_delta,
            )
        ),
        "narrative": sum(
            abs(value)
            for value in (
                packet.state_shift.narrative.suspicion_delta,
                packet.state_shift.narrative.reputation_delta,
                packet.state_shift.narrative.witness_alignment_delta,
                packet.state_shift.narrative.explanation_control_delta,
            )
        ),
        "psychological": sum(
            abs(value)
            for value in (
                packet.state_shift.psychological.shame_load_delta,
                packet.state_shift.psychological.wound_activation_delta,
                packet.state_shift.psychological.protector_trigger_delta,
                packet.state_shift.psychological.identity_destabilization_delta,
            )
        ),
        "hook": len(packet.state_shift.hook.planted_hooks)
        + len(packet.state_shift.hook.armed_payoffs)
        + len(packet.state_shift.hook.recovered_hooks),
    }


def test_integration_same_knife_differs_for_different_villains() -> None:
    scene = build_scene(villain_id="villain-public", observers=networked_observers())
    target = build_target()
    public_rewriter = build_input(
        build_villain(
            villain_id="villain-public",
            preferred=("self_image_feeding", "courteous_humiliation"),
            secondary=("baited_concession",),
            control_preference="public_rewrite",
            witness_dependence="public",
        ),
        target,
        scene,
    )
    resource_cutter = build_input(
        build_villain(
            villain_id="villain-resource",
            preferred=("self_image_feeding", "baited_concession"),
            secondary=("courteous_humiliation",),
            psychology_literacy="experiential",
            witness_need="low",
            control_preference="resource_cut",
            witness_dependence="mixed",
            temperature="faded",
            cruelty_visibility="mixed",
        ),
        target,
        build_scene(villain_id="villain-resource", observers=networked_observers()),
    )

    public_result = build_villain_feedback(public_rewriter)
    resource_result = build_villain_feedback(resource_cutter)

    assert public_result.packet.decision.primary_knife_id == resource_result.packet.decision.primary_knife_id
    assert public_result.packet.flavor_render != resource_result.packet.flavor_render


def test_integration_same_villain_differs_for_different_scenes() -> None:
    villain = build_villain(
        villain_id="villain-scene",
        preferred=("self_image_feeding", "fake_vulnerability"),
        secondary=("delayed_asking",),
    )
    target = build_target()

    public_result = build_villain_feedback(
        build_input(villain, target, build_scene(villain_id="villain-scene", observers=networked_observers()))
    )
    private_result = build_villain_feedback(
        build_input(
            villain,
            target,
            build_scene(
                villain_id="villain-scene",
                arena="qingzhai",
                stake="bond",
                visibility="private",
                observers=(),
            ),
        )
    )

    assert public_result.packet.decision.primary_knife_id != private_result.packet.decision.primary_knife_id


def test_integration_public_observer_topology_change_alters_selection_fit() -> None:
    villain = build_villain(
        villain_id="villain-topology",
        preferred=("self_image_feeding", "courteous_humiliation"),
    )
    target = build_target()

    judge_only = build_villain_feedback(
        build_input(villain, target, build_scene(villain_id="villain-topology", observers=judge_observers()))
    )
    networked = build_villain_feedback(
        build_input(villain, target, build_scene(villain_id="villain-topology", observers=networked_observers()))
    )

    assert (
        judge_only.packet.decision.selected_signals[0].fit_score
        != networked.packet.decision.selected_signals[0].fit_score
    )


def test_integration_anti_condition_rejection_surfaces_through_controller() -> None:
    result = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-anti",
                preferred=("fake_vulnerability",),
                secondary=("delayed_asking",),
            ),
            build_target(defense_style="skeptical"),
            build_scene(
                villain_id="villain-anti",
                arena="qingzhai",
                stake="bond",
                visibility="private",
                observers=(),
            ),
        )
    )

    assert any(
        reason.knife_id == "fake_vulnerability" and reason.category == "anti_condition"
        for reason in result.packet.decision.rejected_knives
    )


def test_integration_no_fit_fallback_keeps_knife_ids_empty() -> None:
    result = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-fallback",
                preferred=("courteous_humiliation",),
                secondary=("self_image_feeding",),
            ),
            build_target(
                witness_sensitivity="low",
                weak_points=("certainty",),
                core_need="distance",
                social_priorities=(),
                identity_anchor="模糊",
            ),
            build_scene(
                villain_id="villain-fallback",
                arena="qingzhai",
                stake="bond",
                visibility="private",
                observers=(),
            ),
        )
    )

    assert result.packet.decision.selection_mode == "fallback"
    assert result.packet.decision.primary_knife_id is None
    assert result.packet.decision.secondary_knife_id is None
    assert result.packet.decision.selected_signals == ()
    assert result.packet.transition.next_state != "collapsed"


def test_integration_public_suspicious_no_fit_uses_public_mask_and_repair_transition() -> None:
    result = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-public-fallback",
                preferred=("courteous_humiliation",),
                secondary=(),
            ),
            build_target(
                witness_sensitivity="low",
                weak_points=("certainty",),
                core_need="distance",
                social_priorities=(),
                identity_anchor="模糊",
            ),
            build_scene(
                villain_id="villain-public-fallback",
                arena="chaotang",
                stake="reputation",
                visibility="public",
                observers=(
                    {
                        "id": "observer-transmitter",
                        "role": "transmitter",
                        "alignment": "unknown",
                        "importance": 2,
                        "visibility_impact": 2,
                    },
                ),
                current_control_state="suspicious",
            ),
        )
    )

    assert result.packet.decision.selection_mode == "fallback"
    assert result.packet.decision.fallback_action == "defer_to_public_mask"
    assert result.packet.transition.next_state == "repair_attempt"
    assert result.packet.transition.recovery_mode == "retreat_to_safer_role"
    assert result.packet.transition.failure_mode == "narrative_lost"


def test_integration_layered_ledger_update_carries_forward_existing_hooks() -> None:
    existing_state = {
        "hook": {
            "planted_hooks": (
                {
                    "id": "hook-existing",
                    "source_knife_id": "memory_reframing",
                    "description": "旧钩子",
                    "payoff_window": "mid",
                    "recovery_condition": "回收旧钩子",
                },
            ),
            "armed_payoffs": (),
            "recovered_hooks": (),
        }
    }
    result = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-hooks",
                preferred=("self_image_feeding", "courteous_humiliation"),
            ),
            build_target(),
            build_scene(
                villain_id="villain-hooks",
                observers=networked_observers(),
                existing_state=existing_state,
            ),
        )
    )

    hook_ids = {hook.id for hook in result.next_snapshot.hook.planted_hooks}
    assert "hook-existing" in hook_ids
    assert any(hook.source_knife_id == result.packet.decision.primary_knife_id for hook in result.packet.future_hooks)


def test_integration_flavor_changes_structural_packet_fields_not_only_wording() -> None:
    scene = build_scene(villain_id="villain-flavor-a", observers=networked_observers())
    target = build_target()
    public_rewriter = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-flavor-a",
                preferred=("self_image_feeding", "courteous_humiliation"),
                control_preference="public_rewrite",
                witness_dependence="public",
            ),
            target,
            scene,
        )
    )
    resource_cutter = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-flavor-b",
                preferred=("self_image_feeding", "baited_concession"),
                control_preference="resource_cut",
                witness_dependence="mixed",
                temperature="faded",
                cruelty_visibility="mixed",
            ),
            target,
            build_scene(villain_id="villain-flavor-b", observers=networked_observers()),
        )
    )

    assert (
        public_rewriter.packet.flavor_render.hook_style != resource_cutter.packet.flavor_render.hook_style
        or public_rewriter.packet.risk_if_exposed != resource_cutter.packet.risk_if_exposed
        or public_rewriter.packet.flavor_render.state_shift_focus
        != resource_cutter.packet.flavor_render.state_shift_focus
    )


def test_integration_state_shift_focus_matches_actual_packet_emphasis() -> None:
    result = build_villain_feedback(
        build_input(
            build_villain(
                villain_id="villain-focus",
                preferred=("self_image_feeding", "courteous_humiliation"),
            ),
            build_target(),
            build_scene(villain_id="villain-focus", observers=networked_observers()),
        )
    )

    totals = layer_totals(result.packet)
    focus = max(totals, key=totals.get)

    assert focus == result.packet.flavor_render.state_shift_focus


def test_integration_current_control_state_changes_transition_outcome() -> None:
    villain = build_villain(
        villain_id="villain-transition-shift",
        preferred=("self_image_feeding", "courteous_humiliation"),
    )
    target = build_target()

    suspicious_result = build_villain_feedback(
        build_input(
            villain,
            target,
            build_scene(
                villain_id="villain-transition-shift",
                observers=networked_observers(),
                current_control_state="suspicious",
            ),
        )
    )
    harmless_result = build_villain_feedback(
        build_input(
            villain,
            target,
            build_scene(
                villain_id="villain-transition-shift",
                observers=networked_observers(),
                current_control_state="harmless",
            ),
        )
    )

    assert suspicious_result.packet.transition.next_state != harmless_result.packet.transition.next_state


def test_integration_public_judge_only_scene_does_not_upgrade_without_witness_network() -> None:
    villain = build_villain(
        villain_id="villain-judge-only",
        preferred=("self_image_feeding", "courteous_humiliation"),
    )
    target = build_target()

    result = build_villain_feedback(
        build_input(
            villain,
            target,
            build_scene(
                villain_id="villain-judge-only",
                observers=judge_observers(),
                current_control_state="suspicious",
            ),
        )
    )

    assert result.packet.decision.selection_mode == "scored_fit"
    assert result.packet.transition.next_state == "suspicious"
    assert result.packet.transition.upgrade_trigger is None


def test_integration_output_can_carry_control_state_forward_into_next_scene() -> None:
    villain = build_villain(
        villain_id="villain-carry-forward",
        preferred=("self_image_feeding", "courteous_humiliation"),
    )
    target = build_target()

    first_result = build_villain_feedback(
        build_input(
            villain,
            target,
            build_scene(
                villain_id="villain-carry-forward",
                observers=networked_observers(),
                current_control_state="suspicious",
            ),
        )
    )
    followup_scene = first_result.build_followup_scene(
        build_scene(
            villain_id="villain-carry-forward",
            observers=networked_observers(),
            current_control_state="harmless",
        ),
        updates={"current_phase": "containment"},
    )

    followup_result = build_villain_feedback(
        build_input(
            villain,
            target,
            followup_scene.model_dump(),
        )
    )

    assert followup_result.packet.transition.prior_state == first_result.next_control_state
    assert followup_scene.existing_state == first_result.next_snapshot
