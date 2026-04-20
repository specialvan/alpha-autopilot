from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .feature_matrix import FeatureMatrix
from .narrative import StoryState
from .planner import ChapterPlanner


@dataclass
class RecommendationPackage:
    action: str
    score: float
    explanation: str
    risk_level: str
    prerequisites: List[str]
    next_step: str
    details: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationPreviewRequest:
    tuning_weights: List[Dict[str, float]]
    base_state: StoryState
    base_recommendations: List[Dict[str, object]]


def _risk_level(score: float, details: Dict[str, float]) -> str:
    if details.get("continuity_safety", 0.0) < 0.55:
        return "medium"
    if score >= 2.2:
        return "low"
    if score >= 1.7:
        return "medium"
    return "high"


def _build_prerequisites(action: str, details: Dict[str, float]) -> List[str]:
    items: List[str] = []
    if action in {"push_conflict", "escalate_pressure", "reverse_twist"}:
        items.append("确认当前冲突链条已建立")
    if action in {"deliver_payoff", "close_branch"}:
        items.append("确认前文铺垫和伏笔已具备回收条件")
    if action in {"plant_foreshadow", "open_new_branch"}:
        items.append("确认章节存在足够的信息留白")
    if action in {"stabilize_continuity", "adjust_pacing"}:
        items.append("确认当前章节不宜继续高速推进")
    if details.get("character_focus", 0.0) > 0.7:
        items.append("确认主要角色的情绪线处于可展开状态")
    return items or ["当前状态可直接执行"]


def _build_next_step(action: str, score: float) -> str:
    if action == "push_conflict":
        return "优先安排对抗、压迫或失败风险场景，形成章节主驱动力。"
    if action == "escalate_pressure":
        return "提高角色代价和外部压力，为反转或爆发做准备。"
    if action == "focus_character":
        return "通过对话、内心或关系细节补强人物弧线。"
    if action == "deepen_relationship":
        return "围绕关键人物互动推进情感张力或联盟变化。"
    if action == "plant_foreshadow":
        return "埋入下一阶段的线索、道具或信息缺口。"
    if action == "open_new_branch":
        return "打开一个轻量支线，但要控制分支长度。"
    if action == "deliver_payoff":
        return "优先兑现前文铺垫，释放情绪和信息回报。"
    if action == "reverse_twist":
        return "使用意外信息打断预期，并确保前文可回溯解释。"
    if action == "adjust_pacing":
        return "补充过渡段或缓冲段，避免节奏过快。"
    if action == "stabilize_continuity":
        return "修复因果、设定或视角连接，保持叙事稳定。"
    if action == "close_branch":
        return "收束支线并合流到主线，避免故事发散。"
    return f"根据当前评分 {score:.2f} 执行常规推进。"


def _apply_tuning_to_score(score: float, tuning_weights: List[Dict[str, float]]) -> float:
    delta = 0.0
    for item in tuning_weights:
        direction = 1.0 if item.get("direction") == "up" else -1.0
        delta += direction * float(item.get("value", 0.0))
    factor = max(0.85, min(1.15, 1 + delta * 0.06))
    return round(score * factor, 4)


def recommend_chapter(state: StoryState, matrix: FeatureMatrix | None = None) -> List[Dict[str, object]]:
    planner = ChapterPlanner(matrix or FeatureMatrix())
    results = planner.recommend(state)
    packages: List[Dict[str, object]] = []
    for item in results:
        prerequisites = _build_prerequisites(item.candidate.action, item.details)
        package = RecommendationPackage(
            action=item.candidate.action,
            score=round(item.score, 4),
            explanation=item.candidate.explanation,
            risk_level=_risk_level(item.score, item.details),
            prerequisites=prerequisites,
            next_step=_build_next_step(item.candidate.action, item.score),
            details={k: round(v, 4) for k, v in item.details.items()},
        )
        packages.append(package.to_dict())
    return packages


def preview_recommendations(
    state: StoryState,
    tuning_weights: List[Dict[str, float]],
    matrix: FeatureMatrix | None = None,
) -> List[Dict[str, object]]:
    base = recommend_chapter(state, matrix)
    preview: List[Dict[str, object]] = []
    for index, item in enumerate(base):
        adjusted_score = _apply_tuning_to_score(float(item["score"]), tuning_weights)
        risk_level = "low" if adjusted_score >= 0.9 else "medium" if adjusted_score >= 0.82 else "high"
        next_step = item["next_step"]
        if isinstance(next_step, str):
            next_step = f"{next_step}（预览已刷新）"
        preview.append(
            {
                **item,
                "score": adjusted_score,
                "risk_level": risk_level,
                "next_step": next_step,
                "top": index == 0,
            }
        )
    preview.sort(key=lambda x: float(x["score"]), reverse=True)
    for index, item in enumerate(preview):
        item["top"] = index == 0
    return preview
