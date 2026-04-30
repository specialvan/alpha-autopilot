from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RetentionDesireDominant(str, Enum):
    PRIMAL_DESIRE = "primal_desire"
    VALUE_RECOGNITION = "value_recognition"
    KNOWLEDGE_CURIOSITY = "knowledge_curiosity"
    INFORMATION_GAP = "information_gap"


@dataclass(frozen=True)
class RetentionDesireVector:
    primal_desire: float = 0.25
    value_recognition: float = 0.25
    knowledge_curiosity: float = 0.25
    information_gap: float = 0.25
    dominant: str | None = None

    @classmethod
    def with_auto_dominant(
        cls,
        *,
        primal_desire: float,
        value_recognition: float,
        knowledge_curiosity: float,
        information_gap: float,
        dominant_override: str | None = None,
    ) -> "RetentionDesireVector":
        if dominant_override:
            dominant = dominant_override
        else:
            ordered = [
                (RetentionDesireDominant.PRIMAL_DESIRE.value, primal_desire),
                (RetentionDesireDominant.VALUE_RECOGNITION.value, value_recognition),
                (RetentionDesireDominant.KNOWLEDGE_CURIOSITY.value, knowledge_curiosity),
                (RetentionDesireDominant.INFORMATION_GAP.value, information_gap),
            ]
            dominant = max(ordered, key=lambda item: item[1])[0]

        return cls(
            primal_desire=primal_desire,
            value_recognition=value_recognition,
            knowledge_curiosity=knowledge_curiosity,
            information_gap=information_gap,
            dominant=dominant,
        )


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
