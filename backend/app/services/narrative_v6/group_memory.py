from __future__ import annotations

from .schemas import (
    BehaviorEffect,
    GroupMemoryApplyRequest,
    GroupMemoryGraph,
    GroupMemoryPropagationLog,
    ReversiblePatch,
)


class GroupMemoryService:
    def apply(self, request: GroupMemoryApplyRequest) -> GroupMemoryGraph:
        behavior_effects: list[BehaviorEffect] = []
        logs: list[GroupMemoryPropagationLog] = []
        patches: list[ReversiblePatch] = []

        members_by_group: dict[str, list[str]] = {}
        for membership in request.memberships:
            members_by_group.setdefault(membership.group_id, []).append(membership.character_id)

        for memory in request.group_memories:
            members = members_by_group.get(memory.group_id, [])
            if not members:
                logs.append(
                    GroupMemoryPropagationLog(
                        memory_id=memory.memory_id,
                        group_id=memory.group_id,
                        character_id="",
                        status="skipped",
                        reason="group-has-no-members",
                    )
                )
                continue

            if not self._in_chapter_range(
                request.chapter_index,
                start=memory.chapter_start,
                end=memory.chapter_end,
            ):
                for character_id in members:
                    logs.append(
                        GroupMemoryPropagationLog(
                            memory_id=memory.memory_id,
                            group_id=memory.group_id,
                            character_id=character_id,
                            status="skipped",
                            reason="chapter-out-of-range",
                        )
                    )
                continue

            for character_id in members:
                scaled_effect = {
                    key: round(value * memory.propagation_strength, 4)
                    for key, value in memory.influence.items()
                }
                hidden_suppressed = memory.hidden and not request.reveal_hidden
                if hidden_suppressed:
                    logs.append(
                        GroupMemoryPropagationLog(
                            memory_id=memory.memory_id,
                            group_id=memory.group_id,
                            character_id=character_id,
                            status="suppressed",
                            reason="hidden-memory",
                        )
                    )
                    continue

                behavior_effects.append(
                    BehaviorEffect(
                        group_id=memory.group_id,
                        character_id=character_id,
                        effect=scaled_effect,
                        source_memory_id=memory.memory_id,
                        hidden=memory.hidden,
                    )
                )
                patches.append(
                    ReversiblePatch(
                        patch_id=f"patch-{memory.memory_id}-{character_id}",
                        character_id=character_id,
                        reverse_effect={key: round(-value, 4) for key, value in scaled_effect.items()},
                        source_memory_id=memory.memory_id,
                    )
                )
                logs.append(
                    GroupMemoryPropagationLog(
                        memory_id=memory.memory_id,
                        group_id=memory.group_id,
                        character_id=character_id,
                        status="applied",
                    )
                )

        return GroupMemoryGraph(
            groups=request.groups,
            memberships=request.memberships,
            group_memories=request.group_memories,
            behavior_effects=behavior_effects,
            propagation_logs=logs,
            reversible_patches=patches,
        )

    def _in_chapter_range(self, chapter_index: int | None, *, start: int | None, end: int | None) -> bool:
        if chapter_index is None:
            return True
        lower = 1 if start is None else start
        if chapter_index < lower:
            return False
        if end is not None and chapter_index > end:
            return False
        return True
