from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4

from .scoring import score_simulation_path
from .schemas import ParallelPlotSimulationResult, ParallelSimulationRequest, SimulationPath


_DEFAULT_STRATEGIES: tuple[str, ...] = (
    "retention_first",
    "suspense_first",
    "relationship_burst",
)


class ParallelPlotSimulationService:
    def run(
        self,
        request: ParallelSimulationRequest,
        *,
        graph_rag_hints: list[str] | None = None,
    ) -> ParallelPlotSimulationResult:
        simulation_id = request.simulation_id or f"sim-{uuid4().hex[:12]}"
        strategies = self._resolve_strategies(request)
        normalized_hints = [item.strip() for item in (graph_rag_hints or []) if item and item.strip()]
        paths: list[SimulationPath] = []

        for index, strategy in enumerate(strategies, start=1):
            path_id = f"{simulation_id}-path-{index}"
            try:
                if strategy in request.debug_force_fail_strategies:
                    raise RuntimeError(f"forced failure for strategy: {strategy}")

                path = self._simulate_path(
                    path_id=path_id,
                    strategy=strategy,
                    request=request,
                    graph_rag_hints=normalized_hints,
                )
                paths.append(path)
            except Exception as exc:
                paths.append(
                    SimulationPath(
                        path_id=path_id,
                        strategy=strategy,
                        status="failed",
                        error_message=str(exc),
                        risk_flags=["path_generation_failed"],
                    )
                )

        winner_path_id = self._rank_paths(paths)
        decision_summary = self._build_decision_summary(paths, winner_path_id=winner_path_id)
        risk_flags = self._aggregate_risk_flags(paths)

        return ParallelPlotSimulationResult(
            simulation_id=simulation_id,
            paths=paths,
            winner_path_id=winner_path_id,
            decision_summary=decision_summary,
            generated_at_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            risk_flags=risk_flags,
        )

    def _resolve_strategies(self, request: ParallelSimulationRequest) -> list[str]:
        strategies = [item.strip() for item in request.strategies if item.strip()]
        if not strategies:
            strategies = list(_DEFAULT_STRATEGIES)

        while len(strategies) < request.path_count:
            strategies.append(_DEFAULT_STRATEGIES[len(strategies) % len(_DEFAULT_STRATEGIES)])
        return strategies[: request.path_count]

    def _simulate_path(
        self,
        *,
        path_id: str,
        strategy: str,
        request: ParallelSimulationRequest,
        graph_rag_hints: list[str],
    ) -> SimulationPath:
        top_character = request.character_profiles[0] if request.character_profiles else None
        top_relationship = request.narrative_seed.relationship_triples[0] if request.narrative_seed.relationship_triples else None

        relationship_trigger = (
            f"{top_relationship.subject}->{top_relationship.target}:{top_relationship.relation}"
            if top_relationship is not None
            else "relationship-signal-missing"
        )
        personality_choice = top_character.function_type.value if top_character is not None else "unknown"
        external_pressure = (
            request.narrative_seed.plot_events[0].event
            if request.narrative_seed.plot_events
            else "pressure-not-detected"
        )

        initial_assumptions = [
            f"macro_structure={request.macro_story_structure}",
            f"strategy={strategy}",
            f"seed_characters={len(request.narrative_seed.characters)}",
        ]
        if graph_rag_hints:
            initial_assumptions.append(f"graph_rag_hints={len(graph_rag_hints)}")
        plot_outline = self._build_plot_outline(strategy, request)
        six_step = self._build_six_step_mapping(plot_outline, request=request)
        character_reactions = self._build_character_reactions(request.character_profiles, strategy)
        relationship_deltas = self._build_relationship_deltas(request.narrative_seed.relationship_triples, strategy)
        memory_deltas = self._build_memory_deltas(request.narrative_seed.open_threads, strategy)
        consistency_issues = self._build_consistency_issues(request.character_profiles)
        risk_flags = self._build_risk_flags(
            strategy=strategy,
            consistency_issues=consistency_issues,
            open_threads=request.narrative_seed.open_threads,
        )
        retention_score, retention_breakdown = score_simulation_path(
            strategy=strategy,
            plot_outline=plot_outline,
            relationship_deltas=relationship_deltas,
            consistency_issues=consistency_issues,
            risk_flags=risk_flags,
            retention_desire_vector=request.retention_desire_vector,
        )

        return SimulationPath(
            path_id=path_id,
            strategy=strategy,
            status="ok",
            initial_assumptions=initial_assumptions,
            plot_outline=plot_outline,
            six_step_scaffold_mapping=six_step,
            character_reactions=character_reactions,
            relationship_deltas=relationship_deltas,
            memory_deltas=memory_deltas,
            retention_score=retention_score,
            retention_breakdown=retention_breakdown,
            consistency_issues=consistency_issues,
            risk_flags=risk_flags,
            causal_chain={
                "relationship_trigger": relationship_trigger,
                "personality_choice": personality_choice,
                "external_pressure": external_pressure,
            },
            graph_rag_hints=graph_rag_hints[:3],
        )

    def _build_plot_outline(self, strategy: str, request: ParallelSimulationRequest) -> list[str]:
        if request.plot_unit_scaffold is not None:
            scaffold = request.plot_unit_scaffold
            return [
                scaffold.encounter_event,
                scaffold.obstacle,
                scaffold.solution_method,
                scaffold.action_climax.node,
                scaffold.resolution,
            ]

        base_seed = request.narrative_seed
        open_thread_text = base_seed.open_threads[0].thread if base_seed.open_threads else "悬念待补"

        if strategy == "suspense_first":
            return [
                "线索先曝光一半，制造误导",
                "关键角色在压力下隐藏真实动机",
                "中段揭露信息差并升级误会",
                f"尾段回钩未解线程：{open_thread_text}",
            ]

        if strategy == "relationship_burst":
            return [
                "关系边先发生位移并触发立场冲突",
                "角色在底线被触及时做出高风险选择",
                "外部压力放大，导致联盟重组",
                "结尾给出可兑现但有代价的下一步",
            ]

        return [
            "开场直接给读者兑现一个短爽点",
            "中段抛出反转线索并扩展代价",
            "冲突升级后触发角色选择分叉",
            f"尾段保留下一章钩子：{open_thread_text}",
        ]

    def _build_six_step_mapping(
        self,
        outline: list[str],
        *,
        request: ParallelSimulationRequest,
    ) -> dict[str, str]:
        if request.plot_unit_scaffold is not None:
            scaffold = request.plot_unit_scaffold
            return {
                "encounter_event": scaffold.encounter_event,
                "desire_goal": scaffold.desire_goal,
                "obstacle": scaffold.obstacle,
                "solution_method": scaffold.solution_method,
                "action_climax": scaffold.action_climax.node,
                "action_climax_turn_type": scaffold.action_climax.turn_type.value,
                "resolution": scaffold.resolution,
            }

        head = outline + ["待补足"] * max(0, 4 - len(outline))
        return {
            "encounter_event": head[0],
            "desire_goal": "角色希望保住主导权并推进主线",
            "obstacle": head[1],
            "solution_method": head[2],
            "action_climax": head[3],
            "resolution": "留下可执行但有代价的后续选择",
        }

    def _build_character_reactions(self, profiles: Iterable, strategy: str) -> list[dict[str, str]]:
        reactions: list[dict[str, str]] = []
        for profile in profiles:
            if strategy == "suspense_first":
                emotion_shift = "压抑 -> 警觉"
            elif strategy == "relationship_burst":
                emotion_shift = "克制 -> 爆发"
            else:
                emotion_shift = "稳定 -> 进攻"
            reactions.append(
                {
                    "character_id": profile.character_id,
                    "reaction": f"{profile.name} 依据 {profile.function_type.value} 站位做出决策",
                    "emotion_shift": emotion_shift,
                }
            )
        return reactions

    def _build_relationship_deltas(self, triples: Iterable, strategy: str) -> list[dict[str, object]]:
        delta_value = {
            "retention_first": 0.06,
            "suspense_first": 0.09,
            "relationship_burst": 0.14,
        }.get(strategy, 0.05)
        deltas: list[dict[str, object]] = []
        for triple in triples:
            deltas.append(
                {
                    "subject": triple.subject,
                    "target": triple.target,
                    "relation": triple.relation,
                    "delta_tension": round(delta_value, 4),
                }
            )
        return deltas

    def _build_memory_deltas(self, open_threads: Iterable, strategy: str) -> list[dict[str, object]]:
        update_mode = "amplify" if strategy == "suspense_first" else "stabilize"
        deltas: list[dict[str, object]] = []
        for thread in open_threads:
            deltas.append(
                {
                    "thread": thread.thread,
                    "update_mode": update_mode,
                    "confidence": thread.confidence,
                }
            )
        return deltas

    def _build_consistency_issues(self, profiles: Iterable) -> list[str]:
        issues: list[str] = []
        for profile in profiles:
            if profile.confidence < 0.45:
                issues.append(f"{profile.character_id}:low-profile-confidence")
            if profile.emotion_slider_map.stress_baseline > 8.5:
                issues.append(f"{profile.character_id}:stress-overload")
        return issues

    def _build_risk_flags(
        self,
        *,
        strategy: str,
        consistency_issues: list[str],
        open_threads: list,
    ) -> list[str]:
        risk_flags: list[str] = []
        if consistency_issues:
            risk_flags.append("consistency-warning")
        if strategy == "suspense_first" and len(open_threads) <= 1:
            risk_flags.append("hook-density-risk")
        return risk_flags

    def _rank_paths(self, paths: list[SimulationPath]) -> str | None:
        success_paths = [path for path in paths if path.status == "ok"]
        if not success_paths:
            return None

        ranked = sorted(success_paths, key=lambda item: item.retention_score, reverse=True)
        for rank, path in enumerate(ranked, start=1):
            path.recommendation_rank = rank

        # If the top path carries hard consistency risks, pick next safe candidate.
        for path in ranked:
            if "critical-consistency" in path.risk_flags:
                continue
            return path.path_id
        return ranked[0].path_id

    def _build_decision_summary(self, paths: list[SimulationPath], *, winner_path_id: str | None) -> str:
        total = len(paths)
        ok_count = len([path for path in paths if path.status == "ok"])
        failed = total - ok_count

        if winner_path_id is None:
            return (
                f"Simulation produced {total} paths but no valid winner (failed_paths={failed}). "
                "Fallback to baseline recommendation is required."
            )

        winner = next((path for path in paths if path.path_id == winner_path_id), None)
        winner_score = winner.retention_score if winner is not None else 0.0
        return (
            f"Simulation generated {ok_count}/{total} valid paths. "
            f"Winner={winner_path_id} (retention_score={winner_score:.4f}). "
            "Decision keeps V3 retention ordering while exposing alternatives."
        )

    def _aggregate_risk_flags(self, paths: Iterable[SimulationPath]) -> list[str]:
        merged: set[str] = set()
        for path in paths:
            merged.update(path.risk_flags)
        return sorted(merged)
