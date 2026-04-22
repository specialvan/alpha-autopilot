from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v2.preview_service import NarrativeV2PreviewService
from ...services.narrative_v2.schemas import NarrativeV2PreviewRequest

router = APIRouter(prefix="/api/v2", tags=["recommendation_v2"])
service = NarrativeV2PreviewService()


@router.post("/recommendation/preview")
def preview_recommendation_v2(payload: NarrativeV2PreviewRequest):
    return service.build_preview(payload)
