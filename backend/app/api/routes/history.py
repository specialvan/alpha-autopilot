from __future__ import annotations

from fastapi import APIRouter, Query

from ...services.narrative.history_export_service import HistoryExportService
from ...services.narrative.history_service import HistoryService

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def get_history(
    stage: str | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    return HistoryService().get_history(stage=stage, action=action, limit=limit)


@router.post("/history/export")
def export_history():
    return HistoryExportService().export_json()
