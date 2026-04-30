from __future__ import annotations

from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.event_injection import EventInjectionService
from backend.app.services.narrative_v6.parallel_simulation import ParallelPlotSimulationService
from backend.app.services.narrative_v6.schemas import (
    CharacterParameterizeRequest,
    EventInjectionRequest,
    NarrativeSeedExtractionRequest,
    ParallelSimulationRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _simulation_result():
    seed = NarrativeSeedExtractor().extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {"chapter_number": 41, "text": "林墨说要突围。苏澈点头。"},
                {"chapter_number": 42, "text": "苏澈背叛了林墨，北城宣战。"},
            ]
        )
    ).seed
    profiles = CharacterParameterizer().parameterize(CharacterParameterizeRequest(seed=seed)).profiles
    result = ParallelPlotSimulationService().run(
        ParallelSimulationRequest(
            story_state={"chapter_index": 42, "stage": "middle"},
            narrative_seed=seed,
            character_profiles=profiles,
            path_count=3,
        )
    )
    return result


def test_event_injection_recomputes_scores_and_winner_with_audit_log() -> None:
    simulation = _simulation_result()
    service = EventInjectionService()

    result = service.inject(
        simulation,
        EventInjectionRequest(
            injected_event={
                "event_id": "evt-001",
                "event_type": "betrayal",
                "description": "核心盟友突然倒戈",
                "affected_characters": ["林墨", "苏澈"],
                "force_level": 0.9,
            },
            author_intent={"forbid_character_death": True},
            macro_story_structure="anthology",
        ),
    )

    assert result.updated_paths
    assert result.audit_log
    assert result.decision_summary
    assert result.previous_winner_path_id == simulation.winner_path_id
    assert result.updated_simulation.winner_path_id == result.winner_path_id
    assert result.destructive_confirmation_required is True
    assert any(flag == "macro-structure-break-risk" for flag in result.macro_structure_risk)

    old_scores = {path.path_id: path.retention_score for path in simulation.paths}
    new_scores = {path.path_id: path.retention_score for path in result.updated_paths}
    assert any(new_scores[path_id] != old_scores.get(path_id) for path_id in new_scores)


def test_event_injection_reports_ranking_changes_when_order_moves() -> None:
    simulation = _simulation_result()
    service = EventInjectionService()

    result = service.inject(
        simulation,
        EventInjectionRequest(
            injected_event={
                "event_id": "evt-002",
                "event_type": "secret_reveal",
                "description": "隐藏线索提前曝光",
                "affected_characters": [],
                "force_level": 0.85,
            },
            macro_story_structure="progressive",
        ),
    )

    assert result.ranking_changes is not None
    assert result.winner_path_id is not None
