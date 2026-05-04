from __future__ import annotations

from backend.app.services.narrative_v8.knife_library import (
    build_compatibility_graph,
    build_default_knife_library,
)
from backend.app.services.narrative_v8.schemas import SceneContext, TargetProfile, VillainProfile
from backend.app.services.narrative_v8.selection import select_knives


def build_flavor_profile(
    *,
    control_preference: str = "public_rewrite",
    witness_dependence: str = "public",
    temperature: str = "cold",
    cruelty_visibility: str = "hidden",
) -> dict[str, str]:
    return {
        "temperature": temperature,
        "rituality": "high",
        "sensuality": "low",
        "theatricality": "mid",
        "cruelty_visibility": cruelty_visibility,
        "witness_dependence": witness_dependence,
        "control_preference": control_preference,
    }


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
) -> VillainProfile:
    return VillainProfile(
        id=villain_id,
        archetype="control_architect",
        core_wound="曾被公开剥夺解释权",
        core_belief="先定义秩序的人才能定义善恶",
        psychology_literacy=psychology_literacy,
        preferred_knives=preferred,
        secondary_knives=secondary,
        forbidden_moves=forbidden,
        public_mask=("克制", "替人着想"),
        private_drive=("解释权", "绑定"),
        time_horizon="long",
        blind_spot="容易高估礼法外壳的稳定性",
        escalation_rule="遭遇公开抵抗时升级为见证压迫",
        shame_relation="weaponized",
        witness_need=witness_need,
        flavor_profile=build_flavor_profile(
            control_preference=control_preference,
            witness_dependence=witness_dependence,
        ),
    )


def build_target(
    *,
    defense_style: str = "ceremonial",
    resistance_style: str = "measured",
    witness_sensitivity: str = "high",
    weak_points: tuple[str, ...] = ("protector_complex", "debt_sensitive", "old_wound"),
    core_need: str = "connection",
    social_priorities: tuple[str, ...] = ("status",),
    identity_anchor: str = "必须维持长者体面",
) -> TargetProfile:
    return TargetProfile(
        id="target-shenqiao",
        self_image="守礼的护持者",
        core_need=core_need,
        core_fear="在众目睽睽下失去自我定义",
        weak_points=weak_points,
        defense_style=defense_style,
        resistance_style=resistance_style,
        witness_sensitivity=witness_sensitivity,
        identity_anchor=identity_anchor,
        social_priorities=social_priorities,
    )


def build_scene(
    *,
    arena: str = "chaotang",
    stake: str = "reputation",
    visibility: str = "public",
    observers: tuple[dict[str, object], ...],
    asymmetry: int = 2,
    time_pressure: str = "mid",
    current_control_state: str = "harmless",
) -> SceneContext:
    return SceneContext(
        arena=arena,
        stake=stake,
        observers=observers,
        power_topology=(
            {
                "source": "villain-luoxue",
                "target": "target-shenqiao",
                "relation": "ceremonial_seniority",
                "asymmetry": asymmetry,
            },
        ),
        relationship_distance="formal" if visibility == "public" else "personal",
        visibility=visibility,
        time_pressure=time_pressure,
        current_phase="pressure_test",
        current_control_state=current_control_state,
        existing_state={},
    )


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


def networked_public_observers() -> tuple[dict[str, object], ...]:
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


def find_signal(result, knife_id: str):
    return next(signal for signal in result.scored_candidates if signal.knife_id == knife_id)


def test_selection_same_knife_scores_differ_for_different_villains() -> None:
    library = build_default_knife_library()
    graph = build_compatibility_graph()
    target = build_target()
    scene = build_scene(observers=networked_public_observers())
    public_controller = build_villain(
        villain_id="villain-public",
        preferred=("self_image_feeding", "courteous_humiliation"),
        secondary=("baited_concession",),
        psychology_literacy="systematic",
        witness_need="high",
        control_preference="public_rewrite",
        witness_dependence="public",
    )
    quieter_operator = build_villain(
        villain_id="villain-quiet",
        preferred=("self_image_feeding", "delayed_asking"),
        secondary=("baited_concession",),
        psychology_literacy="experiential",
        witness_need="low",
        control_preference="resource_cut",
        witness_dependence="mixed",
    )

    public_result = select_knives(
        public_controller,
        target,
        scene,
        library=library,
        compatibility_graph=graph,
    )
    quiet_result = select_knives(
        quieter_operator,
        target,
        scene,
        library=library,
        compatibility_graph=graph,
    )

    public_signal = find_signal(public_result, "self_image_feeding")
    quiet_signal = find_signal(quiet_result, "self_image_feeding")

    assert public_signal.fit_score != quiet_signal.fit_score
    assert public_signal.reasons != quiet_signal.reasons


def test_selection_changes_outcome_when_scene_changes() -> None:
    library = build_default_knife_library()
    graph = build_compatibility_graph()
    villain = build_villain(
        villain_id="villain-swing",
        preferred=("self_image_feeding", "fake_vulnerability"),
        secondary=("delayed_asking",),
    )
    target = build_target()
    public_scene = build_scene(observers=networked_public_observers())
    private_scene = build_scene(
        arena="qingzhai",
        stake="bond",
        visibility="private",
        observers=(),
    )

    public_result = select_knives(
        villain, target, public_scene, library=library, compatibility_graph=graph
    )
    private_result = select_knives(
        villain, target, private_scene, library=library, compatibility_graph=graph
    )

    assert public_result.decision.primary_knife_id != private_result.decision.primary_knife_id


def test_selection_forbidden_knife_always_appears_in_rejected_list() -> None:
    result = select_knives(
        build_villain(
            villain_id="villain-forbidden",
            preferred=("self_image_feeding",),
            secondary=("baited_concession",),
            forbidden=("relationship_withdrawal",),
        ),
        build_target(),
        build_scene(observers=networked_public_observers()),
        library=build_default_knife_library(),
        compatibility_graph=build_compatibility_graph(),
    )

    assert any(
        reason.knife_id == "relationship_withdrawal" and reason.category == "forbidden_move"
        for reason in result.decision.rejected_knives
    )


def test_selection_missing_observer_requirement_is_hard_rejection() -> None:
    result = select_knives(
        build_villain(
            villain_id="villain-observer-gate",
            preferred=("courteous_humiliation", "self_image_feeding"),
        ),
        build_target(),
        build_scene(
            visibility="public",
            stake="reputation",
            observers=(
                {
                    "id": "observer-transmitter",
                    "role": "transmitter",
                    "alignment": "unknown",
                    "importance": 2,
                    "visibility_impact": 2,
                },
            ),
        ),
        library=build_default_knife_library(),
        compatibility_graph=build_compatibility_graph(),
    )

    assert any(
        reason.knife_id == "courteous_humiliation"
        and reason.category == "observer_requirement_missing"
        for reason in result.decision.rejected_knives
    )


def test_selection_anti_condition_is_not_collapsed_into_low_fit() -> None:
    result = select_knives(
        build_villain(
            villain_id="villain-fake-vulnerability",
            preferred=("fake_vulnerability",),
            secondary=("delayed_asking",),
        ),
        build_target(defense_style="skeptical"),
        build_scene(
            arena="qingzhai",
            stake="bond",
            visibility="private",
            observers=(),
        ),
        library=build_default_knife_library(),
        compatibility_graph=build_compatibility_graph(),
    )

    assert any(
        reason.knife_id == "fake_vulnerability" and reason.category == "anti_condition"
        for reason in result.decision.rejected_knives
    )


def test_selection_hard_filtered_knives_never_enter_scored_candidate_pool() -> None:
    result = select_knives(
        build_villain(
            villain_id="villain-pool",
            preferred=("fake_vulnerability",),
            secondary=("delayed_asking",),
        ),
        build_target(defense_style="skeptical"),
        build_scene(
            arena="qingzhai",
            stake="bond",
            visibility="private",
            observers=(),
        ),
        library=build_default_knife_library(),
        compatibility_graph=build_compatibility_graph(),
    )

    assert "fake_vulnerability" not in {signal.knife_id for signal in result.scored_candidates}


def test_selection_observer_topology_changes_public_pressure_fit() -> None:
    library = build_default_knife_library()
    graph = build_compatibility_graph()
    villain = build_villain(
        villain_id="villain-topology",
        preferred=("self_image_feeding", "courteous_humiliation"),
    )
    target = build_target()

    judge_only = select_knives(
        villain,
        target,
        build_scene(observers=judge_observers()),
        library=library,
        compatibility_graph=graph,
    )
    networked = select_knives(
        villain,
        target,
        build_scene(observers=networked_public_observers()),
        library=library,
        compatibility_graph=graph,
    )

    assert find_signal(judge_only, "self_image_feeding").fit_score != find_signal(
        networked, "self_image_feeding"
    ).fit_score


def test_selection_no_fit_path_returns_structured_fallback_without_fake_knife() -> None:
    result = select_knives(
        build_villain(
            villain_id="villain-no-fit",
            preferred=("courteous_humiliation",),
            secondary=("self_image_feeding",),
            forbidden=("relationship_withdrawal",),
        ),
        build_target(
            witness_sensitivity="low",
            weak_points=("certainty",),
            core_need="distance",
            social_priorities=(),
            identity_anchor="模糊",
        ),
        build_scene(
            arena="qingzhai",
            stake="bond",
            visibility="private",
            observers=(),
        ),
        library=build_default_knife_library(),
        compatibility_graph=build_compatibility_graph(),
    )

    assert result.decision.selection_mode == "fallback"
    assert result.decision.primary_knife_id is None
    assert result.decision.secondary_knife_id is None
    assert result.decision.selected_signals == ()
    assert result.decision.fallback_action is not None
    assert result.decision.fallback_reason
