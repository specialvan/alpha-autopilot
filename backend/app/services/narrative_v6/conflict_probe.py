from __future__ import annotations

from collections import defaultdict
from itertools import islice
from typing import Any

from .schemas import (
    ConflictCandidate,
    EmergentConflictProbeRequest,
    EmergentConflictProbeResult,
    InformationLeak,
    InteractionRound,
)


class EmergentConflictProbeService:
    def probe(self, request: EmergentConflictProbeRequest) -> EmergentConflictProbeResult:
        characters = request.characters
        if len(characters) < 2:
            return EmergentConflictProbeResult(
                interaction_rounds=[],
                conflict_candidates=[],
                information_leaks=[],
                relationship_changes=[],
                recommended_plot_hooks=[],
                six_step_binding_suggestions={},
                risk_flags=["insufficient-characters"],
            )

        edge_index = self._build_edge_index(request.relationship_graph_input)
        group_effect = self._group_effect_index(request)

        rounds: list[InteractionRound] = []
        candidates_by_key: dict[str, ConflictCandidate] = {}
        leaks: list[InformationLeak] = []
        relationship_changes: list[dict[str, Any]] = []

        for round_index in range(1, request.rounds + 1):
            exchanges: list[dict[str, Any]] = []
            for idx, actor in enumerate(characters):
                target = characters[(idx + round_index) % len(characters)]
                if actor.character_id == target.character_id:
                    continue

                relation_type, intensity = self._relation_between(actor.character_id, target.character_id, edge_index)
                pressure = self._infer_pressure(request.scene_constraints, actor.character_id, group_effect)
                tension = self._calc_tension(
                    intensity=intensity,
                    stress=actor.emotion_slider_map.stress_baseline,
                    pressure=pressure,
                    round_index=round_index,
                )
                exchange = {
                    "speaker": actor.character_id,
                    "target": target.character_id,
                    "relation": relation_type,
                    "pressure": pressure,
                    "tension": round(tension, 4),
                    "summary": (
                        f"{actor.name} 在 {pressure} 下对 {target.name} 发起试探，"
                        f"关系类型={relation_type}"
                    ),
                }
                exchanges.append(exchange)

                if tension >= 0.72:
                    key = f"{actor.character_id}->{target.character_id}:{relation_type}:{pressure}"
                    candidates_by_key[key] = ConflictCandidate(
                        summary=(
                            f"{actor.name} 与 {target.name} 在 {pressure} 场景下触发"
                            f"{relation_type} 冲突"
                        ),
                        trigger_characters=[actor.character_id, target.character_id],
                        trigger_relationship=relation_type,
                        trigger_personality=actor.function_type.value,
                        trigger_pressure=pressure,
                        confidence=round(min(0.98, tension), 4),
                    )
                    relationship_changes.append(
                        {
                            "source": actor.character_id,
                            "target": target.character_id,
                            "relation": relation_type,
                            "delta_tension": round(min(0.35, tension - 0.5), 4),
                        }
                    )

                leak = self._maybe_leak(actor.character_id, actor.function_type.value, pressure, tension)
                if leak is not None:
                    leaks.append(leak)

            rounds.append(InteractionRound(round_index=round_index, exchanges=exchanges))

        candidates = sorted(candidates_by_key.values(), key=lambda item: item.confidence, reverse=True)
        hooks = [item.summary for item in islice(candidates, 0, 3)]
        risk_flags = self._risk_flags(candidates, leaks)

        return EmergentConflictProbeResult(
            interaction_rounds=rounds,
            conflict_candidates=candidates,
            information_leaks=leaks,
            relationship_changes=relationship_changes,
            recommended_plot_hooks=hooks,
            six_step_binding_suggestions=self._build_six_step_suggestions(candidates),
            risk_flags=risk_flags,
        )

    def _build_edge_index(
        self,
        relationship_graph_input: dict[str, Any] | None,
    ) -> dict[tuple[str, str], tuple[str, float]]:
        index: dict[tuple[str, str], tuple[str, float]] = {}
        edges = []
        if isinstance(relationship_graph_input, dict):
            edges = relationship_graph_input.get("edges", [])
        if not isinstance(edges, list):
            return index

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("from", "")).strip()
            target = str(edge.get("to", "")).strip()
            relation = str(edge.get("relation_type", "ally")).strip() or "ally"
            intensity = self._safe_float(edge.get("intensity"), default=0.5)
            if not source or not target:
                continue
            index[(source, target)] = (relation, intensity)
            if bool(edge.get("bidirectional", True)):
                index[(target, source)] = (relation, intensity)
        return index

    def _group_effect_index(self, request: EmergentConflictProbeRequest) -> dict[str, float]:
        score_by_character: dict[str, float] = defaultdict(float)
        graph = request.group_memory_graph
        if graph is None:
            return score_by_character

        for effect in graph.behavior_effects:
            score_by_character[effect.character_id] += abs(float(effect.effect.get("alertness", 0.0)))
            score_by_character[effect.character_id] += abs(float(effect.effect.get("hostility", 0.0)))
        return score_by_character

    def _relation_between(
        self,
        source: str,
        target: str,
        edge_index: dict[tuple[str, str], tuple[str, float]],
    ) -> tuple[str, float]:
        relation, intensity = edge_index.get((source, target), ("ally", 0.5))
        return relation, max(0.0, min(1.0, intensity))

    def _infer_pressure(
        self,
        scene_constraints: dict[str, Any],
        character_id: str,
        group_effect: dict[str, float],
    ) -> str:
        scene = str(scene_constraints.get("current_event", "scene_conflict")).strip() or "scene_conflict"
        alertness = group_effect.get(character_id, 0.0)
        if alertness >= 0.25:
            return f"{scene}+group_alert"
        return scene

    def _calc_tension(self, *, intensity: float, stress: float, pressure: str, round_index: int) -> float:
        stress_factor = max(0.0, min(1.0, (stress + 10.0) / 20.0))
        pressure_boost = 0.08 if "alert" in pressure else 0.03
        tension = intensity * 0.55 + stress_factor * 0.35 + pressure_boost + round_index * 0.01
        return max(0.0, min(1.0, tension))

    def _maybe_leak(
        self,
        character_id: str,
        function_type: str,
        pressure: str,
        tension: float,
    ) -> InformationLeak | None:
        if function_type != "disguise":
            return None
        if tension < 0.76:
            return None
        return InformationLeak(
            source_character=character_id,
            leaked_information=f"{character_id} 在 {pressure} 下暴露隐藏动机片段",
            risk="hidden_identity_exposure",
        )

    def _build_six_step_suggestions(self, candidates: list[ConflictCandidate]) -> dict[str, str]:
        if not candidates:
            return {
                "encounter_event": "补充高压触发事件后再探测冲突",
                "action_climax": "当前冲突不足以构成高潮",
            }
        top = candidates[0]
        return {
            "encounter_event": top.summary,
            "obstacle": f"{top.trigger_relationship}+{top.trigger_pressure}",
            "action_climax": "将最高置信冲突绑定到 action_climax",
            "resolution": "以代价型和解或局部胜利收束",
        }

    def _risk_flags(self, candidates: list[ConflictCandidate], leaks: list[InformationLeak]) -> list[str]:
        flags: list[str] = []
        if not candidates:
            flags.append("no-conflict-detected")
        if len(candidates) >= 4:
            flags.append("conflict-overload-risk")
        if leaks:
            flags.append("information-leak-risk")
        return flags

    def _safe_float(self, value: object, *, default: float) -> float:
        try:
            return float(value)  # type: ignore[arg-type]
        except Exception:
            return default
