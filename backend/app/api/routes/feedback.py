from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...services.narrative.feedback_service import NarrativeFeedbackService

router = APIRouter(prefix="/api", tags=["feedback"])
service = NarrativeFeedbackService()


class FeedbackRequest(BaseModel):
    recommendationAction: str
    accepted: bool
    score: float = Field(ge=0, le=1)
    notes: str | None = None


@router.post("/feedback")
def record_feedback(payload: FeedbackRequest):
    predicted = payload.score if payload.accepted else max(0.0, payload.score - 0.18)
    result = service.record_feedback(
        action=payload.recommendationAction,
        target=payload.score,
        predicted=predicted,
        feedback=payload.score,
        notes=payload.notes or "",
    )
    return result.to_dict()
