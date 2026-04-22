from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative.training_service import NarrativeTrainingService

router = APIRouter(prefix="/api", tags=["training"])


@router.post("/training")
def train_narrative_model():
    return NarrativeTrainingService().train().to_dict()
