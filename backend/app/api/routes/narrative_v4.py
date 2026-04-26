from __future__ import annotations

from fastapi import APIRouter, Query

from ...services.narrative_v4.alert_channel import (
    create_default_v4_alert_channel,
    route_v4_observability_alerts,
)
from ...services.narrative_v4.bridge import (
    build_v4_bridge_payload_with_memory,
    build_v4_workbench_preview,
)
from ...services.narrative_v4.memory_store import create_default_v4_memory_store
from ...services.narrative_v4.observability import build_v4_observability_snapshot

router = APIRouter(prefix="/api/v4", tags=["narrative_v4"])
memory_store = create_default_v4_memory_store()
alert_channel = create_default_v4_alert_channel()


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


@router.get("/observability/snapshot")
def get_v4_observability_snapshot(
    limit: int = Query(default=600, ge=10, le=5000),
    include_alert_routing: bool = True,
):
    snapshot = build_v4_observability_snapshot(memory_store=memory_store, limit=limit)
    if include_alert_routing:
        snapshot["alertRouting"] = route_v4_observability_alerts(
            snapshot,
            channel=alert_channel,
        )
    return snapshot


@router.post("/observability/alerts/route")
def route_v4_observability_alerts_endpoint(
    limit: int = Query(default=600, ge=10, le=5000),
):
    snapshot = build_v4_observability_snapshot(memory_store=memory_store, limit=limit)
    routing = route_v4_observability_alerts(snapshot, channel=alert_channel)
    return {
        "routing": routing,
        "snapshot": snapshot,
    }
