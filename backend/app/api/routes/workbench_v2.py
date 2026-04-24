from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v2.workbench_service import NarrativeV2WorkbenchService

router = APIRouter(prefix="/api/v2", tags=["workbench_v2"])


def _default_service_factory() -> NarrativeV2WorkbenchService:
    return NarrativeV2WorkbenchService()


service_factory = _default_service_factory


@router.get("/workbench/contexts")
def get_workbench_contexts_v2():
    return service_factory().list_contexts()
