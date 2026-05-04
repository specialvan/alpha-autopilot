from __future__ import annotations

from backend.app.services.narrative_v8.knife_library import (
    BASELINE_KNIFE_IDS,
    build_compatibility_graph,
    build_default_knife_library,
    get_knife_by_id,
)


def test_knife_library_contains_all_baseline_primitives() -> None:
    library = build_default_knife_library()
    knife_ids = {knife.id for knife in library}

    assert len(library) == 10
    assert knife_ids == set(BASELINE_KNIFE_IDS)


def test_compatibility_graph_exposes_incompatible_pairs() -> None:
    graph = build_compatibility_graph()
    incompatible_pairs = {
        frozenset((edge.left, edge.right))
        for edge in graph
        if edge.relation == "incompatible"
    }

    assert frozenset(("fake_vulnerability", "courteous_humiliation")) in incompatible_pairs
    assert frozenset(("relationship_withdrawal", "gentle_absorption")) in incompatible_pairs


def test_public_pressure_primitives_declare_observer_requirements() -> None:
    library = build_default_knife_library()
    self_image_feeding = get_knife_by_id("self_image_feeding", library=library)
    courteous_humiliation = get_knife_by_id("courteous_humiliation", library=library)

    assert self_image_feeding.constraints.observer_requirements
    assert courteous_humiliation.constraints.observer_requirements


def test_high_exposure_risk_primitives_declare_backfire_conditions() -> None:
    library = build_default_knife_library()
    high_ground_pity = get_knife_by_id("high_ground_pity", library=library)
    courteous_humiliation = get_knife_by_id("courteous_humiliation", library=library)

    assert high_ground_pity.constraints.backfire_conditions
    assert courteous_humiliation.constraints.backfire_conditions
