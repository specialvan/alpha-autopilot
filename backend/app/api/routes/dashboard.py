from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative.dashboard_service import build_dashboard

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard():
    return build_dashboard().model_dump()
