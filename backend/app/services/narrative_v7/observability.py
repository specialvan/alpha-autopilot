from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock

from alpha_autopilot import ArtifactStore

from ...core.config import settings


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class V7RuntimeMetricsStore:
    path: Path
    _lock: RLock = field(default_factory=RLock, init=False)

    def append_metric(
        self,
        *,
        route: str,
        status: str,
        latency_ms: float,
        error_type: str | None = None,
        http_status: int | None = None,
        route_id: str | None = None,
    ) -> None:
        row: dict[str, object] = {
            "timestamp": _now_iso(),
            "route": str(route).strip() or "unknown",
            "status": str(status).strip().lower() or "unknown",
            "latency_ms": round(max(0.0, float(latency_ms)), 3),
            "error_type": str(error_type).strip() if error_type else "",
            "http_status": int(http_status) if isinstance(http_status, int) else None,
            "route_id": str(route_id).strip() if route_id else "",
        }
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False))
                handle.write("\n")

    def read_rows(self, *, limit: int = 500) -> list[dict[str, object]]:
        with self._lock:
            if not self.path.exists():
                return []
            rows: list[dict[str, object]] = []
            for raw in self.path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    rows.append(payload)
        if limit <= 0:
            return []
        return rows[-limit:]


def create_default_v7_runtime_metrics_store(root: Path | None = None) -> V7RuntimeMetricsStore:
    store = ArtifactStore.default()
    base = root or (store.artifacts_dir / "history")
    return V7RuntimeMetricsStore(path=base / "v7_runtime_metrics.jsonl")


def build_v7_observability_snapshot(
    runtime_store: V7RuntimeMetricsStore | None = None,
    *,
    limit: int = 500,
) -> dict[str, object]:
    store = runtime_store or create_default_v7_runtime_metrics_store()
    rows = store.read_rows(limit=limit)
    count = len(rows)

    if count == 0:
        return {
            "enabled": False,
            "windowLimit": limit,
            "runtimeRows": 0,
            "latencyP95Ms": 0.0,
            "errorRate": 0.0,
            "routes": [],
            "alerts": [
                {
                    "code": "no-runtime-data",
                    "severity": "info",
                    "message": "No runtime metrics persisted for V7 yet.",
                }
            ],
            "lastUpdated": "",
        }

    latencies = [max(0.0, float(item.get("latency_ms", 0.0))) for item in rows]
    errors = sum(1 for item in rows if str(item.get("status", "")).lower() == "error")
    latency_p95 = _percentile(latencies, percentile=95.0)
    error_rate = errors / count

    route_buckets: dict[str, dict[str, float]] = {}
    for row in rows:
        route = str(row.get("route", "unknown"))
        bucket = route_buckets.setdefault(route, {"count": 0.0, "error": 0.0, "latency": 0.0})
        bucket["count"] += 1
        if str(row.get("status", "")).lower() == "error":
            bucket["error"] += 1
        bucket["latency"] += max(0.0, float(row.get("latency_ms", 0.0)))

    routes = [
        {
            "route": route,
            "sampleCount": int(bucket["count"]),
            "errorRate": round(bucket["error"] / max(1.0, bucket["count"]), 4),
            "latencyAvgMs": round(bucket["latency"] / max(1.0, bucket["count"]), 3),
        }
        for route, bucket in route_buckets.items()
    ]
    routes.sort(key=lambda item: item["sampleCount"], reverse=True)

    alerts: list[dict[str, object]] = []
    if count >= 8 and latency_p95 >= float(settings.v7_sampler_timeout_ms):
        alerts.append(
            {
                "code": "v7-latency-p95-high",
                "severity": "warning",
                "message": "V7 runtime P95 latency exceeded configured threshold.",
                "value": round(latency_p95, 3),
                "threshold": float(settings.v7_sampler_timeout_ms),
            }
        )
    if count >= 8 and error_rate >= 0.1:
        alerts.append(
            {
                "code": "v7-error-rate-high",
                "severity": "critical",
                "message": "V7 runtime error rate exceeded threshold.",
                "value": round(error_rate, 4),
                "threshold": 0.1,
            }
        )

    return {
        "enabled": True,
        "windowLimit": limit,
        "runtimeRows": count,
        "latencyP95Ms": round(latency_p95, 3),
        "errorRate": round(error_rate, 4),
        "routes": routes,
        "alerts": alerts,
        "lastUpdated": str(rows[-1].get("timestamp", "")),
    }


def _percentile(values: list[float], *, percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (max(0.0, min(100.0, percentile)) / 100.0) * (len(sorted_values) - 1)
    lower = int(rank)
    upper = min(len(sorted_values) - 1, lower + 1)
    fraction = rank - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction
