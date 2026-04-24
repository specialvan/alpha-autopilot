from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..retention.models import RetentionMetrics, RetentionTargetFunction


@dataclass(frozen=True)
class GenerationControlPlan:
    target_function: RetentionTargetFunction
    retention_metrics: RetentionMetrics
    focus_mode: str
    emotional_curve: str
    pacing_curve: str
    suspense_curve: str
    conflict_curve: str
    hook_strategy: str
    anti_pattern_warnings: list[str] = field(default_factory=list)
    decision_tags: dict[str, Any] = field(default_factory=dict)
    suggestions: dict[str, Any] = field(default_factory=dict)
