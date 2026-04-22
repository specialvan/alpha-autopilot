from __future__ import annotations

from dataclasses import dataclass

from alpha_autopilot_v2.domain import SearchResult


WEIGHTS = {
    "structure_value": 0.28,
    "continuity_safety": 0.22,
    "emotional_payoff": 0.20,
    "foreshadow_balance": 0.18,
    "stage_fit": 0.12,
}


@dataclass
class EvaluationService:
    def score_details(self, details: dict[str, float]) -> float:
        total = 0.0
        denom = 0.0
        for key, weight in WEIGHTS.items():
            if key not in details:
                continue
            total += _clamp01(float(details[key])) * weight
            denom += weight
        if denom == 0.0:
            return 0.0
        score = total / denom
        if "feasibility" in details:
            score *= max(0.6, _clamp01(float(details["feasibility"])))
        return round(score, 4)

    def rank(self, results: list[SearchResult]) -> list[SearchResult]:
        for result in results:
            result.score = self.score_details(result.details)
        return sorted(results, key=lambda item: item.score, reverse=True)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
