from __future__ import annotations

from typing import Any

from ..decomposition.models import ChapterDecompositionRecord
from ..retention.models import RetentionMetrics


def build_decision_tags(record: ChapterDecompositionRecord, metrics: RetentionMetrics) -> dict[str, Any]:
    return {
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


def build_generation_control_suggestions(record: ChapterDecompositionRecord, metrics: RetentionMetrics) -> dict[str, Any]:
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

    return suggestions
