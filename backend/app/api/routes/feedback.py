from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...services.narrative.feedback_service import NarrativeFeedbackService

router = APIRouter(prefix="/api", tags=["feedback"])
service = NarrativeFeedbackService()


class FeedbackRequest(BaseModel):
    action: str
    target: float = Field(ge=0, le=1)
    predicted: float = Field(ge=0, le=1)
    feedback: float = Field(ge=0, le=1)


@router.post("/feedback")
def submit_feedback(payload: FeedbackRequest):
    return service.record_feedback(payload.action, payload.target, payload.predicted, payload.feedback).to_dict()
