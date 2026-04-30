from __future__ import annotations

from typing import Any


def build_unified_observability_envelope(
    *,
    layer: str,
    snapshot: dict[str, object],
) -> dict[str, object]:
    alerts = snapshot.get("alerts")
    alert_items = alerts if isinstance(alerts, list) else []
    routes = snapshot.get("routes")
    route_items = routes if isinstance(routes, list) else []

    thresholds = snapshot.get("runtimeThresholds")
    if not isinstance(thresholds, dict):
        thresholds = snapshot.get("thresholds")
    if not isinstance(thresholds, dict):
        thresholds = {}

    runtime_rows = _to_int(snapshot.get("runtimeRows"), default=0)
    latency_p95_ms = _to_float(snapshot.get("latencyP95Ms"), default=0.0)
    error_rate = _to_float(snapshot.get("errorRate"), default=0.0)
    fallback_rate = _to_float(snapshot.get("fallbackRate"), default=0.0)
    alert_count = _to_int(snapshot.get("alertCount"), default=len(alert_items))
    critical_alert_count = _to_int(
        snapshot.get("criticalAlertCount"),
        default=sum(1 for item in alert_items if isinstance(item, dict) and item.get("severity") == "critical"),
    )

    key_metrics: dict[str, float | int] = {
        "runtimeRows": runtime_rows,
        "latencyP95Ms": round(latency_p95_ms, 3),
        "errorRate": round(error_rate, 4),
        "fallbackRate": round(fallback_rate, 4),
        "alertCount": alert_count,
        "criticalAlertCount": critical_alert_count,
    }

    return {
        "schemaVersion": "obs-envelope.v1",
        "layer": layer,
        "enabled": bool(snapshot.get("enabled", False)),
        "windowLimit": _to_int(snapshot.get("windowLimit"), default=0),
        "lastUpdated": str(snapshot.get("lastUpdated", "") or ""),
        "keyMetrics": key_metrics,
        "thresholds": thresholds,
        "routeCount": len(route_items),
    }


def _to_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _to_int(value: object, *, default: int) -> int:
    try:
        if value is None:
            return default
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default
