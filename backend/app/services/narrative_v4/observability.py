from __future__ import annotations

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
    trend = _build_feedback_trend(feedback_rows)
    alerts = _build_observability_alerts(
        relationship_rows=relationship_rows,
        feedback_rows=feedback_rows,
        average_tension=average_tension,
        feedback_signal=feedback_signal,
        accept_rate=accept_rate,
        genres_tracked=len(genres),
        auto_learning_ready_genres=auto_learning_ready_genres,
        trend=trend,
    )
    latest_timestamp = _latest_timestamp([*relationship_rows, *feedback_rows])

    return {
        "enabled": bool(relationship_rows or feedback_rows),
        "windowLimit": limit,
        "activeContexts": len(context_ids),
        "relationshipRows": len(relationship_rows),
        "feedbackRows": len(feedback_rows),
        "averageTension": average_tension,
        "feedbackSignal": feedback_signal,
        "acceptRate": accept_rate,
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
    average_tension: float,
    feedback_signal: float,
    accept_rate: float,
    genres_tracked: int,
    auto_learning_ready_genres: int,
    trend: list[dict[str, object]],
) -> list[dict[str, object]]:
    alerts: list[dict[str, object]] = []
    feedback_count = len(feedback_rows)
    relationship_count = len(relationship_rows)
    if feedback_count == 0:
        alerts.append(
            {
                "code": "no-feedback",
                "severity": "info",
                "message": "No persisted feedback rows yet.",
            }
        )
        return alerts

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
