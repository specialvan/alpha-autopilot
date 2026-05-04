from __future__ import annotations

from backend.app.services.narrative_v8.flavor import render_flavor
from backend.app.services.narrative_v8.knife_library import build_default_knife_library, get_knife_by_id
from backend.app.services.narrative_v8.schemas import DecisionLayer, SceneContext, TargetProfile, VillainProfile
from backend.app.services.narrative_v8.transitions import derive_transition_outcome


def build_villain() -> VillainProfile:
    return VillainProfile(
        id="villain-transition",
        archetype="transition-operator",
        core_wound="曾经在公开场合被夺走解释权",
        core_belief="只要先控制当下解释，就能后续控制关系",
        psychology_literacy="systematic",
        preferred_knives=("self_image_feeding", "courteous_humiliation"),
        secondary_knives=("baited_concession",),
        forbidden_moves=("relationship_withdrawal",),
        public_mask=("克制", "体贴"),
        private_drive=("解释权", "绑定"),
        time_horizon="long",
        blind_spot="把秩序等同于稳定",
        escalation_rule="公开受挫时升级到更精细的秩序施压",
        shame_relation="weaponized",
        witness_need="high",
        flavor_profile={
            "temperature": "cold",
            "rituality": "high",
            "sensuality": "low",
            "theatricality": "mid",
            "cruelty_visibility": "hidden",
            "witness_dependence": "public",
            "control_preference": "public_rewrite",
        },
    )


def build_target() -> TargetProfile:
    return TargetProfile(
        id="target-transition",
        self_image="守礼而不愿失态的人",
        core_need="connection",
        core_fear="在众人面前丢掉体面",
        weak_points=("protector_complex", "debt_sensitive", "old_wound"),
        defense_style="ceremonial",
        resistance_style="measured",
        witness_sensitivity="high",
        identity_anchor="必须维护长者体面",
        social_priorities=("status",),
    )


def build_scene(*, current_control_state: str, visibility: str = "public") -> SceneContext:
    observers = (
        {
            "id": "observer-judge",
            "role": "judge",
            "alignment": "unknown",
            "importance": 3,
            "visibility_impact": 3,
        },
        {
            "id": "observer-transmitter",
            "role": "transmitter",
            "alignment": "volatile",
            "importance": 2,
            "visibility_impact": 3,
        },
    ) if visibility == "public" else ()
    return SceneContext(
        arena="chaotang" if visibility == "public" else "qingzhai",
        stake="reputation" if visibility == "public" else "bond",
        observers=observers,
        power_topology=(
            {
                "source": "villain-transition",
                "target": "target-transition",
                "relation": "ritual_seniority",
                "asymmetry": 2,
            },
        ),
        relationship_distance="formal" if visibility == "public" else "personal",
        visibility=visibility,
        time_pressure="mid",
        current_phase="pressure_test",
        current_control_state=current_control_state,
        existing_state={},
    )


def build_scored_decision() -> DecisionLayer:
    return DecisionLayer(
        selection_mode="scored_fit",
        primary_knife_id="self_image_feeding",
        selected_signals=(
            {
                "knife_id": "self_image_feeding",
                "fit_score": 0.92,
                "reasons": ("public witness leverage", "identity anchor exposed"),
            },
        ),
        rejected_knives=(),
    )


def build_fallback_decision(*, fallback_action: str = "reduce_exposure") -> DecisionLayer:
    return DecisionLayer(
        selection_mode="fallback",
        fallback_action=fallback_action,
        fallback_reason="no knife survived hard filters without exposure cost",
        rejected_knives=(),
    )


def build_flavor(*, visibility: str = "public"):
    villain = build_villain()
    scene = build_scene(current_control_state="harmless", visibility=visibility)
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    return render_flavor(villain, knife, scene)


def test_transition_moves_public_harmless_control_into_suspicion() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="harmless"),
        decision=build_scored_decision(),
        flavor=build_flavor(),
    )

    assert result.prior_state == "harmless"
    assert result.next_state == "suspicious"


def test_transition_turns_suspicious_fallback_into_repair_attempt_not_collapse() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="suspicious"),
        decision=build_fallback_decision(),
        flavor=build_flavor(),
    )

    assert result.next_state == "repair_attempt"
    assert result.recovery_mode == "lower_intensity"
    assert result.failure_mode == "pace_lost"


def test_transition_public_mask_fallback_uses_narrative_repair_shell() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="suspicious"),
        decision=build_fallback_decision(fallback_action="defer_to_public_mask"),
        flavor=build_flavor(),
    )

    assert result.next_state == "repair_attempt"
    assert result.recovery_mode == "retreat_to_safer_role"
    assert result.failure_mode == "narrative_lost"


def test_transition_restores_repair_attempt_into_partially_restored() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="repair_attempt"),
        decision=build_scored_decision(),
        flavor=build_flavor(),
    )

    assert result.next_state == "partially_restored"
    assert result.recovery_mode == "re_establish_narrative_control"


def test_transition_upgrades_suspicious_public_controller_when_higher_order_path_appears() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="suspicious"),
        decision=build_scored_decision(),
        flavor=build_flavor(),
    )

    assert result.next_state == "upgraded"
    assert result.upgrade_trigger == "higher_order_path_found"
    assert result.upgrade_path == "more_systemic"


def test_transition_collapses_distrusted_public_fallback_without_pretending_recovery() -> None:
    result = derive_transition_outcome(
        scene=build_scene(current_control_state="distrusted"),
        decision=build_fallback_decision(),
        flavor=build_flavor(),
    )

    assert result.next_state == "collapsed"
    assert result.failure_mode == "shell_exposed"
    assert result.recovery_mode is None
