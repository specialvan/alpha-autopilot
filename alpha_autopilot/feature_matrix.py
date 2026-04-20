from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .narrative import StoryState


FEATURE_NAMES = [
    "conflict_push",
    "emotion_payoff",
    "hook_strength",
    "continuity_safety",
    "character_focus",
    "foreshadowing_value",
    "tempo_fit",
]


@dataclass
class FeatureMatrix:
    weights: Dict[str, float] = field(default_factory=lambda: {name: 1.0 for name in FEATURE_NAMES})
    bias: float = 0.0

    def score(self, state: StoryState, features: Dict[str, float]) -> float:
        total = self.bias
        for name, value in features.items():
            total += self.weights.get(name, 0.0) * value
        total += 0.15 * state.conflict_intensity
        total += 0.10 * state.emotional_temperature
        total += 0.10 * state.mainline_progress
        return total

    def update_from_feedback(self, features: Dict[str, float], target: float, prediction: float, lr: float = 0.1) -> None:
        error = target - prediction
        for name, value in features.items():
            self.weights[name] = self.weights.get(name, 0.0) + lr * error * value
        self.bias += lr * error

    @classmethod
    def from_samples(cls, samples: Iterable[Dict[str, float]]) -> "FeatureMatrix":
        matrix = cls()
        counts = {name: 0.0 for name in FEATURE_NAMES}
        totals = {name: 0.0 for name in FEATURE_NAMES}
        for sample in samples:
            for name in FEATURE_NAMES:
                value = sample.get(name, 0.0)
                totals[name] += value
                counts[name] += 1.0
        for name in FEATURE_NAMES:
            if counts[name]:
                matrix.weights[name] = 0.5 + totals[name] / counts[name]
        return matrix
