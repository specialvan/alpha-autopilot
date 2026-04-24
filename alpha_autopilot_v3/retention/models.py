from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetentionTargetFunction:
    name: str
    primary_objective: str
    priority_order: list[str]
    guardrails: list[str] = field(default_factory=list)
    description: str = ""


@dataclass(frozen=True)
class RetentionMetrics:
    chapter_attraction_score: float
    continue_reading_intent: float
    emotional_drive: float
    pacing_drive: float
    suspense_drive: float
    conflict_drive: float
    hook_strength: float
    template_risk: float
    evidence: dict[str, Any] = field(default_factory=dict)
