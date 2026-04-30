from __future__ import annotations

from typing import Any

from ..decomposition.models import ChapterDecompositionRecord
from ..retention.models import RetentionDesireVector, RetentionMetrics


DESIRE_HOOK_STRATEGY_MAP: dict[str, str] = {
    "primal_desire": "escalate-power-survival-and-reward-hook",
    "value_recognition": "highlight-proof-recognition-and-status-reversal-hook",
    "knowledge_curiosity": "strengthen-rule-discovery-and-causal-payoff-hook",
    "information_gap": "expand-information-gap-with-controlled-reveal-hook",
}


def resolve_desire_hook_strategy(
    desire_vector: RetentionDesireVector | None,
) -> str | None:
    if desire_vector is None or not desire_vector.dominant:
        return None
    return DESIRE_HOOK_STRATEGY_MAP.get(desire_vector.dominant)


def build_decision_tags(
    record: ChapterDecompositionRecord,
    metrics: RetentionMetrics,
    desire_vector: RetentionDesireVector | None = None,
) -> dict[str, Any]:
    tags = {
        "chapter_function": record.primary_function,
        "stage": record.stage,
        "genre": record.genre,
        "retention_score": metrics.chapter_attraction_score,
        "continue_reading_intent": metrics.continue_reading_intent,
        "hook_strength": metrics.hook_strength,
        "suspense_drive": metrics.suspense_drive,
        "conflict_drive": metrics.conflict_drive,
        "template_risk": metrics.template_risk,
    }
    if desire_vector is not None and desire_vector.dominant:
        tags["desire_dominant"] = desire_vector.dominant
        tags["desire_hook_strategy"] = (
            resolve_desire_hook_strategy(desire_vector) or "fallback-desire-hook"
        )
    return tags


def build_generation_control_suggestions(
    record: ChapterDecompositionRecord,
    metrics: RetentionMetrics,
    desire_vector: RetentionDesireVector | None = None,
) -> dict[str, Any]:
    suggestions: dict[str, Any] = {}

    if metrics.hook_strength >= 0.7:
        suggestions["opening"] = "keep-opening-sharp"
    else:
        suggestions["opening"] = "strengthen-opening-hook"

    if metrics.suspense_drive >= 0.7:
        suggestions["middle"] = "delay-reveal-and-sustain-pressure"
    else:
        suggestions["middle"] = "increase-information-withholding"

    if metrics.conflict_drive >= 0.7:
        suggestions["escalation"] = "push-conflict-forward"
    else:
        suggestions["escalation"] = "raise-conflict-stakes"

    if metrics.template_risk >= 0.35:
        suggestions["risk"] = "avoid-template-overfit"
    else:
        suggestions["risk"] = "retain-structure-with-flexibility"

    if record.primary_function == "transition-breathing":
        suggestions["pace"] = "compress-exposition-and-inject-hook"
    if desire_vector is not None and desire_vector.dominant:
        suggestions["desire_hook"] = (
            resolve_desire_hook_strategy(desire_vector) or "fallback-desire-hook"
        )
        suggestions["desire_dominant"] = desire_vector.dominant

    return suggestions
