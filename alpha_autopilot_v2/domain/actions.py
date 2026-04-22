from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NarrativeAction:
    action: str
    delta: dict[str, float]
    explanation: str


@dataclass
class RuleCheck:
    action: str
    status: str
    prerequisites: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    action: NarrativeAction
    rule_check: RuleCheck
    score: float
    details: dict[str, float] = field(default_factory=dict)


@dataclass
class RecommendationResult:
    result: SearchResult
    explanation: str
