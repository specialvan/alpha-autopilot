from __future__ import annotations

from .models import PlotCandidate

WINDOW_CONFIG: tuple[tuple[int, float], ...] = (
    (3, 0.5),
    (8, 0.3),
    (21, 0.2),
)
DECAY_FACTOR = 0.82


def rank_plot_candidates(
    candidates: list[PlotCandidate],
    retention_context: dict[str, object] | None = None,
) -> list[PlotCandidate]:
    context = retention_context if isinstance(retention_context, dict) else {}
    retention_weight = _safe_weight(context.get("retention_weight"), default=0.7)
    tension_weight = _safe_weight(context.get("tension_weight"), default=0.3)
    template_penalty = _safe_weight(context.get("template_penalty"), default=0.08)
    return sorted(
        candidates,
        key=lambda item: (
            round(
                retention_weight * item.retention_score
                + tension_weight * item.tension_score
                - template_penalty * _template_risk(item),
                6,
            ),
            item.retention_score,
            item.tension_score,
        ),
        reverse=True,
    )


def _safe_weight(value: object, *, default: float) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except Exception:
        return default
    return max(0.0, min(1.0, number))


def _template_risk(candidate: PlotCandidate) -> float:
    return 1.0 if "template-risk" in candidate.risk_flags else 0.0


def _safe_signed(value: object, *, default: float) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except Exception:
        return default
    return max(-1.0, min(1.0, number))


def apply_retention_feedback_writeback(retention_context: dict[str, object]) -> dict[str, object]:
    context = dict(retention_context)
    feedback_items = context.get("retention_feedback_history")
    if not isinstance(feedback_items, list) or not feedback_items:
        context["retention_writeback"] = {
            "feedback_count": 0,
            "feedback_valid_count": 0,
            "feedback_denoised_count": 0,
            "feedback_signal": 0.0,
            "adaptation_mode": "no-feedback",
            "aggregation_strategy": "multi-window-decay-denoise",
            "window_signals": [],
        }
        return context

    raw_signals = _extract_feedback_signals(feedback_items)
    denoised_signals, denoised_count = _denoise_signals(raw_signals)
    window_signals = _window_signals(
        denoised_signals,
        window_config=WINDOW_CONFIG,
        decay=DECAY_FACTOR,
    )
    feedback_signal = _aggregate_window_signals(window_signals)
    base_retention = _safe_weight(context.get("retention_weight"), default=0.7)
    base_tension = _safe_weight(context.get("tension_weight"), default=0.3)
    base_template_penalty = _safe_weight(context.get("template_penalty"), default=0.08)

    context["retention_weight"] = _safe_weight(base_retention + 0.08 * feedback_signal, default=base_retention)
    context["tension_weight"] = _safe_weight(base_tension + 0.06 * (-feedback_signal), default=base_tension)
    context["template_penalty"] = _safe_weight(
        base_template_penalty + 0.04 * (-feedback_signal),
        default=base_template_penalty,
    )
    context["retention_writeback"] = {
        "feedback_count": len(feedback_items),
        "feedback_valid_count": len(raw_signals),
        "feedback_denoised_count": denoised_count,
        "feedback_signal": round(feedback_signal, 4),
        "adaptation_mode": "feedback-driven-multi-window",
        "aggregation_strategy": "multi-window-decay-denoise",
        "window_signals": window_signals,
        "base_weights": {
            "retention_weight": base_retention,
            "tension_weight": base_tension,
            "template_penalty": base_template_penalty,
        },
        "adapted_weights": {
            "retention_weight": context["retention_weight"],
            "tension_weight": context["tension_weight"],
            "template_penalty": context["template_penalty"],
        },
    }
    return context


def _extract_feedback_signals(feedback_items: list[object]) -> list[float]:
    signals: list[float] = []
    for item in feedback_items:
        if not isinstance(item, dict):
            continue
        accepted_signal = 1.0 if item.get("accepted") else -1.0
        retention_delta = _safe_signed(item.get("retention_delta"), default=0.0)
        abandonment_delta = _safe_signed(item.get("abandonment_delta"), default=0.0)
        raw_signal = accepted_signal + retention_delta - abandonment_delta
        signals.append(raw_signal)
    return signals


def _denoise_signals(signals: list[float]) -> tuple[list[float], int]:
    if len(signals) < 4:
        return signals, 0
    median = _median(signals)
    deviations = [abs(item - median) for item in signals]
    mad = _median(deviations)
    if mad <= 0:
        return signals, 0
    threshold = 3.5 * 1.4826 * mad
    filtered = [item for item in signals if abs(item - median) <= threshold]
    if not filtered:
        return signals, 0
    return filtered, max(0, len(signals) - len(filtered))


def _window_signals(
    signals: list[float],
    *,
    window_config: tuple[tuple[int, float], ...],
    decay: float,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for window_size, weight in window_config:
        bucket = signals[-window_size:]
        if not bucket:
            continue
        rows.append(
            {
                "window_size": window_size,
                "count": len(bucket),
                "weight": weight,
                "signal": round(_decayed_average(bucket, decay=decay), 4),
            }
        )
    return rows


def _aggregate_window_signals(window_signals: list[dict[str, object]]) -> float:
    if not window_signals:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0.0
    for row in window_signals:
        signal = _safe_signed(row.get("signal"), default=0.0)
        weight = _safe_weight(row.get("weight"), default=0.0)
        if weight <= 0:
            continue
        weighted_sum += signal * weight
        total_weight += weight
    if total_weight <= 0:
        return 0.0
    return max(-1.0, min(1.0, round(weighted_sum / total_weight, 4)))


def _decayed_average(values: list[float], *, decay: float) -> float:
    if not values:
        return 0.0
    clamped_decay = max(0.0, min(1.0, decay))
    weighted_sum = 0.0
    total_weight = 0.0
    for index, value in enumerate(reversed(values)):
        weight = clamped_decay ** index
        weighted_sum += value * weight
        total_weight += weight
    if total_weight <= 0:
        return 0.0
    return weighted_sum / total_weight


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2
