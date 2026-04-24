from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v2.preview_service import NarrativeV2PreviewService
from ...services.narrative_v2.schemas import NarrativeV2PreviewRequest

router = APIRouter(prefix="/api/v2", tags=["recommendation_v2"])


def _default_service_factory() -> NarrativeV2PreviewService:
    return NarrativeV2PreviewService()


service_factory = _default_service_factory


@router.post("/recommendation/preview")
def preview_recommendation_v2(payload: NarrativeV2PreviewRequest):
    return service_factory().build_preview(payload)
