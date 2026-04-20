from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List

from .feature_matrix import FeatureMatrix
from .metrics import RecommendationMetricRecord, RecommendationValueMetrics
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
    value_metrics: RecommendationValueMetrics = field(default_factory=RecommendationValueMetrics)

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
            self.value_metrics.add_record(
                RecommendationMetricRecord(
                    action=chosen.candidate.action,
                    score=chosen.score,
                    accepted=sample.feedback >= 0.8,
                    chapter_quality=sample.feedback,
                    followup_writeability=max(0.0, min(1.0, sample.feedback * 0.9 + 0.05)),
                    continuity_delta=max(-1.0, min(1.0, sample.target_score - chosen.score)),
                    notes="training sample",
                )
            )
        return self.matrix

    def update_from_result(self, result: RecommendationResult, target: float) -> None:
        self.matrix.update_from_feedback(result.details, target, result.score, lr=0.05)
        self.history.append({"action": result.candidate.action, "predicted": result.score, "target": target})
        self.value_metrics.add_record(
            RecommendationMetricRecord(
                action=result.candidate.action,
                score=result.score,
                accepted=target >= 0.8,
                chapter_quality=target,
                followup_writeability=max(0.0, min(1.0, target * 0.88 + 0.07)),
                continuity_delta=max(-1.0, min(1.0, target - result.score)),
                notes="live result update",
            )
        )

    def summary(self) -> Dict[str, float]:
        if not self.history:
            return {"count": 0.0, "avg_predicted": 0.0, "avg_target": 0.0, "avg_feedback": 0.0, "rmse": 0.0}
        count = float(len(self.history))
        predicted_values = [item["predicted"] for item in self.history]
        target_values = [item["target"] for item in self.history]
        feedback_values = [item.get("feedback", item["target"]) for item in self.history]
        errors = [(item["predicted"] - item["target"]) ** 2 for item in self.history]
        return {
            "count": count,
            "avg_predicted": round(mean(predicted_values), 4),
            "avg_target": round(mean(target_values), 4),
            "avg_feedback": round(mean(feedback_values), 4),
            "rmse": round(mean(errors) ** 0.5, 4),
        }
