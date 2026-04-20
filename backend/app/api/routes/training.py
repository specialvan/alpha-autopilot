from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative.training_service import NarrativeTrainingService

router = APIRouter(prefix="/api", tags=["training"])
service = NarrativeTrainingService()


@router.post("/training")
def train_narrative_model():
    return service.train().to_dict()
