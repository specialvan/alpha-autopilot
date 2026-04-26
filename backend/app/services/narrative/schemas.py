from __future__ import annotations

from pydantic import BaseModel, Field


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
    prerequisites: list[str] | None = None
    nextStep: str | None = None
    top: bool | None = None


class PreviewRequest(BaseModel):
    tuningWeights: list[TuningWeightPayload]
    recommendations: list[RecommendationPayload]


class DashboardResponse(BaseModel):
    overview: dict
    narrativeSignals: list[dict]
    matrixWeights: list[dict]
    chapterSummary: dict
    tuningWeights: list[dict]
    recommendations: list[dict]
    feedbackNotes: list[str]
    logs: list[dict]
    v4Observability: dict = Field(default_factory=dict)
