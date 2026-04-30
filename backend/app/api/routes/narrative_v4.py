from __future__ import annotations

from fastapi import APIRouter, Query
from time import perf_counter

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
    started_at = perf_counter()
    route_name = "/api/v4/plot/preview"
    context_id = str(context.get("id", "api-v4-plot"))
    payload: dict[str, object] | None = None
    try:
        payload = build_v4_bridge_payload_with_memory(
            context,
            memory_store=memory_store,
            context_id=context_id,
        )
        return payload
    except Exception as exc:
        _record_runtime_metric(
            route_name=route_name,
            started_at=started_at,
            context_id=context_id,
            error=exc,
        )
        raise
    finally:
        if payload is not None:
            _record_runtime_metric(
                route_name=route_name,
                started_at=started_at,
                context_id=context_id,
                payload=payload,
            )


@router.post("/workbench/preview")
def preview_v4_workbench(context: dict[str, object]):
    started_at = perf_counter()
    route_name = "/api/v4/workbench/preview"
    context_id = str(context.get("id", "workbench-context"))
    payload: dict[str, object] | None = None
    try:
        payload = build_v4_workbench_preview(context, memory_store=memory_store)
        return payload
    except Exception as exc:
        _record_runtime_metric(
            route_name=route_name,
            started_at=started_at,
            context_id=context_id,
            error=exc,
        )
        raise
    finally:
        if payload is not None:
            _record_runtime_metric(
                route_name=route_name,
                started_at=started_at,
                context_id=context_id,
                payload=payload,
            )


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


def _record_runtime_metric(
    *,
    route_name: str,
    started_at: float,
    context_id: str,
    payload: dict[str, object] | None = None,
    error: Exception | None = None,
) -> None:
    latency_ms = max(0.0, (perf_counter() - started_at) * 1000.0)
    fallback_reason = ""
    status = "success"
    if payload is not None:
        enabled = bool(payload.get("enabled", True))
        if not enabled:
            status = "fallback"
            fallback_reason = str(payload.get("fallback_reason", "")).strip()
    if error is not None:
        status = "error"
    memory_store.append_runtime_metric(
        route=route_name,
        status=status,
        latency_ms=latency_ms,
        fallback_reason=fallback_reason or None,
        error_type=type(error).__name__ if error is not None else None,
        context_id=context_id,
    )
