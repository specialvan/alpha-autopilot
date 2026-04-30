from __future__ import annotations

from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.parallel_simulation import ParallelPlotSimulationService
from backend.app.services.narrative_v6.scoring import normalize_retention_vector_weights
from backend.app.services.narrative_v6.schemas import (
    CharacterParameterizeRequest,
    NarrativeSeedExtractionRequest,
    ParallelSimulationRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _seed_and_profiles():
    extractor = NarrativeSeedExtractor()
    seed = extractor.extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {
                    "chapter_number": 21,
                    "text": "林墨说必须抢在黎明前拿到钥匙。苏澈问要不要联手。",
                },
                {
                    "chapter_number": 22,
                    "text": "苏澈背叛了林墨，北城宣战，众人怀疑真正凶手是谁？",
                },
            ]
        )
    ).seed
    profiles = CharacterParameterizer().parameterize(CharacterParameterizeRequest(seed=seed)).profiles
    return seed, profiles


def test_parallel_simulation_generates_three_independent_paths_and_winner() -> None:
    seed, profiles = _seed_and_profiles()
    service = ParallelPlotSimulationService()

    result = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
        )
    )

    assert len(result.paths) == 3
    assert len({path.path_id for path in result.paths}) == 3

    successful_paths = [path for path in result.paths if path.status == "ok"]
    assert len(successful_paths) >= 2
    assert all(path.character_reactions for path in successful_paths)
    assert all(path.relationship_deltas is not None for path in successful_paths)

    top = max(successful_paths, key=lambda item: item.retention_score)
    assert result.winner_path_id == top.path_id
    assert "retention_score" in result.decision_summary


def test_parallel_simulation_isolates_single_path_failure() -> None:
    seed, profiles = _seed_and_profiles()
    service = ParallelPlotSimulationService()

    result = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
            debug_force_fail_strategies=["suspense_first"],
        )
    )

    failed_paths = [path for path in result.paths if path.status == "failed"]
    successful_paths = [path for path in result.paths if path.status == "ok"]

    assert len(failed_paths) == 1
    assert len(successful_paths) >= 2
    assert result.winner_path_id in {path.path_id for path in successful_paths}
    assert failed_paths[0].error_message


def test_parallel_simulation_carries_graph_rag_hints_per_path() -> None:
    seed, profiles = _seed_and_profiles()
    service = ParallelPlotSimulationService()

    result = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
        ),
        graph_rag_hints=[
            "苏澈背叛林墨，关系从同盟转为敌对",
            "北城宣战将强化生存压力",
            "钥匙悬念需要兑现",
        ],
    )

    successful_paths = [path for path in result.paths if path.status == "ok"]
    assert successful_paths
    assert all(path.graph_rag_hints for path in successful_paths)
    assert successful_paths[0].graph_rag_hints[0].startswith("苏澈背叛")


def test_parallel_simulation_respects_plot_unit_scaffold_contract() -> None:
    seed, profiles = _seed_and_profiles()
    service = ParallelPlotSimulationService()

    result = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
            plot_unit_scaffold={
                "encounter_event": "密令提前泄露，主角被迫应战",
                "desire_goal": "守住城门并确保密钥安全",
                "obstacle": "同盟内出现身份不明的内应",
                "solution_method": "分兵诱导并反向布置假线索",
                "action_climax": {"node": "在城门伏击点揭露内应", "turn_type": "goal_inversion"},
                "resolution": "城门暂守住，但真正密钥仍未现身",
            },
        )
    )

    successful_paths = [path for path in result.paths if path.status == "ok"]
    assert successful_paths
    for path in successful_paths:
        assert path.six_step_scaffold_mapping["encounter_event"] == "密令提前泄露，主角被迫应战"
        assert path.six_step_scaffold_mapping["desire_goal"] == "守住城门并确保密钥安全"
        assert path.six_step_scaffold_mapping["obstacle"] == "同盟内出现身份不明的内应"
        assert path.six_step_scaffold_mapping["solution_method"] == "分兵诱导并反向布置假线索"
        assert path.six_step_scaffold_mapping["action_climax"] == "在城门伏击点揭露内应"
        assert path.six_step_scaffold_mapping["action_climax_turn_type"] == "goal_inversion"
        assert path.six_step_scaffold_mapping["resolution"] == "城门暂守住，但真正密钥仍未现身"
        assert path.plot_outline[0] == "密令提前泄露，主角被迫应战"


def test_v6_retention_vector_supports_v5_desire_keys_mapping() -> None:
    mapped = normalize_retention_vector_weights(
        {
            "primal_desire": 0.1,
            "value_recognition": 0.2,
            "knowledge_curiosity": 0.3,
            "information_gap": 0.4,
            "dominant": "information_gap",
        }
    )

    assert set(mapped.keys()) == {"hook_strength", "suspense", "relationship_tension", "coherence"}
    assert abs(sum(mapped.values()) - 1.0) < 1e-9
    assert mapped["suspense"] > mapped["relationship_tension"]
    assert mapped["hook_strength"] > 0.2


def test_parallel_simulation_accepts_v5_retention_vector_for_path_ranking() -> None:
    seed, profiles = _seed_and_profiles()
    service = ParallelPlotSimulationService()

    information_gap_focused = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
            strategies=["suspense_first", "retention_first", "relationship_burst"],
            retention_desire_vector={
                "primal_desire": 0.1,
                "value_recognition": 0.1,
                "knowledge_curiosity": 0.1,
                "information_gap": 0.95,
                "dominant": "information_gap",
            },
        )
    )
    primal_desire_focused = service.run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 22, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
            strategies=["suspense_first", "retention_first", "relationship_burst"],
            retention_desire_vector={
                "primal_desire": 0.95,
                "value_recognition": 0.1,
                "knowledge_curiosity": 0.1,
                "information_gap": 0.1,
                "dominant": "primal_desire",
            },
        )
    )

    info_gap_path = next(path for path in information_gap_focused.paths if path.strategy == "suspense_first")
    primal_path = next(path for path in primal_desire_focused.paths if path.strategy == "suspense_first")
    assert info_gap_path.retention_score > primal_path.retention_score
