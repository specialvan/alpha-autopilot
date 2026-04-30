from __future__ import annotations

from ...core.config import settings
from ..observability_envelope import build_unified_observability_envelope
from .memory_store import V4MemoryStore, create_default_v4_memory_store

AUTO_LEARNING_MIN_SAMPLES = 4
TREND_WINDOWS: tuple[int, ...] = (20, 60, 180)


def build_v4_observability_snapshot(
    memory_store: V4MemoryStore | None = None,
    *,
    limit: int = 600,
) -> dict[str, object]:
    store = memory_store or create_default_v4_memory_store()
    relationship_rows = store.read_relationship_rows(limit=limit)
    feedback_rows = store.read_feedback_rows(limit=limit)
    runtime_rows = store.read_runtime_metric_rows(limit=limit)

    context_ids = {
        str(row.get("context_id", "")).strip()
        for row in [*relationship_rows, *feedback_rows]
        if isinstance(row, dict) and str(row.get("context_id", "")).strip()
    }
    tension_values = [
        _safe_float(row.get("tension_score"), default=0.0)
        for row in relationship_rows
        if isinstance(row, dict)
    ]
    feedback_signals = [
        _feedback_signal(row)
        for row in feedback_rows
        if isinstance(row, dict)
    ]
    accepted_count = sum(
        1
        for row in feedback_rows
        if isinstance(row, dict) and bool(row.get("accepted", False))
    )
    genres = _aggregate_genre_metrics(feedback_rows)
    top_genres = sorted(
        genres.values(),
        key=lambda item: (
            item["sampleCount"],
            abs(item["feedbackSignal"]),
            item["acceptRate"],
        ),
        reverse=True,
    )[:3]
    auto_learning_ready_genres = sum(
        1 for item in genres.values() if item["sampleCount"] >= AUTO_LEARNING_MIN_SAMPLES
    )
    average_tension = round(sum(tension_values) / len(tension_values), 4) if tension_values else 0.0
    feedback_signal = (
        round(sum(feedback_signals) / len(feedback_signals), 4)
        if feedback_signals
        else 0.0
    )
    accept_rate = round(accepted_count / len(feedback_rows), 4) if feedback_rows else 0.0
    runtime_thresholds = {
        "latencyP95Ms": round(
            max(1.0, float(settings.v4_observability_latency_p95_ms_threshold)),
            3,
        ),
        "errorRate": round(
            max(0.0, min(1.0, float(settings.v4_observability_error_rate_threshold))),
            4,
        ),
        "fallbackRate": round(
            max(0.0, min(1.0, float(settings.v4_observability_fallback_rate_threshold))),
            4,
        ),
    }
    latency_values = [
        max(0.0, _safe_float(row.get("latency_ms"), default=0.0))
        for row in runtime_rows
        if isinstance(row, dict)
    ]
    runtime_count = len(runtime_rows)
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
    trend = _build_feedback_trend(feedback_rows)
    alerts = _build_observability_alerts(
        relationship_rows=relationship_rows,
        feedback_rows=feedback_rows,
        runtime_rows=runtime_rows,
        average_tension=average_tension,
        feedback_signal=feedback_signal,
        accept_rate=accept_rate,
        latency_p95_ms=latency_p95_ms,
        error_rate=error_rate,
        fallback_rate=fallback_rate,
        runtime_thresholds=runtime_thresholds,
        genres_tracked=len(genres),
        auto_learning_ready_genres=auto_learning_ready_genres,
        trend=trend,
    )
    latest_timestamp = _latest_timestamp([*relationship_rows, *feedback_rows])

    snapshot = {
        "enabled": bool(relationship_rows or feedback_rows),
        "windowLimit": limit,
        "activeContexts": len(context_ids),
        "relationshipRows": len(relationship_rows),
        "feedbackRows": len(feedback_rows),
        "runtimeRows": runtime_count,
        "averageTension": average_tension,
        "feedbackSignal": feedback_signal,
        "acceptRate": accept_rate,
        "latencyP95Ms": latency_p95_ms,
        "errorRate": error_rate,
        "fallbackRate": fallback_rate,
        "runtimeThresholds": runtime_thresholds,
        "genresTracked": len(genres),
        "autoLearningReadyGenres": auto_learning_ready_genres,
        "topGenres": top_genres,
        "trend": trend,
        "alerts": alerts,
        "alertCount": len(alerts),
        "criticalAlertCount": sum(
            1 for item in alerts if item.get("severity") == "critical"
        ),
        "lastUpdated": latest_timestamp,
    }
    snapshot["unifiedEnvelope"] = build_unified_observability_envelope(
        layer="v4",
        snapshot=snapshot,
    )
    return snapshot


def _aggregate_genre_metrics(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    metrics: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        genre = str(row.get("genre", "")).strip().lower()
        if not genre:
            continue
        bucket = metrics.setdefault(
            genre,
            {
                "genre": genre,
                "sampleCount": 0,
                "acceptCount": 0,
                "signalSum": 0.0,
            },
        )
        bucket["sampleCount"] = int(bucket.get("sampleCount", 0)) + 1
        if bool(row.get("accepted", False)):
            bucket["acceptCount"] = int(bucket.get("acceptCount", 0)) + 1
        bucket["signalSum"] = _safe_float(bucket.get("signalSum"), default=0.0) + _feedback_signal(row)

    normalized: dict[str, dict[str, object]] = {}
    for genre, bucket in metrics.items():
        sample_count = int(bucket.get("sampleCount", 0))
        if sample_count <= 0:
            continue
        accept_count = int(bucket.get("acceptCount", 0))
        signal_sum = _safe_float(bucket.get("signalSum"), default=0.0)
        normalized[genre] = {
            "genre": genre,
            "sampleCount": sample_count,
            "acceptRate": round(accept_count / sample_count, 4),
            "feedbackSignal": round(signal_sum / sample_count, 4),
        }
    return normalized


def _feedback_signal(row: dict[str, object]) -> float:
    retention_delta = _safe_float(row.get("retention_delta"), default=0.0)
    abandonment_delta = _safe_float(row.get("abandonment_delta"), default=0.0)
    accepted_signal = 0.5 if bool(row.get("accepted", False)) else -0.5
    return max(-1.0, min(1.0, accepted_signal + 0.5 * (retention_delta - abandonment_delta)))


def _build_feedback_trend(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    trend: list[dict[str, object]] = []
    for window_size in TREND_WINDOWS:
        bucket = rows[-window_size:]
        if not bucket:
            continue
        sample_count = len(bucket)
        accept_count = sum(1 for item in bucket if bool(item.get("accepted", False)))
        signal = sum(_feedback_signal(item) for item in bucket) / sample_count
        trend.append(
            {
                "windowSize": window_size,
                "sampleCount": sample_count,
                "feedbackSignal": round(signal, 4),
                "acceptRate": round(accept_count / sample_count, 4),
            }
        )
    return trend


def _build_observability_alerts(
    *,
    relationship_rows: list[dict[str, object]],
    feedback_rows: list[dict[str, object]],
    runtime_rows: list[dict[str, object]],
    average_tension: float,
    feedback_signal: float,
    accept_rate: float,
    latency_p95_ms: float,
    error_rate: float,
    fallback_rate: float,
    runtime_thresholds: dict[str, float],
    genres_tracked: int,
    auto_learning_ready_genres: int,
    trend: list[dict[str, object]],
) -> list[dict[str, object]]:
    alerts: list[dict[str, object]] = []
    feedback_count = len(feedback_rows)
    relationship_count = len(relationship_rows)
    runtime_count = len(runtime_rows)
    latency_threshold = _safe_float(runtime_thresholds.get("latencyP95Ms"), default=900.0)
    error_threshold = _safe_float(runtime_thresholds.get("errorRate"), default=0.08)
    fallback_threshold = _safe_float(runtime_thresholds.get("fallbackRate"), default=0.35)
    if feedback_count == 0:
        alerts.append(
            {
                "code": "no-feedback",
                "severity": "info",
                "message": "No persisted feedback rows yet.",
            }
        )

    if feedback_count >= 12 and accept_rate < 0.35:
        alerts.append(
            {
                "code": "low-accept-rate",
                "severity": "critical",
                "message": "Accept rate dropped below 35% in persisted feedback.",
                "value": round(accept_rate, 4),
                "threshold": 0.35,
            }
        )
    if feedback_count >= 12 and abs(feedback_signal) >= 0.45:
        alerts.append(
            {
                "code": "feedback-signal-drift",
                "severity": "warning",
                "message": "Feedback signal magnitude is above drift threshold.",
                "value": round(feedback_signal, 4),
                "threshold": 0.45,
            }
        )
    if relationship_count >= 12 and average_tension < 0.2:
        alerts.append(
            {
                "code": "low-relationship-tension",
                "severity": "warning",
                "message": "Average relationship tension is low for recent memory rows.",
                "value": round(average_tension, 4),
                "threshold": 0.2,
            }
        )
    if genres_tracked > 0 and auto_learning_ready_genres == 0:
        alerts.append(
            {
                "code": "genre-learning-not-ready",
                "severity": "info",
                "message": "Genre auto-learning has not reached minimum sample threshold.",
            }
        )
    if len(trend) >= 2:
        newest = trend[0]
        oldest = trend[-1]
        newest_signal = _safe_float(newest.get("feedbackSignal"), default=0.0)
        oldest_signal = _safe_float(oldest.get("feedbackSignal"), default=0.0)
        if newest_signal - oldest_signal <= -0.25:
            alerts.append(
                {
                    "code": "trend-signal-drop",
                    "severity": "warning",
                    "message": "Recent feedback signal dropped sharply versus long window.",
                    "value": round(newest_signal - oldest_signal, 4),
                    "threshold": -0.25,
                }
            )
    if runtime_count >= 8 and latency_p95_ms >= latency_threshold:
        alerts.append(
            {
                "code": "runtime-latency-p95-high",
                "severity": "warning",
                "message": "Runtime P95 latency exceeded configured threshold.",
                "value": round(latency_p95_ms, 3),
                "threshold": round(latency_threshold, 3),
            }
        )
    if runtime_count >= 8 and error_rate >= error_threshold:
        alerts.append(
            {
                "code": "runtime-error-rate-high",
                "severity": "critical",
                "message": "Runtime error rate exceeded configured threshold.",
                "value": round(error_rate, 4),
                "threshold": round(error_threshold, 4),
            }
        )
    if runtime_count >= 8 and fallback_rate >= fallback_threshold:
        alerts.append(
            {
                "code": "runtime-fallback-rate-high",
                "severity": "warning",
                "message": "Runtime fallback rate exceeded configured threshold.",
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
