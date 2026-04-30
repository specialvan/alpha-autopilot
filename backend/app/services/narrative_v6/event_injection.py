from __future__ import annotations

from datetime import datetime, timezone

from .schemas import (
    EventInjectionRequest,
    EventInjectionResult,
    ParallelPlotSimulationResult,
    SimulationPath,
)


class EventInjectionService:
    def inject(
        self,
        simulation: ParallelPlotSimulationResult,
        request: EventInjectionRequest,
    ) -> EventInjectionResult:
        old_ranks = self._rank_snapshot(simulation.paths)
        updated_paths: list[SimulationPath] = []
        macro_risk: list[str] = []

        for path in simulation.paths:
            if path.status != "ok":
                updated_paths.append(path.model_copy(deep=True))
                continue

            updated = path.model_copy(deep=True)
            score_delta = self._score_delta(path.strategy, request)
            updated.retention_score = round(self._clamp(0.0, 1.0, updated.retention_score + score_delta), 4)
            updated.character_reactions.append(
                {
                    "character_id": "event_injection",
                    "reaction": (
                        f"event={request.injected_event.event_type};"
                        f"desc={request.injected_event.description}"
                    ),
                    "emotion_shift": "recompute",
                }
            )

            if request.injected_event.force_level >= 0.85:
                updated.risk_flags.append("event-force-high")
            if self._violates_author_intent(request):
                updated.risk_flags.append("author-intent-violation")
            if self._macro_structure_risky(request):
                macro_risk.append("macro-structure-break-risk")
            updated_paths.append(updated)

        winner_path_id = self._rerank(updated_paths)
        ranking_changes = self._build_ranking_changes(old_ranks, updated_paths)
        previous_winner = simulation.winner_path_id
        destructive_confirmation_required = self._destructive_confirmation_required(
            request=request,
            previous_winner=previous_winner,
            winner_path_id=winner_path_id,
        )

        decision_summary = (
            f"Injected event={request.injected_event.event_type} force={request.injected_event.force_level:.2f}; "
            f"winner changed {previous_winner} -> {winner_path_id}."
        )
        updated_simulation = simulation.model_copy(deep=True)
        updated_simulation.paths = updated_paths
        updated_simulation.winner_path_id = winner_path_id
        updated_simulation.decision_summary = decision_summary
        updated_simulation.generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        updated_simulation.risk_flags = sorted(set(updated_simulation.risk_flags + macro_risk))

        audit_log = [
            {
                "at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "event_id": request.injected_event.event_id,
                "event_type": request.injected_event.event_type,
                "force_level": request.injected_event.force_level,
                "previous_winner": previous_winner,
                "winner": winner_path_id,
                "affected_characters": request.injected_event.affected_characters,
            }
        ]

        return EventInjectionResult(
            simulation_id=simulation.simulation_id,
            previous_winner_path_id=previous_winner,
            winner_path_id=winner_path_id,
            updated_paths=updated_paths,
            ranking_changes=ranking_changes,
            macro_structure_risk=sorted(set(macro_risk)),
            destructive_confirmation_required=destructive_confirmation_required,
            audit_log=audit_log,
            decision_summary=decision_summary,
            updated_simulation=updated_simulation,
        )

    def _score_delta(self, strategy: str, request: EventInjectionRequest) -> float:
        event_type = request.injected_event.event_type.lower()
        force = request.injected_event.force_level

        if strategy == "suspense_first":
            if event_type in {"secret_reveal", "betrayal", "ambush"}:
                return 0.12 * force
            return -0.06 * force
        if strategy == "relationship_burst":
            if event_type in {"war", "betrayal", "death", "duel"}:
                return 0.1 * force
            return -0.03 * force
        if strategy == "retention_first":
            return 0.05 * force if event_type not in {"filler"} else -0.08 * force
        return 0.02 * force

    def _rank_snapshot(self, paths: list[SimulationPath]) -> dict[str, int]:
        ranked = sorted(
            [path for path in paths if path.status == "ok"],
            key=lambda item: item.retention_score,
            reverse=True,
        )
        return {path.path_id: idx for idx, path in enumerate(ranked, start=1)}

    def _rerank(self, paths: list[SimulationPath]) -> str | None:
        ranked = sorted(
            [path for path in paths if path.status == "ok"],
            key=lambda item: item.retention_score,
            reverse=True,
        )
        if not ranked:
            return None
        for idx, path in enumerate(ranked, start=1):
            path.recommendation_rank = idx
        return ranked[0].path_id

    def _build_ranking_changes(
        self,
        old_ranks: dict[str, int],
        paths: list[SimulationPath],
    ) -> list[dict[str, object]]:
        new_ranks = self._rank_snapshot(paths)
        changes: list[dict[str, object]] = []
        for path_id, new_rank in new_ranks.items():
            old_rank = old_ranks.get(path_id)
            if old_rank != new_rank:
                changes.append(
                    {
                        "path_id": path_id,
                        "old_rank": old_rank,
                        "new_rank": new_rank,
                    }
                )
        return changes

    def _violates_author_intent(self, request: EventInjectionRequest) -> bool:
        intent = request.author_intent
        forbid_death = bool(intent.get("forbid_character_death", False))
        if not forbid_death:
            return False
        return request.injected_event.event_type.lower() in {"death", "execution"}

    def _macro_structure_risky(self, request: EventInjectionRequest) -> bool:
        structure = request.macro_story_structure.lower()
        force = request.injected_event.force_level
        if structure == "anthology" and force >= 0.8:
            return True
        if structure == "hub_and_spoke" and force >= 0.9:
            return True
        return False

    def _destructive_confirmation_required(
        self,
        *,
        request: EventInjectionRequest,
        previous_winner: str | None,
        winner_path_id: str | None,
    ) -> bool:
        if request.injected_event.force_level >= 0.9:
            return True
        if previous_winner != winner_path_id:
            return True
        return False

    def _clamp(self, low: float, high: float, value: float) -> float:
        return max(low, min(high, value))
