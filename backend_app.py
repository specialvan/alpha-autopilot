from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from alpha_autopilot import FeatureMatrix, StoryState, preview_recommendations, recommend_chapter
from alpha_autopilot.recommend import RecommendationPreviewRequest

app = FastAPI(title="alpha-autopilot api", version="0.1.0")


class TuningWeightPayload(BaseModel):
    label: str
    value: float = Field(ge=0, le=1)
    direction: str
    description: str


class RecommendationPayload(BaseModel):
    action: str
    score: str
    description: str
    riskLevel: str | None = None
    prerequisites: List[str] | None = None
    nextStep: str | None = None
    top: bool | None = None


class PreviewRequest(BaseModel):
    tuningWeights: List[TuningWeightPayload]
    recommendations: List[RecommendationPayload]


class DashboardResponse(BaseModel):
    overview: Dict[str, Any]
    narrativeSignals: List[Dict[str, Any]]
    matrixWeights: List[Dict[str, Any]]
    chapterSummary: Dict[str, Any]
    tuningWeights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    feedbackNotes: List[str]
    logs: List[Dict[str, Any]]


def _base_state() -> StoryState:
    return StoryState(
        chapter_index=18,
        stage="middle",
        mainline_progress=0.61,
        sideplot_progress=0.37,
        conflict_intensity=0.64,
        emotional_temperature=0.53,
        pacing_speed=0.49,
        foreshadowing_load=0.36,
        payoff_pressure=0.31,
        tags=["power", "middle"],
    )


def _dashboard_payload() -> DashboardResponse:
    state = _base_state()
    recommendations = recommend_chapter(state, FeatureMatrix())
    return DashboardResponse(
        overview={
            "matrixVersion": "v003",
            "healthValue": 82,
            "sampleCount": 19,
            "versionCount": 3,
            "hitRate": "76%",
            "riskScore": 34,
        },
        narrativeSignals=[
            {"label": "主线推进", "value": 61},
            {"label": "冲突强度", "value": 64},
            {"label": "伏笔负载", "value": 36},
            {"label": "回收压力", "value": 31},
        ],
        matrixWeights=[
            {"label": "冲突推进", "value": "1.32"},
            {"label": "情绪回报", "value": "1.18"},
            {"label": "钩子强度", "value": "1.09"},
            {"label": "连续性安全", "value": "1.24"},
            {"label": "人物聚焦", "value": "0.96"},
            {"label": "伏笔价值", "value": "1.12"},
            {"label": "节奏适配", "value": "1.04"},
        ],
        chapterSummary={
            "title": "本章建议摘要",
            "hook": "通过一个高压事件或关键信息切入口，快速建立读者注意力。",
            "conflict": "本章优先推进主线冲突，并保留一个可回收的矛盾点。",
            "turn": "在中段加入轻量反转或信息偏转，避免节奏平直。",
            "payoff": "结尾给出明确的阶段性回报或下一章钩子，增强续读动力。",
        },
        tuningWeights=[
            {"label": "爽点强度", "value": 0.78, "direction": "up", "description": "提升打脸、压制、反转后的情绪释放强度。"},
            {"label": "节奏速度", "value": 0.62, "direction": "up", "description": "加快章节推进速度，提升阅读推进感。"},
            {"label": "打斗密度", "value": 0.55, "direction": "up", "description": "增加动作场景与冲突交锋的出现频率。"},
            {"label": "情绪沉淀", "value": 0.47, "direction": "down", "description": "适度降低抒情停顿，避免影响爽感连贯。"},
            {"label": "铺垫权重", "value": 0.58, "direction": "down", "description": "减少过长铺垫，让主线反馈更快发生。"},
        ],
        recommendations=recommendations,
        feedbackNotes=[
            "早期开篇样本对冲突推进的权重修正最明显。",
            "中段样本提高了伏笔与节奏的联动强度。",
            "后段样本增强了回收压力与情绪回报的相关性。",
        ],
        logs=[
            {"time": "2026-04-21 10:41", "text": "v001 初始矩阵生成，完成 10 条样本训练。"},
            {"time": "2026-04-21 11:08", "text": "补充中段样本，伏笔与节奏权重上调。"},
            {"time": "2026-04-21 11:32", "text": "增加后段样本，回收压力与情绪回报闭环增强。"},
        ],
    )


@app.get("/api/dashboard", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    return _dashboard_payload()


@app.post("/api/recommendation/preview")
def preview(payload: PreviewRequest) -> Dict[str, Any]:
    state = _base_state()
    tuning = [weight.model_dump() for weight in payload.tuningWeights]
    recommendations = preview_recommendations(state, tuning, FeatureMatrix())
    return {"recommendations": recommendations}
