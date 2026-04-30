from __future__ import annotations

from backend.app.services.narrative_v6.group_memory import GroupMemoryService
from backend.app.services.narrative_v6.schemas import GroupMemoryApplyRequest


def test_group_memory_applies_effects_with_chapter_filter_and_patch_output() -> None:
    service = GroupMemoryService()

    result = service.apply(
        GroupMemoryApplyRequest(
            groups=[{"group_id": "g1", "name": "黑潮会", "description": ""}],
            memberships=[
                {"group_id": "g1", "character_id": "hero", "role": "leader"},
                {"group_id": "g1", "character_id": "ally", "role": "member"},
            ],
            group_memories=[
                {
                    "memory_id": "m1",
                    "group_id": "g1",
                    "summary": "曾遭背叛",
                    "influence": {"alertness": 0.4, "hostility": 0.2},
                    "chapter_start": 10,
                    "chapter_end": 30,
                    "hidden": False,
                    "propagation_strength": 0.5,
                }
            ],
            chapter_index=20,
            reveal_hidden=False,
        )
    )

    assert len(result.behavior_effects) == 2
    assert result.propagation_logs
    assert len(result.reversible_patches) == 2
    effect = result.behavior_effects[0]
    assert effect.effect["alertness"] == 0.2


def test_group_memory_hides_hidden_events_by_default_and_respects_chapter_range() -> None:
    service = GroupMemoryService()

    result = service.apply(
        GroupMemoryApplyRequest(
            groups=[{"group_id": "g1", "name": "黑潮会", "description": ""}],
            memberships=[{"group_id": "g1", "character_id": "hero", "role": "member"}],
            group_memories=[
                {
                    "memory_id": "hidden-memory",
                    "group_id": "g1",
                    "summary": "内部清洗",
                    "influence": {"loyalty": 0.6},
                    "chapter_start": 5,
                    "chapter_end": 8,
                    "hidden": True,
                    "propagation_strength": 1.0,
                }
            ],
            chapter_index=12,
            reveal_hidden=False,
        )
    )

    assert result.behavior_effects == []
    assert result.reversible_patches == []
    assert result.propagation_logs
    assert result.propagation_logs[0].status in {"skipped", "suppressed"}
