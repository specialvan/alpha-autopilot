from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .feature_matrix import FeatureMatrix
from .narrative import NarrativeCandidate, RecommendationResult, StoryState


DEFAULT_CANDIDATES = [
    NarrativeCandidate(
        action="push_conflict",
        delta={"conflict_intensity": 0.18, "mainline_progress": 0.10, "pacing_speed": 0.08},
        explanation="推进主线冲突，提升当前章节张力。",
    ),
    NarrativeCandidate(
        action="focus_character",
        delta={"character_focus": 0.0, "emotional_temperature": 0.08, "sideplot_progress": 0.05},
        explanation="强化人物关系与情绪沉淀，补足人物弧线。",
    ),
    NarrativeCandidate(
        action="plant_foreshadow",
        delta={"foreshadowing_load": 0.20, "payoff_pressure": 0.08, "mainline_progress": 0.05},
        explanation="埋设伏笔，增强后续回收价值。",
    ),
    NarrativeCandidate(
        action="deliver_payoff",
        delta={"payoff_pressure": -0.15, "emotional_temperature": 0.18, "mainline_progress": 0.12},
        explanation="回收已有铺垫，获得明确情绪回报。",
    ),
    NarrativeCandidate(
        action="adjust_pacing",
        delta={"pacing_speed": -0.10, "continuity_safety": 0.10},
        explanation="降低推进速度，保证过渡自然与稳定性。",
    ),
]


@dataclass
class ChapterPlanner:
    matrix: FeatureMatrix

    def extract_features(self, state: StoryState, candidate: NarrativeCandidate) -> Dict[str, float]:
        delta = candidate.delta
        return {
            "conflict_push": max(0.0, delta.get("conflict_intensity", 0.0)),
            "emotion_payoff": max(0.0, delta.get("emotional_temperature", 0.0)),
            "hook_strength": max(0.0, delta.get("pacing_speed", 0.0) + delta.get("mainline_progress", 0.0)),
            "continuity_safety": max(0.0, delta.get("continuity_safety", 0.0) + 0.2 - abs(state.pacing_speed - 0.5)),
            "character_focus": max(0.0, delta.get("sideplot_progress", 0.0) + state.emotional_temperature * 0.2),
            "foreshadowing_value": max(0.0, delta.get("foreshadowing_load", 0.0) + state.payoff_pressure * 0.2),
            "tempo_fit": max(0.0, 1.0 - abs(state.pacing_speed - (0.55 if state.stage == "opening" else 0.45))),
        }

    def recommend(self, state: StoryState) -> List[RecommendationResult]:
        results: List[RecommendationResult] = []
        for candidate in DEFAULT_CANDIDATES:
            features = self.extract_features(state, candidate)
            score = self.matrix.score(state, features)
            results.append(RecommendationResult(candidate=candidate, score=score, details=features))
        return sorted(results, key=lambda x: x.score, reverse=True)
