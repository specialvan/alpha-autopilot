from __future__ import annotations

from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.parallel_simulation import ParallelPlotSimulationService
from backend.app.services.narrative_v6.schemas import (
    CharacterParameterizeRequest,
    NarrativeSeedExtractionRequest,
    ParallelSimulationRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor
from backend.app.services.narrative_v6.state_store import PersistentSimulationStore


def _build_result(simulation_id: str):
    seed = NarrativeSeedExtractor().extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {"chapter_number": 1, "text": "林墨说先守住城门。苏澈问要不要反击。"},
                {"chapter_number": 2, "text": "苏澈背叛了林墨，北城宣战。"},
            ]
        )
    ).seed
    profiles = CharacterParameterizer().parameterize(CharacterParameterizeRequest(seed=seed)).profiles
    return ParallelPlotSimulationService().run(
        ParallelSimulationRequest(
            simulation_id=simulation_id,
            story_state={"chapter_index": 2, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
        )
    )


def test_persistent_store_can_reload_saved_simulation(tmp_path) -> None:
    path = tmp_path / "v6_store.jsonl"
    store = PersistentSimulationStore(path=path)
    result = _build_result("sim-persist-1")

    store.save(result)

    reloaded = PersistentSimulationStore(path=path)
    restored = reloaded.get("sim-persist-1")

    assert restored is not None
    assert restored.simulation_id == "sim-persist-1"
    assert restored.winner_path_id == result.winner_path_id
    assert restored.decision_summary == result.decision_summary


def test_persistent_store_keeps_latest_snapshot_when_same_simulation_saved_twice(tmp_path) -> None:
    path = tmp_path / "v6_store.jsonl"
    store = PersistentSimulationStore(path=path)
    first = _build_result("sim-persist-2")
    second = first.model_copy(deep=True)
    second.decision_summary = "updated-summary"

    store.save(first)
    store.save(second)

    reloaded = PersistentSimulationStore(path=path)
    restored = reloaded.get("sim-persist-2")

    assert restored is not None
    assert restored.decision_summary == "updated-summary"
    assert reloaded.list_ids() == ["sim-persist-2"]


def test_persistent_store_rotates_rows_and_replays_archived_results(tmp_path) -> None:
    path = tmp_path / "v6_store.jsonl"
    archive_root = tmp_path / "archive"
    store = PersistentSimulationStore(
        path=path,
        max_rows_per_file=1,
        max_bytes_per_file=10_000_000,
        archive_root=archive_root,
    )

    first = _build_result("sim-rotate-1")
    second = _build_result("sim-rotate-2")
    store.save(first)
    store.save(second)

    archived_files = list(archive_root.rglob("v6_store-*.jsonl"))
    assert archived_files, "expected archived file after row-based rotation"
    assert path.exists(), "active file should still exist for fresh writes"

    reloaded = PersistentSimulationStore(path=path, archive_root=archive_root)
    assert reloaded.get("sim-rotate-1") is not None
    assert reloaded.get("sim-rotate-2") is not None
    assert reloaded.list_ids() == ["sim-rotate-1", "sim-rotate-2"]


def test_persistent_store_rotates_by_file_size_threshold(tmp_path) -> None:
    path = tmp_path / "v6_store.jsonl"
    archive_root = tmp_path / "archive"
    store = PersistentSimulationStore(
        path=path,
        max_rows_per_file=1000,
        max_bytes_per_file=1,
        archive_root=archive_root,
    )

    first = _build_result("sim-bytes-1")
    second = _build_result("sim-bytes-2")
    store.save(first)
    store.save(second)

    archived_files = list(archive_root.rglob("v6_store-*.jsonl"))
    assert archived_files, "expected archived file after size-based rotation"
    assert store.get("sim-bytes-1") is not None
    assert store.get("sim-bytes-2") is not None
