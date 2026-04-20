from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .feature_matrix import FeatureMatrix
from .narrative import RecommendationResult, StoryState
from .planner import ChapterPlanner


@dataclass
class TrainingSample:
    state: StoryState
    target_action: str
    target_score: float
    feedback: float


@dataclass
class Trainer:
    matrix: FeatureMatrix = field(default_factory=FeatureMatrix)
    history: List[Dict[str, float]] = field(default_factory=list)

    def fit(self, samples: Iterable[TrainingSample]) -> FeatureMatrix:
        planner = ChapterPlanner(self.matrix)
        for sample in samples:
            candidates = planner.recommend(sample.state)
            chosen = next((c for c in candidates if c.candidate.action == sample.target_action), candidates[0])
            self.matrix.update_from_feedback(chosen.details, sample.target_score, chosen.score, lr=0.08)
            self.history.append({
                "action": chosen.candidate.action,
                "predicted": chosen.score,
                "target": sample.target_score,
                "feedback": sample.feedback,
            })
        return self.matrix

    def update_from_result(self, result: RecommendationResult, target: float) -> None:
        self.matrix.update_from_feedback(result.details, target, result.score, lr=0.05)
        self.history.append({"action": result.candidate.action, "predicted": result.score, "target": target})
