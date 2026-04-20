from __future__ import annotations

from typing import Dict, List

from .feature_matrix import FeatureMatrix
from .narrative import StoryState
from .planner import ChapterPlanner


def recommend_chapter(state: StoryState, matrix: FeatureMatrix | None = None) -> List[Dict[str, object]]:
    planner = ChapterPlanner(matrix or FeatureMatrix())
    results = planner.recommend(state)
    return [
        {
            "action": item.candidate.action,
            "score": round(item.score, 4),
            "explanation": item.candidate.explanation,
            "details": {k: round(v, 4) for k, v in item.details.items()},
        }
        for item in results
    ]
