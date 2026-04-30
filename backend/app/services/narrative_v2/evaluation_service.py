from __future__ import annotations

from dataclasses import dataclass, field

from alpha_autopilot_v2.domain import SearchResult, StoryState
from alpha_autopilot_v2.evaluation.service import EvaluationService
from alpha_autopilot_v3.retention.target_function import build_retention_target_function


@dataclass
class NarrativeV2EvaluationService:
    core: EvaluationService = field(default_factory=EvaluationService)

    def score_details(self, details: dict[str, float]) -> float:
        return self.core.score_details(details)

    def rank(self, results: list[SearchResult], state: StoryState | None = None) -> list[SearchResult]:
        ranked = self.core.rank(results)
        if state is None or not ranked:
            return ranked

        target_function = build_retention_target_function()
        priority_weights = _build_priority_weights(
            target_function.priority_order,
            stage=state.stage,
            macro_structure=state.macro_structure,
        )

        for result in ranked:
            base_score = result.score
            retention_score = _retention_score(result, state, priority_weights)
            guardrail_penalty = _guardrail_penalty(result, state, target_function.guardrails)
            adjusted = _clip01(result.score * 0.85 + retention_score * 0.15 - guardrail_penalty)
            result.score = round(adjusted, 4)
            result.details = {
                **result.details,
                "base_score": round(base_score, 4),
                "retention_target_score": round(retention_score, 4),
                "retention_guardrail_penalty": round(guardrail_penalty, 4),
                "retention_weight": 0.15,
            }
        return sorted(ranked, key=lambda item: item.score, reverse=True)

    def build_retention_driver(
        self,
        result: SearchResult | None,
        state: StoryState,
    ) -> dict[str, object] | None:
        if result is None:
            return None

        target_function = build_retention_target_function()
        priority_weights = _build_priority_weights(
            target_function.priority_order,
            stage=state.stage,
            macro_structure=state.macro_structure,
        )
        retention_score = _retention_score(result, state, priority_weights)
        guardrail_penalty = _guardrail_penalty(result, state, target_function.guardrails)
        final_score = _clip01(result.score)
        base_score = _clip01(_detail_number(result.details, "base_score", result.score))

        return {
            "target_function": target_function.name,
            "primary_objective": target_function.primary_objective,
            "priority_order": list(target_function.priority_order),
            "guardrails": list(target_function.guardrails),
            "selected_base_score": round(base_score, 4),
            "selected_retention_score": round(retention_score, 4),
            "selected_guardrail_penalty": round(guardrail_penalty, 4),
            "selected_final_score": round(final_score, 4),
            "control_mode": _control_mode(retention_score, result.action.action),
            "decision_tags": {
                "stage": state.stage,
                "macro_structure": state.macro_structure,
                "action": result.action.action,
                "risk_flags": list(result.rule_check.risk_flags),
                "top_priority": _highest_weight_label(priority_weights),
            },
        }


def _build_priority_weights(
    priority_order: list[str],
    stage: str | None = None,
    macro_structure: str | None = None,
) -> dict[str, float]:
    if not priority_order:
        return {}
    total = sum(range(1, len(priority_order) + 1))
    weights = {
        key: (len(priority_order) - index) / total
        for index, key in enumerate(priority_order)
    }
    if not stage:
        return weights

    staged_weights = {
        key: value * _stage_multiplier(stage, key)
        for key, value in weights.items()
    }
    structure_adjusted_weights = {
        key: value * _macro_structure_multiplier(macro_structure, key)
        for key, value in staged_weights.items()
    }
    staged_total = sum(structure_adjusted_weights.values())
    if staged_total <= 0:
        return weights
    return {key: value / staged_total for key, value in structure_adjusted_weights.items()}


def _retention_score(
    result: SearchResult,
    state: StoryState,
    priority_weights: dict[str, float],
) -> float:
    delta = result.action.delta
    details = result.details
    continue_reading_intent = _clip01(
        0.45 * state.mainline_progress
        + 0.25 * state.conflict_intensity
        + 0.15 * state.payoff_pressure
        + 0.15 * max(0.0, delta.get("mainline_progress", 0.0))
    )
    chapter_attraction = _clip01(
        0.50 * details.get("structure_value", 0.0)
        + 0.20 * details.get("stage_fit", 0.0)
        + 0.30 * continue_reading_intent
    )
    emotional_drive = _clip01(
        0.70 * state.emotional_temperature
        + 0.30 * max(0.0, delta.get("emotional_temperature", 0.0))
    )
    pacing_drive = _clip01(details.get("continuity_safety", 0.0))
    suspense_drive = _clip01(
        0.60 * state.foreshadowing_load + 0.40 * details.get("foreshadow_balance", 0.0)
    )
    conflict_drive = _clip01(
        state.conflict_intensity + max(0.0, delta.get("conflict_intensity", 0.0))
    )
    hook_strength = _clip01(
        state.mainline_progress + max(0.0, delta.get("mainline_progress", 0.0))
    )

    features = {
        "continue-reading-intent": continue_reading_intent,
        "chapter-attraction": chapter_attraction,
        "emotional-drive": emotional_drive,
        "pacing-drive": pacing_drive,
        "suspense-drive": suspense_drive,
        "conflict-drive": conflict_drive,
        "hook-strength": hook_strength,
    }
    weighted = sum(
        features.get(key, 0.0) * weight for key, weight in priority_weights.items()
    )
    return _clip01(weighted)


def _guardrail_penalty(result: SearchResult, state: StoryState, guardrails: list[str]) -> float:
    penalty = 0.0
    if "preserve-structure-constraints" in guardrails and result.details.get("structure_value", 0.0) < 0.40:
        penalty += 0.04
    if "preserve-style-consistency" in guardrails and result.details.get("continuity_safety", 0.0) < 0.40:
        penalty += 0.03
    if "preserve-fact-and-worldstate-constraints" in guardrails and result.details.get("feasibility", 1.0) < 0.70:
        penalty += 0.03
    if "avoid-template-overfit" in guardrails:
        if result.action.action == "open_new_thread" and state.stage in {"mid_late", "late"}:
            penalty += 0.05
    return round(penalty, 4)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _stage_multiplier(stage: str, signal: str) -> float:
    stage_key = stage.strip().lower()
    if stage_key == "opening":
        if signal == "hook-strength":
            return 1.3
        if signal == "suspense-drive":
            return 1.2
    if stage_key == "middle":
        if signal == "conflict-drive":
            return 1.15
        if signal == "pacing-drive":
            return 1.1
    if stage_key in {"mid_late", "late"}:
        if signal == "chapter-attraction":
            return 1.2
        if signal == "emotional-drive":
            return 1.15
    return 1.0


def _control_mode(retention_score: float, action: str) -> str:
    if retention_score >= 0.78 and action in {"push_conflict", "deliver_payoff"}:
        return "retain-and-escalate"
    if retention_score >= 0.58:
        return "balance-and-sharpen"
    return "repair-and-reframe"


def _macro_structure_multiplier(macro_structure: str | None, signal: str) -> float:
    structure_key = (macro_structure or "progressive").strip().lower()
    if structure_key == "hub_and_spoke":
        if signal == "hook-strength":
            return 1.25
        if signal == "suspense-drive":
            return 1.15
        return 1.0
    if structure_key == "anthology":
        if signal == "hook-strength":
            return 0.75
        if signal == "suspense-drive":
            return 0.85
        if signal == "chapter-attraction":
            return 1.2
        return 1.0
    if structure_key == "progressive":
        if signal == "conflict-drive":
            return 1.1
        if signal == "chapter-attraction":
            return 1.05
    return 1.0


def _highest_weight_label(weights: dict[str, float]) -> str:
    if not weights:
        return "none"
    return max(weights.items(), key=lambda item: item[1])[0]


def _detail_number(details: dict[str, float], key: str, fallback: float) -> float:
    value = details.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    return fallback
