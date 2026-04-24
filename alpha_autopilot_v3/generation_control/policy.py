from __future__ import annotations

from .mapping import build_decision_tags, build_generation_control_suggestions
from .models import GenerationControlPlan
from ..decomposition.models import ChapterDecompositionRecord
from ..retention.metrics import build_retention_metrics
from ..retention.target_function import build_retention_target_function


def build_generation_control_plan(record: ChapterDecompositionRecord) -> GenerationControlPlan:
    target_function = build_retention_target_function()
    retention_metrics = build_retention_metrics(record)
    decision_tags = build_decision_tags(record, retention_metrics)
    suggestions = build_generation_control_suggestions(record, retention_metrics)

    if retention_metrics.chapter_attraction_score >= 0.75:
        focus_mode = "retain-and-escalate"
        emotional_curve = "high"
        pacing_curve = "brisk"
        suspense_curve = "sustained"
        conflict_curve = "aggressive"
        hook_strategy = "preserve-and-amplify-hook"
    elif retention_metrics.chapter_attraction_score >= 0.5:
        focus_mode = "balance-and-sharpen"
        emotional_curve = "moderate"
        pacing_curve = "balanced"
        suspense_curve = "moderate"
        conflict_curve = "moderate"
        hook_strategy = "strengthen-hook"
    else:
        focus_mode = "repair-and-reframe"
        emotional_curve = "explicit"
        pacing_curve = "tight"
        suspense_curve = "high"
        conflict_curve = "raise-stakes"
        hook_strategy = "force-reader-pull"

    anti_pattern_warnings: list[str] = []
    if retention_metrics.template_risk >= 0.35:
        anti_pattern_warnings.append("template-overfit-risk")
    if retention_metrics.continue_reading_intent < 0.55:
        anti_pattern_warnings.append("weak-reader-pull")
    if retention_metrics.hook_strength < 0.5:
        anti_pattern_warnings.append("weak-hook")

    return GenerationControlPlan(
        target_function=target_function,
        retention_metrics=retention_metrics,
        focus_mode=focus_mode,
        emotional_curve=emotional_curve,
        pacing_curve=pacing_curve,
        suspense_curve=suspense_curve,
        conflict_curve=conflict_curve,
        hook_strategy=hook_strategy,
        anti_pattern_warnings=anti_pattern_warnings,
        decision_tags=decision_tags,
        suggestions={
            **suggestions,
            "focus_mode": focus_mode,
            "emotion": emotional_curve,
            "pace": pacing_curve,
            "suspense": suspense_curve,
            "conflict": conflict_curve,
            "hook": hook_strategy,
        },
    )
