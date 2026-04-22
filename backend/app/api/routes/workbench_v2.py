from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v2.workbench_service import NarrativeV2WorkbenchService

router = APIRouter(prefix="/api/v2", tags=["workbench_v2"])
service = NarrativeV2WorkbenchService()


@router.get("/workbench/contexts")
def get_workbench_contexts_v2():
    return service.list_contexts()
