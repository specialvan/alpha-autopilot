from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock

from alpha_autopilot import ArtifactStore

from ...core.config import settings
from ..observability_envelope import build_unified_observability_envelope


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class V6RuntimeMetricsStore:
    path: Path
    _lock: RLock = field(default_factory=RLock, init=False)

    def append_metric(
        self,
        *,
        route: str,
        status: str,
        latency_ms: float,
        simulation_id: str | None = None,
        path_count: int | None = None,
        failed_path_count: int | None = None,
        winner_path_id: str | None = None,
        fallback_reason: str | None = None,
        error_type: str | None = None,
        risk_flags: list[str] | None = None,
        http_status: int | None = None,
    ) -> None:
        row: dict[str, object] = {
            "timestamp": _now_iso(),
            "route": str(route).strip() or "unknown",
            "status": str(status).strip().lower() or "unknown",
            "latency_ms": round(max(0.0, _safe_float(latency_ms, default=0.0)), 3),
            "simulation_id": str(simulation_id).strip() if simulation_id else "",
            "path_count": _safe_int(path_count, default=None),
            "failed_path_count": _safe_int(failed_path_count, default=None),
            "winner_path_id": str(winner_path_id).strip() if winner_path_id else "",
            "fallback_reason": str(fallback_reason).strip() if fallback_reason else "",
            "error_type": str(error_type).strip() if error_type else "",
            "risk_flags": list(risk_flags or []),
            "http_status": _safe_int(http_status, default=None),
        }
        with self._lock:
            self._append_jsonl(row)

    def read_rows(self, *, limit: int = 500) -> list[dict[str, object]]:
        with self._lock:
            rows = self._read_jsonl()
        if limit <= 0:
            return []
        return rows[-limit:]

    def _append_jsonl(self, row: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")

    def _read_jsonl(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, object]] = []
        for raw in self.path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows


def create_default_v6_runtime_metrics_store(root: Path | None = None) -> V6RuntimeMetricsStore:
    store = ArtifactStore.default()
    base = root or (store.artifacts_dir / "history")
    return V6RuntimeMetricsStore(path=base / "v6_runtime_metrics.jsonl")


def build_v6_observability_snapshot(
    runtime_store: V6RuntimeMetricsStore | None = None,
    *,
    limit: int = 500,
) -> dict[str, object]:
    store = runtime_store or create_default_v6_runtime_metrics_store()
    runtime_rows = store.read_rows(limit=limit)
    runtime_count = len(runtime_rows)

    latency_values = [
        max(0.0, _safe_float(row.get("latency_ms"), default=0.0))
        for row in runtime_rows
        if isinstance(row, dict)
    ]
    error_count = sum(
        1
        for row in runtime_rows
        if isinstance(row, dict) and str(row.get("status", "")).strip().lower() == "error"
    )
    fallback_count = sum(
        1
        for row in runtime_rows
        if isinstance(row, dict)
        and (
            str(row.get("status", "")).strip().lower() == "fallback"
            or bool(str(row.get("fallback_reason", "")).strip())
        )
    )

    latency_p95_ms = round(_percentile(latency_values, percentile=95.0), 3) if latency_values else 0.0
    error_rate = round(error_count / runtime_count, 4) if runtime_count else 0.0
    fallback_rate = round(fallback_count / runtime_count, 4) if runtime_count else 0.0

    runtime_thresholds = {
        "latencyP95Ms": round(max(1.0, float(settings.v6_observability_latency_p95_ms_threshold)), 3),
        "errorRate": round(max(0.0, min(1.0, float(settings.v6_observability_error_rate_threshold))), 4),
        "fallbackRate": round(max(0.0, min(1.0, float(settings.v6_observability_fallback_rate_threshold))), 4),
    }

    routes = _aggregate_route_metrics(runtime_rows)
    alerts = _build_observability_alerts(
        runtime_count=runtime_count,
        latency_p95_ms=latency_p95_ms,
        error_rate=error_rate,
        fallback_rate=fallback_rate,
        runtime_thresholds=runtime_thresholds,
    )

    snapshot = {
        "enabled": bool(runtime_rows),
        "windowLimit": limit,
        "runtimeRows": runtime_count,
        "latencyP95Ms": latency_p95_ms,
        "errorRate": error_rate,
        "fallbackRate": fallback_rate,
        "runtimeThresholds": runtime_thresholds,
        "routes": routes,
        "alerts": alerts,
        "alertCount": len(alerts),
        "criticalAlertCount": sum(1 for item in alerts if item.get("severity") == "critical"),
        "lastUpdated": _latest_timestamp(runtime_rows),
    }
    snapshot["unifiedEnvelope"] = build_unified_observability_envelope(
        layer="v6",
        snapshot=snapshot,
    )
    return snapshot


def _aggregate_route_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        route = str(row.get("route", "")).strip() or "unknown"
        bucket = buckets.setdefault(
            route,
            {
                "route": route,
                "sampleCount": 0,
                "errorCount": 0,
                "fallbackCount": 0,
                "latencyTotal": 0.0,
            },
        )
        bucket["sampleCount"] = int(bucket.get("sampleCount", 0)) + 1
        status = str(row.get("status", "")).strip().lower()
        if status == "error":
            bucket["errorCount"] = int(bucket.get("errorCount", 0)) + 1
        if status == "fallback" or bool(str(row.get("fallback_reason", "")).strip()):
            bucket["fallbackCount"] = int(bucket.get("fallbackCount", 0)) + 1
        bucket["latencyTotal"] = _safe_float(bucket.get("latencyTotal"), default=0.0) + max(
            0.0,
            _safe_float(row.get("latency_ms"), default=0.0),
        )

    output: list[dict[str, object]] = []
    for bucket in buckets.values():
        sample_count = int(bucket.get("sampleCount", 0))
        if sample_count <= 0:
            continue
        error_count = int(bucket.get("errorCount", 0))
        fallback_count = int(bucket.get("fallbackCount", 0))
        latency_total = _safe_float(bucket.get("latencyTotal"), default=0.0)
        output.append(
            {
                "route": str(bucket.get("route", "unknown")),
                "sampleCount": sample_count,
                "errorRate": round(error_count / sample_count, 4),
                "fallbackRate": round(fallback_count / sample_count, 4),
                "latencyAvgMs": round(latency_total / sample_count, 3),
            }
        )

    return sorted(
        output,
        key=lambda item: (
            int(item.get("sampleCount", 0)),
            float(item.get("errorRate", 0.0)),
            float(item.get("fallbackRate", 0.0)),
        ),
        reverse=True,
    )


def _build_observability_alerts(
    *,
    runtime_count: int,
    latency_p95_ms: float,
    error_rate: float,
    fallback_rate: float,
    runtime_thresholds: dict[str, float],
) -> list[dict[str, object]]:
    alerts: list[dict[str, object]] = []
    latency_threshold = _safe_float(runtime_thresholds.get("latencyP95Ms"), default=1200.0)
    error_threshold = _safe_float(runtime_thresholds.get("errorRate"), default=0.1)
    fallback_threshold = _safe_float(runtime_thresholds.get("fallbackRate"), default=0.4)

    if runtime_count == 0:
        alerts.append(
            {
                "code": "no-runtime-data",
                "severity": "info",
                "message": "No runtime metrics persisted for V6 yet.",
            }
        )
        return alerts

    if runtime_count >= 8 and latency_p95_ms >= latency_threshold:
        alerts.append(
            {
                "code": "runtime-latency-p95-high",
                "severity": "warning",
                "message": "V6 runtime P95 latency exceeded configured threshold.",
                "value": round(latency_p95_ms, 3),
                "threshold": round(latency_threshold, 3),
            }
        )
    if runtime_count >= 8 and error_rate >= error_threshold:
        alerts.append(
            {
                "code": "runtime-error-rate-high",
                "severity": "critical",
                "message": "V6 runtime error rate exceeded configured threshold.",
                "value": round(error_rate, 4),
                "threshold": round(error_threshold, 4),
            }
        )
    if runtime_count >= 8 and fallback_rate >= fallback_threshold:
        alerts.append(
            {
                "code": "runtime-fallback-rate-high",
                "severity": "warning",
                "message": "V6 runtime fallback rate exceeded configured threshold.",
                "value": round(fallback_rate, 4),
                "threshold": round(fallback_threshold, 4),
            }
        )
    return alerts


def _latest_timestamp(rows: list[dict[str, object]]) -> str | None:
    timestamps = [
        str(row.get("timestamp", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("timestamp", "")).strip()
    ]
    if not timestamps:
        return None
    return max(timestamps)


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _safe_int(value: object, *, default: int | None) -> int | None:
    try:
        if value is None:
            return default
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _percentile(values: list[float], *, percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = max(0.0, min(100.0, percentile)) / 100.0 * (len(sorted_values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    if lower == upper:
        return sorted_values[lower]
    weight = rank - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight
