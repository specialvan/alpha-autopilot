from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .models import ChapterDecompositionRecord

QC_REPORT_SCHEMA_VERSION = "1.0"


def build_projection_qc_report(
    records: list[ChapterDecompositionRecord],
    projections: list[dict[str, Any]],
    *,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    admission_distribution = Counter(record.admission for record in records)
    checkpoint_status_distribution = Counter(
        _normalize_label(checkpoint.status) for record in records for checkpoint in record.checkpoints
    )
    stage_distribution = Counter(_normalize_label(item.get("recommended_stage")) for item in projections)
    primary_function_distribution = Counter(_normalize_label(item.get("primary_function")) for item in projections)

    conflict_values: list[float] = []
    payoff_values: list[float] = []
    missing_signals = 0
    for item in projections:
        signals = item.get("narrative_signals", {})
        if not isinstance(signals, dict):
            missing_signals += 1
            continue
        if "conflict_intensity" in signals:
            try:
                conflict_values.append(float(signals["conflict_intensity"]))
            except Exception:
                pass
        if "payoff_pressure" in signals:
            try:
                payoff_values.append(float(signals["payoff_pressure"]))
            except Exception:
                pass
        if "conflict_intensity" not in signals and "payoff_pressure" not in signals:
            missing_signals += 1

    return {
        "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
        "schema_version": QC_REPORT_SCHEMA_VERSION,
        "record_count": len(records),
        "projection_count": len(projections),
        "admission_distribution": dict(sorted(admission_distribution.items())),
        "checkpoint_status_distribution": dict(sorted(checkpoint_status_distribution.items())),
        "stage_distribution": dict(sorted(stage_distribution.items())),
        "primary_function_distribution": dict(sorted(primary_function_distribution.items())),
        "avg_conflict_intensity": _safe_average(conflict_values),
        "avg_payoff_pressure": _safe_average(payoff_values),
        "missing_signal_count": missing_signals,
    }


def _safe_average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _normalize_label(value: Any) -> str:
    if value is None:
        return "unknown"
    label = str(value).strip()
    return label or "unknown"
