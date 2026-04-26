from __future__ import annotations

from fastapi import APIRouter

from ...services.narrative_v4.bridge import (
    build_v4_bridge_payload_with_memory,
    build_v4_workbench_preview,
)
from ...services.narrative_v4.memory_store import create_default_v4_memory_store

router = APIRouter(prefix="/api/v4", tags=["narrative_v4"])
memory_store = create_default_v4_memory_store()


@router.post("/plot/preview")
def preview_v4_plot(context: dict[str, object]):
    return build_v4_bridge_payload_with_memory(
        context,
        memory_store=memory_store,
        context_id=str(context.get("id", "api-v4-plot")),
    )


@router.post("/workbench/preview")
def preview_v4_workbench(context: dict[str, object]):
    return build_v4_workbench_preview(context, memory_store=memory_store)
