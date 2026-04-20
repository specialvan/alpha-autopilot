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
        action="escalate_pressure",
        delta={"conflict_intensity": 0.22, "payoff_pressure": 0.10, "pacing_speed": 0.06},
        explanation="加压当前局面，推动角色进入更强对抗区。",
    ),
    NarrativeCandidate(
        action="focus_character",
        delta={"emotional_temperature": 0.08, "sideplot_progress": 0.05},
        explanation="强化人物关系与情绪沉淀，补足人物弧线。",
    ),
    NarrativeCandidate(
        action="deepen_relationship",
        delta={"emotional_temperature": 0.10, "sideplot_progress": 0.04, "character_focus": 0.06},
        explanation="加深人物互动，让关系变化成为推进动力。",
    ),
    NarrativeCandidate(
        action="plant_foreshadow",
        delta={"foreshadowing_load": 0.20, "payoff_pressure": 0.08, "mainline_progress": 0.05},
        explanation="埋设伏笔，增强后续回收价值。",
    ),
    NarrativeCandidate(
        action="open_new_branch",
        delta={"sideplot_progress": 0.14, "foreshadowing_load": 0.06},
        explanation="开启新支线，扩大叙事空间。",
    ),
    NarrativeCandidate(
        action="deliver_payoff",
        delta={"payoff_pressure": -0.15, "emotional_temperature": 0.18, "mainline_progress": 0.12},
        explanation="回收已有铺垫，获得明确情绪回报。",
    ),
    NarrativeCandidate(
        action="reverse_twist",
        delta={"conflict_intensity": 0.14, "emotional_temperature": 0.12, "foreshadowing_load": -0.04},
        explanation="用反转提升惊讶值和局势波动。",
    ),
    NarrativeCandidate(
        action="adjust_pacing",
        delta={"pacing_speed": -0.10, "continuity_safety": 0.10},
        explanation="降低推进速度，保证过渡自然与稳定性。",
    ),
    NarrativeCandidate(
        action="stabilize_continuity",
        delta={"continuity_safety": 0.18, "pacing_speed": -0.04},
        explanation="优先修复叙事连续性，降低章节跳跃风险。",
    ),
    NarrativeCandidate(
        action="close_branch",
        delta={"sideplot_progress": -0.08, "payoff_pressure": 0.06},
        explanation="收束支线，避免故事发散过度。",
    ),
]


@dataclass
class ChapterPlanner:
    matrix: FeatureMatrix

    def extract_features(self, state: StoryState, candidate: NarrativeCandidate) -> Dict[str, float]:
        delta = candidate.delta
        stage_bias = {
            "opening": 0.15,
            "middle": 0.10,
            "mid_late": 0.08,
            "late": 0.05,
        }.get(state.stage, 0.10)
        return {
            "conflict_push": max(0.0, delta.get("conflict_intensity", 0.0) + state.conflict_intensity * 0.15),
            "emotion_payoff": max(0.0, delta.get("emotional_temperature", 0.0) + state.emotional_temperature * 0.10),
            "hook_strength": max(0.0, delta.get("pacing_speed", 0.0) + delta.get("mainline_progress", 0.0) + stage_bias),
            "continuity_safety": max(0.0, delta.get("continuity_safety", 0.0) + 0.2 - abs(state.pacing_speed - 0.5)),
            "character_focus": max(0.0, delta.get("sideplot_progress", 0.0) + state.sideplot_progress * 0.12 + state.emotional_temperature * 0.2),
            "foreshadowing_value": max(0.0, delta.get("foreshadowing_load", 0.0) + state.foreshadowing_load * 0.15 + state.payoff_pressure * 0.2),
            "tempo_fit": max(0.0, 1.0 - abs(state.pacing_speed - (0.58 if state.stage == "opening" else 0.46))),
        }

    def recommend(self, state: StoryState) -> List[RecommendationResult]:
        results: List[RecommendationResult] = []
        for candidate in DEFAULT_CANDIDATES:
            features = self.extract_features(state, candidate)
            score = self.matrix.score(state, features)
            results.append(RecommendationResult(candidate=candidate, score=score, details=features))
        return sorted(results, key=lambda x: x.score, reverse=True)
