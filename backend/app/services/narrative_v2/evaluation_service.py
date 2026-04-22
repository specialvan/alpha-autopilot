from __future__ import annotations

from dataclasses import dataclass, field

from alpha_autopilot_v2.domain import SearchResult
from alpha_autopilot_v2.evaluation.service import EvaluationService


@dataclass
class NarrativeV2EvaluationService:
    core: EvaluationService = field(default_factory=EvaluationService)

    def score_details(self, details: dict[str, float]) -> float:
        return self.core.score_details(details)

    def rank(self, results: list[SearchResult]) -> list[SearchResult]:
        return self.core.rank(results)
