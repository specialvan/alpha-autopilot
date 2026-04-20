from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict, Iterable, List

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
    history: List[Dict[str, Any]] = field(default_factory=list)

    def fit(self, samples: Iterable[TrainingSample]) -> FeatureMatrix:
        planner = ChapterPlanner(self.matrix)
        for sample in samples:
            candidates = planner.recommend(sample.state)
            chosen = next((c for c in candidates if c.candidate.action == sample.target_action), candidates[0])
            before = chosen.score
            self.matrix.update_from_feedback(chosen.details, sample.target_score, chosen.score, lr=0.08)
            after = self.matrix.score(sample.state, chosen.details)
            self.history.append(
                {
                    "action": chosen.candidate.action,
                    "predicted": before,
                    "target": sample.target_score,
                    "feedback": sample.feedback,
                    "updated_score": after,
                }
            )
        return self.matrix

    def update_from_result(self, result: RecommendationResult, target: float) -> None:
        before = result.score
        self.matrix.update_from_feedback(result.details, target, result.score, lr=0.05)
        after = self.matrix.score(StoryState(), result.details)
        self.history.append({"action": result.candidate.action, "predicted": before, "target": target, "updated_score": after})

    def summary(self) -> Dict[str, Any]:
        if not self.history:
            return {"samples": 0, "avg_predicted": 0.0, "avg_target": 0.0, "avg_feedback": 0.0}
        return {
            "samples": len(self.history),
            "avg_predicted": round(mean(item["predicted"] for item in self.history), 4),
            "avg_target": round(mean(item["target"] for item in self.history), 4),
            "avg_feedback": round(mean(item.get("feedback", 0.0) for item in self.history), 4),
        }
