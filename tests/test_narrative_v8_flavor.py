from __future__ import annotations

from backend.app.services.narrative_v8.flavor import (
    build_risk_if_exposed,
    build_state_shift_emphasis,
    render_flavor,
)
from backend.app.services.narrative_v8.knife_library import build_default_knife_library, get_knife_by_id
from backend.app.services.narrative_v8.schemas import SceneContext, VillainProfile


def build_villain(
    *,
    villain_id: str,
    control_preference: str,
    witness_dependence: str,
    temperature: str = "cold",
    cruelty_visibility: str = "hidden",
) -> VillainProfile:
    return VillainProfile(
        id=villain_id,
        archetype="flavor-test",
        core_wound="被当众剥夺选择权",
        core_belief="先控制叙事，再控制关系",
        psychology_literacy="systematic",
        preferred_knives=("self_image_feeding", "courteous_humiliation"),
        secondary_knives=("baited_concession",),
        forbidden_moves=("relationship_withdrawal",),
        public_mask=("温柔", "克制"),
        private_drive=("解释权", "回收债务"),
        time_horizon="long",
        blind_spot="把秩序等同于稳定",
        escalation_rule="遭遇反抗后升级为更精致的公开控制",
        shame_relation="weaponized",
        witness_need="high",
        flavor_profile={
            "temperature": temperature,
            "rituality": "high",
            "sensuality": "low",
            "theatricality": "mid",
            "cruelty_visibility": cruelty_visibility,
            "witness_dependence": witness_dependence,
            "control_preference": control_preference,
        },
    )


def build_scene(
    *,
    arena: str = "chaotang",
    visibility: str = "public",
    observers: tuple[dict[str, object], ...],
) -> SceneContext:
    return SceneContext(
        arena=arena,
        stake="reputation" if visibility == "public" else "bond",
        observers=observers,
        power_topology=(
            {
                "source": "villain-flavor",
                "target": "target-flavor",
                "relation": "narrative_pressure",
                "asymmetry": 2,
            },
        ),
        relationship_distance="formal" if visibility == "public" else "personal",
        visibility=visibility,
        time_pressure="mid",
        current_phase="pressure_test",
        existing_state={},
    )


def public_observers() -> tuple[dict[str, object], ...]:
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
    )


def private_observers() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "observer-recovery",
            "role": "recovery_node",
            "alignment": "mixed",
            "importance": 1,
            "visibility_impact": 0,
        },
    )


def test_flavor_same_knife_differs_for_different_villains() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    scene = build_scene(observers=public_observers())
    public_rewriter = build_villain(
        villain_id="villain-public",
        control_preference="public_rewrite",
        witness_dependence="public",
    )
    resource_cutter = build_villain(
        villain_id="villain-resource",
        control_preference="resource_cut",
        witness_dependence="mixed",
        temperature="faded",
        cruelty_visibility="mixed",
    )

    public_flavor = render_flavor(public_rewriter, knife, scene)
    resource_flavor = render_flavor(resource_cutter, knife, scene)

    assert public_flavor != resource_flavor


def test_flavor_same_villain_differs_for_different_arenas() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    villain = build_villain(
        villain_id="villain-arena",
        control_preference="public_rewrite",
        witness_dependence="public",
    )

    public_flavor = render_flavor(villain, knife, build_scene(arena="chaotang", observers=public_observers()))
    private_flavor = render_flavor(
        villain,
        knife,
        build_scene(arena="qingzhai", visibility="private", observers=private_observers()),
    )

    assert public_flavor != private_flavor


def test_flavor_render_remains_structurally_separate_from_flavor_axis_profile() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    villain = build_villain(
        villain_id="villain-separation",
        control_preference="public_rewrite",
        witness_dependence="public",
    )
    flavor = render_flavor(villain, knife, build_scene(observers=public_observers()))

    dumped = flavor.model_dump()
    assert "control_preference" not in dumped
    assert "witness_dependence" not in dumped
    assert "structural_targets" in dumped


def test_flavor_changes_structural_packet_fields_besides_wording() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    scene = build_scene(observers=public_observers())
    public_rewriter = build_villain(
        villain_id="villain-public-struct",
        control_preference="public_rewrite",
        witness_dependence="public",
    )
    resource_cutter = build_villain(
        villain_id="villain-resource-struct",
        control_preference="resource_cut",
        witness_dependence="mixed",
        temperature="faded",
        cruelty_visibility="mixed",
    )

    public_flavor = render_flavor(public_rewriter, knife, scene)
    resource_flavor = render_flavor(resource_cutter, knife, scene)

    assert (
        public_flavor.hook_style != resource_flavor.hook_style
        or public_flavor.cost_profile != resource_flavor.cost_profile
        or public_flavor.state_shift_focus != resource_flavor.state_shift_focus
    )


def test_flavor_can_change_hook_style_or_exposure_profile_without_changing_knife() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    scene = build_scene(observers=public_observers())
    public_rewriter = build_villain(
        villain_id="villain-public-risk",
        control_preference="public_rewrite",
        witness_dependence="public",
    )
    resource_cutter = build_villain(
        villain_id="villain-resource-risk",
        control_preference="resource_cut",
        witness_dependence="mixed",
        temperature="faded",
        cruelty_visibility="mixed",
    )

    public_flavor = render_flavor(public_rewriter, knife, scene)
    resource_flavor = render_flavor(resource_cutter, knife, scene)

    assert (
        public_flavor.hook_style != resource_flavor.hook_style
        or build_risk_if_exposed(knife, public_flavor) != build_risk_if_exposed(knife, resource_flavor)
    )


def test_flavor_structural_targets_always_cover_at_least_two_packet_surfaces() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    flavor = render_flavor(
        build_villain(
            villain_id="villain-coverage",
            control_preference="public_rewrite",
            witness_dependence="public",
        ),
        knife,
        build_scene(observers=public_observers()),
    )

    assert len(set(flavor.structural_targets)) >= 2


def test_flavor_state_shift_focus_matches_emphasis_template() -> None:
    knife = get_knife_by_id("self_image_feeding", library=build_default_knife_library())
    flavor = render_flavor(
        build_villain(
            villain_id="villain-emphasis",
            control_preference="public_rewrite",
            witness_dependence="public",
        ),
        knife,
        build_scene(observers=public_observers()),
    )
    emphasis = build_state_shift_emphasis(flavor)
    focus = max(emphasis, key=emphasis.get)

    assert focus == flavor.state_shift_focus
