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

GENRE_WEIGHTS = {
    "suspense": {
        "conflict_push": 1.25,
        "emotion_payoff": 0.95,
        "hook_strength": 1.30,
        "continuity_safety": 1.05,
        "character_focus": 0.90,
        "foreshadowing_value": 1.28,
        "tempo_fit": 1.10,
    },
    "romance": {
        "conflict_push": 0.92,
        "emotion_payoff": 1.30,
        "hook_strength": 1.05,
        "continuity_safety": 1.10,
        "character_focus": 1.28,
        "foreshadowing_value": 0.94,
        "tempo_fit": 1.00,
    },
    "power": {
        "conflict_push": 1.18,
        "emotion_payoff": 1.00,
        "hook_strength": 1.12,
        "continuity_safety": 1.08,
        "character_focus": 1.06,
        "foreshadowing_value": 1.20,
        "tempo_fit": 1.02,
    },
    "daily": {
        "conflict_push": 0.88,
        "emotion_payoff": 1.10,
        "hook_strength": 0.94,
        "continuity_safety": 1.22,
        "character_focus": 1.16,
        "foreshadowing_value": 0.88,
        "tempo_fit": 1.08,
    },
    "xianxia": {
        "conflict_push": 1.15,
        "emotion_payoff": 1.00,
        "hook_strength": 1.10,
        "continuity_safety": 1.06,
        "character_focus": 1.00,
        "foreshadowing_value": 1.22,
        "tempo_fit": 1.05,
    },
}

TONE_WEIGHTS = {
    "fast": {
        "conflict_push": 1.15,
        "emotion_payoff": 0.90,
        "hook_strength": 1.22,
        "continuity_safety": 0.96,
        "character_focus": 0.92,
        "foreshadowing_value": 1.10,
        "tempo_fit": 1.18,
    },
    "balanced": {
        "conflict_push": 1.00,
        "emotion_payoff": 1.00,
        "hook_strength": 1.00,
        "continuity_safety": 1.05,
        "character_focus": 1.00,
        "foreshadowing_value": 1.00,
        "tempo_fit": 1.00,
    },
    "slow": {
        "conflict_push": 0.92,
        "emotion_payoff": 1.12,
        "hook_strength": 0.90,
        "continuity_safety": 1.15,
        "character_focus": 1.14,
        "foreshadowing_value": 1.06,
        "tempo_fit": 0.92,
    },
}

STAGE_WEIGHTS = {
    "opening": {
        "conflict_push": 1.12,
        "emotion_payoff": 0.92,
        "hook_strength": 1.20,
        "continuity_safety": 1.00,
        "character_focus": 0.96,
        "foreshadowing_value": 1.08,
        "tempo_fit": 1.15,
    },
    "middle": {
        "conflict_push": 1.00,
        "emotion_payoff": 1.00,
        "hook_strength": 1.00,
        "continuity_safety": 1.05,
        "character_focus": 1.02,
        "foreshadowing_value": 1.12,
        "tempo_fit": 1.00,
    },
    "mid_late": {
        "conflict_push": 1.06,
        "emotion_payoff": 1.08,
        "hook_strength": 1.02,
        "continuity_safety": 1.08,
        "character_focus": 1.00,
        "foreshadowing_value": 1.18,
        "tempo_fit": 0.98,
    },
    "late": {
        "conflict_push": 0.96,
        "emotion_payoff": 1.16,
        "hook_strength": 0.96,
        "continuity_safety": 1.20,
        "character_focus": 1.04,
        "foreshadowing_value": 0.96,
        "tempo_fit": 0.96,
    },
}


@dataclass
class FeatureMatrix:
    weights: Dict[str, float] = field(default_factory=lambda: {name: 1.0 for name in FEATURE_NAMES})
    bias: float = 0.0

    def score(self, state: StoryState, features: Dict[str, float]) -> float:
        total = self.bias
        combined = self._contextual_weights(state)
        for name, value in features.items():
            total += combined.get(name, 0.0) * value
        total += 0.15 * state.conflict_intensity
        total += 0.10 * state.emotional_temperature
        total += 0.10 * state.mainline_progress
        total += self._tag_bonus(state)
        return total

    def _contextual_weights(self, state: StoryState) -> Dict[str, float]:
        genre = self._detect_genre(state)
        tone = self._detect_tone(state)
        stage = state.stage if state.stage in STAGE_WEIGHTS else "middle"
        contextual = {}
        for name in FEATURE_NAMES:
            contextual[name] = (
                self.weights.get(name, 0.0)
                * GENRE_WEIGHTS.get(genre, {}).get(name, 1.0)
                * TONE_WEIGHTS.get(tone, {}).get(name, 1.0)
                * STAGE_WEIGHTS.get(stage, {}).get(name, 1.0)
            )
        return contextual

    def _detect_genre(self, state: StoryState) -> str:
        tags = set(state.tags)
        if any(tag in tags for tag in {"romance", "cp", "love"}):
            return "romance"
        if any(tag in tags for tag in {"suspense", "mystery", "crime"}):
            return "suspense"
        if any(tag in tags for tag in {"power", "court", "strategy"}):
            return "power"
        if any(tag in tags for tag in {"daily", "slice", "life"}):
            return "daily"
        if any(tag in tags for tag in {"xianxia", "cultivation", "fantasy"}):
            return "xianxia"
        return "power"

    def _detect_tone(self, state: StoryState) -> str:
        if state.pacing_speed >= 0.62:
            return "fast"
        if state.pacing_speed <= 0.42:
            return "slow"
        return "balanced"

    def _tag_bonus(self, state: StoryState) -> float:
        bonus = 0.0
        tags = set(state.tags)
        if "opening" in tags:
            bonus += 0.05
        if "payoff" in tags:
            bonus += 0.04
        if "continuity" in tags:
            bonus += 0.03
        return bonus

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
