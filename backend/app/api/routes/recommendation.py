from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative.preview_service import build_preview
from ...services.narrative.schemas import PreviewRequest

router = APIRouter(prefix="/api", tags=["recommendation"])


@router.post("/recommendation/preview")
def preview_recommendation(payload: PreviewRequest):
    return build_preview(payload)
