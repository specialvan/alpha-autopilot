from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v2.schemas import NarrativeV2WorkbenchContextsResponsePayload
from ...services.narrative_v2.workbench_service import NarrativeV2WorkbenchService

router = APIRouter(prefix="/api/v2", tags=["workbench_v2"])


def _default_service_factory() -> NarrativeV2WorkbenchService:
    return NarrativeV2WorkbenchService()


service_factory = _default_service_factory


@router.get(
    "/workbench/contexts",
    response_model=NarrativeV2WorkbenchContextsResponsePayload,
    response_model_exclude_none=True,
)
def get_workbench_contexts_v2():
    return service_factory().list_contexts(include_source_diagnostics=True)


@router.post(
    "/workbench/contexts/refresh",
    response_model=NarrativeV2WorkbenchContextsResponsePayload,
    response_model_exclude_none=True,
)
def refresh_workbench_contexts_v2(online_only: bool = False):
    return service_factory().list_contexts(
        include_source_diagnostics=True,
        online_only=online_only,
    )
