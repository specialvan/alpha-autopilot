from __future__ import annotations

import json
import math

from alpha_autopilot_v4.integration import build_v4_to_v3_bridge_result
from ...core.config import settings
from .memory_store import V4MemoryStore

_GENRE_GUARD_OVERRIDE_CACHE: tuple[str | None, dict[str, dict[str, float | int]]] = (None, {})


def build_v4_bridge_payload(context: dict[str, object]) -> dict[str, object]:
    bridge = build_v4_to_v3_bridge_result(context)
    selected = bridge.plot_generation_result.selected_candidate
    candidates = [
        {
            "candidate_id": item.candidate_id,
            "predicted_action": item.predicted_action,
            "predicted_turning_point": item.predicted_turning_point,
            "predicted_conflict_type": item.predicted_conflict_type,
            "predicted_payoff_type": item.predicted_payoff_type,
            "retention_score": item.retention_score,
            "tension_score": item.tension_score,
            "explanation": item.explanation,
            "risk_flags": item.risk_flags,
        }
        for item in bridge.plot_generation_result.plot_candidates
    ]
    return {
        "enabled": bridge.enabled,
        "fallback_reason": bridge.fallback_reason,
        "retention_sort_key": bridge.retention_sort_key,
        "candidate_count": len(bridge.plot_generation_result.plot_candidates),
        "plot_candidates": candidates,
        "selected_candidate": None if selected is None else {
            "candidate_id": selected.candidate_id,
            "predicted_action": selected.predicted_action,
            "predicted_turning_point": selected.predicted_turning_point,
            "predicted_conflict_type": selected.predicted_conflict_type,
            "predicted_payoff_type": selected.predicted_payoff_type,
            "retention_score": selected.retention_score,
            "tension_score": selected.tension_score,
            "explanation": selected.explanation,
            "risk_flags": selected.risk_flags,
        },
        "v3_context": bridge.v3_context,
        "qc_summary": bridge.qc_summary or {},
        "relationship_graph": bridge.v3_context.get("relationship_graph", {}),
        "relationship_displacements": bridge.v3_context.get("relationship_displacements", []),
        "retention_writeback": bridge.v3_context.get("retention_writeback", {}),
        "memory_summary": {
            "relationship_history_count": len(context.get("relationship_history", []))
            if isinstance(context.get("relationship_history"), list)
            else 0,
            "feedback_history_count": len(context.get("v3_feedback_history", []))
            if isinstance(context.get("v3_feedback_history"), list)
            else 0,
        },
    }


def build_v4_bridge_payload_with_memory(
    context: dict[str, object],
    *,
    memory_store: V4MemoryStore | None = None,
    context_id: str | None = None,
    history_window: int = 50,
) -> dict[str, object]:
    context_payload = dict(context)
    resolved_context_id = context_id or str(
        context_payload.get("id")
        or context_payload.get("case_id")
        or "global"
    )
    incoming_relationship_history = context_payload.get("relationship_history")
    if not isinstance(incoming_relationship_history, list):
        incoming_relationship_history = []
    incoming_feedback_history = context_payload.get("v3_feedback_history")
    if not isinstance(incoming_feedback_history, list):
        incoming_feedback_history = []

    relationship_history = list(incoming_relationship_history)
    feedback_history = list(incoming_feedback_history)
    relationship_merge_denoised_count = 0
    feedback_merge_denoised_count = 0

    if memory_store is not None:
        stored_relationship_history = memory_store.read_relationship_history(
            resolved_context_id,
            limit=history_window,
        )
        stored_feedback_history = memory_store.read_feedback_history(
            resolved_context_id,
            limit=history_window,
        )
        relationship_history, relationship_merge_denoised_count = _merge_history_rows(
            stored_relationship_history,
            relationship_history,
            limit=history_window,
        )
        feedback_history, feedback_merge_denoised_count = _merge_history_rows(
            stored_feedback_history,
            feedback_history,
            limit=history_window,
        )
    else:
        relationship_history, relationship_merge_denoised_count = _merge_history_rows(
            [],
            relationship_history,
            limit=history_window,
        )
        feedback_history, feedback_merge_denoised_count = _merge_history_rows(
            [],
            feedback_history,
            limit=history_window,
        )

    relationship_history, relationship_memory_stats = _prepare_relationship_history(
        relationship_history,
        limit=history_window,
    )
    feedback_history, feedback_memory_stats = _prepare_feedback_history(
        feedback_history,
        limit=history_window,
    )
    genre = _resolve_genre_from_context(context_payload)
    genre_feedback_history: list[dict[str, object]] = []
    if memory_store is not None and genre:
        genre_feedback_history = memory_store.read_feedback_history_by_genre(
            genre,
            limit=max(history_window * 4, 80),
        )
    genre_calibration = _derive_genre_auto_calibration(
        genre=genre,
        feedback_history=feedback_history,
        genre_feedback_history=genre_feedback_history,
    )
    _inject_genre_auto_calibration(context_payload, genre_calibration)

    context_payload["relationship_history"] = relationship_history
    context_payload["v3_feedback_history"] = feedback_history
    payload = build_v4_bridge_payload(context_payload)
    chapter_index = _safe_int(context_payload.get("chapter_index"), default=None)
    relationship_timeline = _build_relationship_timeline(
        relationship_history,
        relationship_displacements=payload.get("relationship_displacements", []),
        chapter_index=chapter_index,
        limit=min(history_window, 12),
    )
    if not relationship_timeline:
        relationship_timeline = _build_graph_fallback_timeline(
            payload.get("relationship_graph", {}),
            chapter_index=chapter_index,
            relationship_displacements=payload.get("relationship_displacements", []),
        )
    candidate_timeline = _build_candidate_timeline(
        feedback_history,
        fallback_chapter_index=chapter_index,
        limit=min(history_window, 12),
    )
    if not candidate_timeline:
        candidate_timeline = _build_candidate_fallback_timeline(
            payload.get("selected_candidate"),
            chapter_index=chapter_index,
        )
    payload["relationship_timeline"] = relationship_timeline
    payload["candidate_timeline"] = candidate_timeline
    payload["genre_calibration"] = genre_calibration
    memory_summary = dict(payload.get("memory_summary", {}))
    memory_summary["context_id"] = resolved_context_id
    memory_summary["history_window"] = history_window
    memory_summary["memory_strategy"] = "append-window-decay-denoise-v2"
    memory_summary["relationship_merge_deduped_count"] = relationship_merge_denoised_count
    memory_summary["feedback_merge_deduped_count"] = feedback_merge_denoised_count
    memory_summary["relationship_collapsed_count"] = relationship_memory_stats["collapsed"]
    memory_summary["feedback_collapsed_count"] = feedback_memory_stats["deduped"]
    memory_summary["relationship_clipped_count"] = relationship_memory_stats["clipped"]
    memory_summary["feedback_clipped_count"] = feedback_memory_stats["clipped"]
    memory_summary["relationship_decay_dropped_count"] = relationship_memory_stats["decay_dropped"]
    memory_summary["feedback_decay_dropped_count"] = feedback_memory_stats["decay_dropped"]
    memory_summary["relationship_denoised_count"] = (
        relationship_merge_denoised_count
        + relationship_memory_stats["collapsed"]
        + relationship_memory_stats["clipped"]
    )
    memory_summary["feedback_denoised_count"] = (
        feedback_merge_denoised_count
        + feedback_memory_stats["deduped"]
        + feedback_memory_stats["clipped"]
    )
    memory_summary["relationship_timeline_count"] = len(relationship_timeline)
    memory_summary["candidate_timeline_count"] = len(candidate_timeline)
    memory_summary["relationship_timeline_displacement_count"] = sum(
        _safe_int(item.get("displacement_count"), default=0) or 0
        for item in relationship_timeline
        if isinstance(item, dict)
    )
    memory_summary["genre_auto_learning_mode"] = str(
        genre_calibration.get("learning_mode", "disabled"),
    )
    memory_summary["genre_auto_learning_applied"] = bool(
        genre_calibration.get("applied", False),
    )
    memory_summary["genre_auto_learning_sample_count"] = _safe_int(
        genre_calibration.get("sample_count"),
        default=0,
    ) or 0
    memory_summary["genre_auto_learning_denoised_count"] = _safe_int(
        genre_calibration.get("denoised_count"),
        default=0,
    ) or 0
    memory_summary["genre_auto_learning_feedback_signal"] = round(
        _safe_float(genre_calibration.get("feedback_signal"), default=0.0),
        4,
    )
    memory_summary["genre_auto_learning_bias_count"] = len(
        genre_calibration.get("bias_updates", {})
        if isinstance(genre_calibration.get("bias_updates"), dict)
        else {},
    )
    memory_summary["genre_auto_learning_guard_triggered"] = bool(
        genre_calibration.get("guard_triggered", False),
    )
    guard_reason = genre_calibration.get("guard_reason")
    if isinstance(guard_reason, str) and guard_reason:
        memory_summary["genre_auto_learning_guard_reason"] = guard_reason
    fallback_mode = genre_calibration.get("fallback_mode")
    if isinstance(fallback_mode, str) and fallback_mode:
        memory_summary["genre_auto_learning_fallback_mode"] = fallback_mode
    guard_profile = genre_calibration.get("guard_profile")
    if isinstance(guard_profile, dict):
        memory_summary["genre_auto_learning_guard_profile"] = {
            "min_samples": _safe_int(guard_profile.get("min_samples"), default=0) or 0,
            "decay": round(_safe_float(guard_profile.get("decay"), default=0.0), 4),
            "bias_limit": round(_safe_float(guard_profile.get("bias_limit"), default=0.0), 4),
            "max_volatility": round(_safe_float(guard_profile.get("max_volatility"), default=0.0), 4),
            "max_signal_divergence": round(
                _safe_float(guard_profile.get("max_signal_divergence"), default=0.0),
                4,
            ),
            "extreme_signal": round(_safe_float(guard_profile.get("extreme_signal"), default=0.0), 4),
            "extreme_min_samples": _safe_int(guard_profile.get("extreme_min_samples"), default=0) or 0,
            "reversal_divergence_min": round(
                _safe_float(guard_profile.get("reversal_divergence_min"), default=0.0),
                4,
            ),
        }
    payload["memory_summary"] = memory_summary

    if memory_store is not None:
        memory_store.append_feedback_history(
            resolved_context_id,
            feedback_history,
            source="v4-bridge-input",
            chapter_index=chapter_index,
            genre=genre,
        )
        memory_store.append_relationship_snapshot(
            resolved_context_id,
            chapter_index=_safe_int(context_payload.get("chapter_index"), default=None),
            payload=payload,
        )

    return payload


def build_v4_workbench_preview(
    context: dict[str, object],
    *,
    memory_store: V4MemoryStore | None = None,
    history_window: int = 50,
) -> dict[str, object]:
    state = context.get("state")
    if not isinstance(state, dict):
        return {
            "enabled": False,
            "fallback_reason": "missing-state",
            "candidate_count": 0,
            "selected_candidate": None,
            "top_candidates": [],
            "qc_summary": {"warnings": ["missing-state"]},
            "memory_summary": {
                "relationship_history_count": 0,
                "feedback_history_count": 0,
                "relationship_denoised_count": 0,
                "feedback_denoised_count": 0,
                "relationship_timeline_count": 0,
                "candidate_timeline_count": 0,
                "genre_auto_learning_mode": "disabled",
                "genre_auto_learning_applied": False,
                "genre_auto_learning_sample_count": 0,
                "genre_auto_learning_denoised_count": 0,
                "genre_auto_learning_feedback_signal": 0.0,
                "genre_auto_learning_bias_count": 0,
                "genre_auto_learning_guard_triggered": False,
                "genre_auto_learning_fallback_mode": "missing-state",
            },
            "relationship_timeline": [],
            "candidate_timeline": [],
            "genre_calibration": {},
            "v4_input_profile": {},
        }

    v4_context = _v2_state_to_v4_context(
        state,
        context_id=str(context.get("id", "workbench-context")),
        raw_context=context,
    )
    payload = build_v4_bridge_payload_with_memory(
        v4_context,
        memory_store=memory_store,
        context_id=str(context.get("id", "workbench-context")),
        history_window=history_window,
    )
    plot_candidates = payload.get("plot_candidates", [])
    selected_candidate = payload.get("selected_candidate")
    top_candidates = plot_candidates[:3] if isinstance(plot_candidates, list) else []

    return {
        "enabled": bool(payload.get("enabled", False)),
        "fallback_reason": payload.get("fallback_reason"),
        "candidate_count": int(payload.get("candidate_count", 0)),
        "retention_sort_key": payload.get("retention_sort_key", "retention_score"),
        "selected_candidate": _workbench_candidate_view(selected_candidate),
        "top_candidates": [
            item_view
            for item_view in (_workbench_candidate_view(item) for item in top_candidates)
            if item_view is not None
        ],
        "qc_summary": payload.get("qc_summary", {}),
        "relationship_graph": payload.get("relationship_graph", {}),
        "relationship_displacements": payload.get("relationship_displacements", []),
        "relationship_timeline": payload.get("relationship_timeline", []),
        "candidate_timeline": payload.get("candidate_timeline", []),
        "genre_calibration": payload.get("genre_calibration", {}),
        "retention_writeback": payload.get("retention_writeback", {}),
        "memory_summary": payload.get("memory_summary", {}),
        "v4_input_profile": {
            "chapter_index": _safe_int(state.get("chapter_index"), default=0),
            "stage": str(state.get("stage", "unknown")),
            "mainline_progress": _bounded_float(state.get("mainline_progress"), 0.5),
            "sideplot_progress": _bounded_float(state.get("sideplot_progress"), 0.5),
            "conflict_intensity": _bounded_float(state.get("conflict_intensity"), 0.5),
            "payoff_pressure": _bounded_float(state.get("payoff_pressure"), 0.5),
            "foreshadowing_load": _bounded_float(state.get("foreshadowing_load"), 0.5),
        },
    }


def _bounded_float(value: object, default: float = 0.5) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except Exception:
        return default
    return max(0.0, min(1.0, round(number, 4)))


def _safe_int(value: object, *, default: int | None) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _merge_history_rows(
    left: list[dict[str, object]],
    right: list[dict[str, object]],
    *,
    limit: int,
) -> tuple[list[dict[str, object]], int]:
    merged: list[dict[str, object]] = []
    seen: set[str] = set()
    deduped = 0
    for item in [*left, *right]:
        if isinstance(item, dict):
            row = dict(item)
            key = _history_key(row)
            if key in seen:
                deduped += 1
                continue
            seen.add(key)
            merged.append(row)
    if len(merged) <= limit:
        return merged, deduped
    dropped = len(merged) - limit
    return merged[-limit:], deduped + dropped


def _history_key(row: dict[str, object]) -> str:
    normalized = {key: _normalize_history_value(value) for key, value in row.items()}
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True)


def _normalize_history_value(value: object) -> object:
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, (int, str, bool)) or value is None:
        return value
    return str(value)


def _prepare_relationship_history(
    relationship_history: list[dict[str, object]],
    *,
    limit: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    sanitized_rows: list[dict[str, object]] = []
    clipped_count = 0
    invalid_count = 0
    for row in relationship_history:
        if not isinstance(row, dict):
            invalid_count += 1
            continue
        source_character = str(row.get("source_character", "")).strip()
        target_character = str(row.get("target_character", "")).strip()
        if not source_character or not target_character:
            invalid_count += 1
            continue
        tension_raw = _safe_float(row.get("tension_score"), default=0.0)
        tension_score = max(0.0, min(1.0, round(tension_raw, 4)))
        if abs(tension_score - tension_raw) > 1e-6:
            clipped_count += 1
        sanitized_rows.append(
            {
                "source_character": source_character,
                "target_character": target_character,
                "tension_score": tension_score,
                "dominant_gap": str(row.get("dominant_gap", "status")) or "status",
                "chapter_index": _safe_int(row.get("chapter_index"), default=None),
            }
        )

    collapsed_rows, collapsed_count = _collapse_relationship_rows(sanitized_rows)
    decayed_rows, decay_dropped_count = _apply_history_decay_filter(
        collapsed_rows,
        limit=limit,
        min_recent=max(6, min(12, limit // 2)),
        half_life=max(4, limit // 3),
        floor=0.04,
        score_fn=lambda item: _safe_float(item.get("tension_score"), default=0.0),
    )
    return decayed_rows, {
        "collapsed": collapsed_count + invalid_count,
        "clipped": clipped_count,
        "decay_dropped": decay_dropped_count,
    }


def _collapse_relationship_rows(
    relationship_history: list[dict[str, object]],
) -> tuple[list[dict[str, object]], int]:
    grouped: dict[tuple[str, str, int | None], dict[str, object]] = {}
    for index, row in enumerate(relationship_history):
        source_character = str(row.get("source_character", ""))
        target_character = str(row.get("target_character", ""))
        pair_left, pair_right = sorted((source_character, target_character))
        chapter_index = _safe_int(row.get("chapter_index"), default=None)
        key = (pair_left, pair_right, chapter_index)
        group = grouped.setdefault(
            key,
            {
                "source_character": pair_left,
                "target_character": pair_right,
                "chapter_index": chapter_index,
                "tension_sum": 0.0,
                "count": 0,
                "gap_counts": {},
                "last_index": index,
            },
        )
        group["tension_sum"] = _safe_float(group.get("tension_sum"), default=0.0) + _safe_float(
            row.get("tension_score"),
            default=0.0,
        )
        group["count"] = (_safe_int(group.get("count"), default=0) or 0) + 1
        dominant_gap = str(row.get("dominant_gap", "status")) or "status"
        gap_counts = group.get("gap_counts")
        if isinstance(gap_counts, dict):
            gap_counts[dominant_gap] = int(gap_counts.get(dominant_gap, 0)) + 1
        group["last_index"] = index

    collapsed: list[dict[str, object]] = []
    collapsed_count = 0
    for group in sorted(
        grouped.values(),
        key=lambda item: _safe_int(item.get("last_index"), default=0) or 0,
    ):
        count = _safe_int(group.get("count"), default=0) or 0
        if count <= 0:
            continue
        collapsed_count += max(0, count - 1)
        tension_score = round(_safe_float(group.get("tension_sum"), default=0.0) / count, 4)
        collapsed.append(
            {
                "source_character": str(group.get("source_character", "")),
                "target_character": str(group.get("target_character", "")),
                "chapter_index": _safe_int(group.get("chapter_index"), default=None),
                "tension_score": tension_score,
                "dominant_gap": _dominant_gap_from_counts(group.get("gap_counts")),
            }
        )
    return collapsed, collapsed_count


def _prepare_feedback_history(
    feedback_history: list[dict[str, object]],
    *,
    limit: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    sanitized_rows: list[dict[str, object]] = []
    clipped_count = 0
    invalid_count = 0
    for row in feedback_history:
        if not isinstance(row, dict):
            invalid_count += 1
            continue
        retention_raw = _safe_float(row.get("retention_delta"), default=0.0)
        abandonment_raw = _safe_float(row.get("abandonment_delta"), default=0.0)
        retention_delta = max(-1.0, min(1.0, round(retention_raw, 4)))
        abandonment_delta = max(-1.0, min(1.0, round(abandonment_raw, 4)))
        if abs(retention_delta - retention_raw) > 1e-6:
            clipped_count += 1
        if abs(abandonment_delta - abandonment_raw) > 1e-6:
            clipped_count += 1
        sanitized_rows.append(
            {
                "accepted": bool(row.get("accepted", False)),
                "retention_delta": retention_delta,
                "abandonment_delta": abandonment_delta,
                "chapter_index": _safe_int(row.get("chapter_index"), default=None),
            }
        )

    deduped_rows, deduped_count = _dedupe_feedback_rows(sanitized_rows)
    decayed_rows, decay_dropped_count = _apply_history_decay_filter(
        deduped_rows,
        limit=limit,
        min_recent=max(8, min(14, limit // 2)),
        half_life=max(5, limit // 2),
        floor=0.03,
        score_fn=lambda item: abs(_feedback_signal(item)),
    )
    return decayed_rows, {
        "deduped": deduped_count + invalid_count,
        "clipped": clipped_count,
        "decay_dropped": decay_dropped_count,
    }


def _dedupe_feedback_rows(
    feedback_history: list[dict[str, object]],
) -> tuple[list[dict[str, object]], int]:
    deduped_reversed: list[dict[str, object]] = []
    seen: set[tuple[bool, float, float, int | None]] = set()
    deduped_count = 0
    for row in reversed(feedback_history):
        key = (
            bool(row.get("accepted", False)),
            round(_safe_float(row.get("retention_delta"), default=0.0), 4),
            round(_safe_float(row.get("abandonment_delta"), default=0.0), 4),
            _safe_int(row.get("chapter_index"), default=None),
        )
        if key in seen:
            deduped_count += 1
            continue
        seen.add(key)
        deduped_reversed.append(dict(row))
    deduped_reversed.reverse()
    return deduped_reversed, deduped_count


def _apply_history_decay_filter(
    rows: list[dict[str, object]],
    *,
    limit: int,
    min_recent: int,
    half_life: int,
    floor: float,
    score_fn,
) -> tuple[list[dict[str, object]], int]:
    if not rows:
        return [], 0

    kept: list[dict[str, object]] = []
    dropped_count = 0
    total = len(rows)
    for index, row in enumerate(rows):
        age = total - index - 1
        if age < min_recent:
            kept.append(row)
            continue
        signal = max(0.0, float(score_fn(row)))
        decay_weight = math.pow(0.5, (age - min_recent + 1) / max(1, half_life))
        if signal * decay_weight >= floor:
            kept.append(row)
        else:
            dropped_count += 1

    if not kept:
        kept = [rows[-1]]

    if len(kept) > limit:
        dropped_count += len(kept) - limit
        kept = kept[-limit:]

    return kept, dropped_count


def _feedback_signal(item: dict[str, object]) -> float:
    retention_delta = _safe_float(item.get("retention_delta"), default=0.0)
    abandonment_delta = _safe_float(item.get("abandonment_delta"), default=0.0)
    return retention_delta - abandonment_delta


def _resolve_genre_from_context(context: dict[str, object]) -> str:
    profile = context.get("genre_profile")
    if isinstance(profile, dict):
        genre = str(profile.get("genre", "")).strip().lower()
        if genre:
            return genre
    return str(context.get("genre", "")).strip().lower()


def _derive_genre_auto_calibration(
    *,
    genre: str,
    feedback_history: list[dict[str, object]],
    genre_feedback_history: list[dict[str, object]],
) -> dict[str, object]:
    normalized_genre = genre.strip().lower()
    guard_profile = _resolve_genre_guard_profile(normalized_genre)
    history_sources = {
        "context_feedback_count": len(feedback_history),
        "genre_feedback_count": len(genre_feedback_history),
    }
    if not normalized_genre:
        return {
            "genre": "",
            "learning_mode": "disabled-no-genre",
            "applied": False,
            "feedback_signal": 0.0,
            "sample_count": 0,
            "denoised_count": 0,
            "bias_updates": {},
            "guard_triggered": False,
            "guard_reason": None,
            "fallback_mode": "no-op",
            "accept_rate": 0.0,
            "signal_recent": 0.0,
            "signal_long": 0.0,
            "signal_volatility": 0.0,
            "signal_divergence": 0.0,
            "guard_profile": guard_profile,
            "history_sources": history_sources,
        }

    learning_rows = _dedupe_genre_learning_rows(
        [*genre_feedback_history, *feedback_history],
    )
    signals = _extract_genre_feedback_signals(learning_rows)
    accepted_count = sum(1 for row in learning_rows if bool(row.get("accepted", False)))
    sample_count = len(signals)
    accept_rate = round(accepted_count / sample_count, 4) if sample_count else 0.0
    min_samples = int(guard_profile["min_samples"])
    if len(signals) < min_samples:
        return {
            "genre": normalized_genre,
            "learning_mode": "disabled-low-sample",
            "applied": False,
            "feedback_signal": 0.0,
            "sample_count": len(signals),
            "denoised_count": 0,
            "bias_updates": {},
            "guard_triggered": False,
            "guard_reason": None,
            "fallback_mode": "no-op",
            "accept_rate": accept_rate,
            "signal_recent": 0.0,
            "signal_long": 0.0,
            "signal_volatility": 0.0,
            "signal_divergence": 0.0,
            "guard_profile": guard_profile,
            "history_sources": history_sources,
        }

    denoised_signals, denoised_count = _denoise_numeric_signals(signals)
    usable_signals = denoised_signals if len(denoised_signals) >= min_samples else signals
    feedback_signal = _clamp_signed(
        _decayed_average_signals(
            usable_signals,
            decay=float(guard_profile["decay"]),
        ),
    )
    recent_window = usable_signals[-min(6, len(usable_signals)):]
    long_window = usable_signals[-min(18, len(usable_signals)):]
    recent_signal = _clamp_signed(_decayed_average_signals(recent_window, decay=0.85))
    long_signal = _clamp_signed(_decayed_average_signals(long_window, decay=0.93))
    signal_divergence = round(abs(recent_signal - long_signal), 4)
    signal_volatility = round(_stddev_numeric(usable_signals), 4)
    guard_reason = _detect_genre_calibration_guard(
        sample_count=len(usable_signals),
        feedback_signal=feedback_signal,
        recent_signal=recent_signal,
        long_signal=long_signal,
        signal_volatility=signal_volatility,
        signal_divergence=signal_divergence,
        guard_profile=guard_profile,
    )
    guarded = guard_reason is not None
    bias_updates = {} if guarded else _genre_bias_updates_from_signal(
        feedback_signal,
        bias_limit=float(guard_profile["bias_limit"]),
    )
    fallback_mode = "no-bias-update" if guarded else (
        "bias-update-applied" if bias_updates else "no-op-low-signal"
    )
    return {
        "genre": normalized_genre,
        "learning_mode": "feedback-adaptive-v1-guarded" if guarded else "feedback-adaptive-v1",
        "applied": bool(bias_updates),
        "feedback_signal": round(feedback_signal, 4),
        "sample_count": len(signals),
        "denoised_count": denoised_count,
        "bias_updates": bias_updates,
        "guard_triggered": guarded,
        "guard_reason": guard_reason,
        "fallback_mode": fallback_mode,
        "accept_rate": accept_rate,
        "signal_recent": recent_signal,
        "signal_long": long_signal,
        "signal_volatility": signal_volatility,
        "signal_divergence": signal_divergence,
        "guard_profile": guard_profile,
        "history_sources": history_sources,
    }


def _inject_genre_auto_calibration(
    context: dict[str, object],
    genre_calibration: dict[str, object],
) -> None:
    bias_updates = genre_calibration.get("bias_updates")
    if not isinstance(bias_updates, dict) or not bias_updates:
        return

    genre_profile = context.get("genre_profile")
    if not isinstance(genre_profile, dict):
        genre_profile = {}
    else:
        genre_profile = dict(genre_profile)

    resolved_genre = str(genre_calibration.get("genre", "")).strip().lower()
    guard_profile = genre_calibration.get("guard_profile")
    if isinstance(guard_profile, dict):
        bias_limit = _safe_float(guard_profile.get("bias_limit"), default=0.12)
    else:
        bias_limit = 0.12
    if resolved_genre and not str(genre_profile.get("genre", "")).strip():
        genre_profile["genre"] = resolved_genre

    for raw_key, raw_value in bias_updates.items():
        if not isinstance(raw_key, str) or not raw_key.endswith("_bias"):
            continue
        base_value = _safe_float(genre_profile.get(raw_key), default=0.0)
        update_value = _safe_float(raw_value, default=0.0)
        genre_profile[raw_key] = _clip_bias(base_value + update_value, bias_limit=bias_limit)

    genre_profile["auto_calibration_mode"] = str(genre_calibration.get("learning_mode", "unknown"))
    genre_profile["auto_calibration_signal"] = round(
        _safe_float(genre_calibration.get("feedback_signal"), default=0.0),
        4,
    )
    genre_profile["auto_calibration_sample_count"] = _safe_int(
        genre_calibration.get("sample_count"),
        default=0,
    ) or 0
    context["genre_profile"] = genre_profile
    if resolved_genre:
        context["genre"] = resolved_genre


def _extract_genre_feedback_signals(rows: list[dict[str, object]]) -> list[float]:
    signals: list[float] = []
    for row in rows:
        accepted_signal = 0.6 if bool(row.get("accepted", False)) else -0.6
        combined = accepted_signal + 0.4 * _feedback_signal(row)
        signals.append(_clamp_signed(combined))
    return signals


def _dedupe_genre_learning_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped_reversed: list[dict[str, object]] = []
    seen: set[tuple[bool, float, float, int | None, str]] = set()
    for row in reversed(rows):
        if not isinstance(row, dict):
            continue
        key = (
            bool(row.get("accepted", False)),
            round(_safe_float(row.get("retention_delta"), default=0.0), 4),
            round(_safe_float(row.get("abandonment_delta"), default=0.0), 4),
            _safe_int(row.get("chapter_index"), default=None),
            str(row.get("context_id", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped_reversed.append(dict(row))
    deduped_reversed.reverse()
    return deduped_reversed


def _denoise_numeric_signals(signals: list[float]) -> tuple[list[float], int]:
    if len(signals) < 5:
        return signals, 0
    median = _median_numeric(signals)
    deviations = [abs(item - median) for item in signals]
    mad = _median_numeric(deviations)
    if mad <= 0:
        return signals, 0
    threshold = 3.5 * 1.4826 * mad
    filtered = [item for item in signals if abs(item - median) <= threshold]
    if not filtered:
        return signals, 0
    return filtered, max(0, len(signals) - len(filtered))


def _median_numeric(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2


def _decayed_average_signals(values: list[float], *, decay: float) -> float:
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


def _detect_genre_calibration_guard(
    *,
    sample_count: int,
    feedback_signal: float,
    recent_signal: float,
    long_signal: float,
    signal_volatility: float,
    signal_divergence: float,
    guard_profile: dict[str, float | int],
) -> str | None:
    max_volatility = _safe_float(guard_profile.get("max_volatility"), default=0.58)
    max_signal_divergence = _safe_float(guard_profile.get("max_signal_divergence"), default=0.32)
    extreme_signal = _safe_float(guard_profile.get("extreme_signal"), default=0.82)
    extreme_min_samples = _safe_int(guard_profile.get("extreme_min_samples"), default=10) or 10
    reversal_divergence_min = _safe_float(guard_profile.get("reversal_divergence_min"), default=0.24)
    if signal_volatility > max_volatility:
        return "high-volatility"
    if signal_divergence > max_signal_divergence:
        return "recent-long-divergence"
    if (
        abs(feedback_signal) >= extreme_signal
        and sample_count < extreme_min_samples
    ):
        return "extreme-signal-low-sample"
    # A sharp recent/long sign reversal is treated as unstable and keeps bias untouched.
    if recent_signal * long_signal < 0 and abs(recent_signal - long_signal) > reversal_divergence_min:
        return "signal-reversal"
    return None


def _stddev_numeric(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((item - mean_value) ** 2 for item in values) / len(values)
    return math.sqrt(max(0.0, variance))


def _resolve_genre_guard_profile(genre: str) -> dict[str, float | int]:
    profile = _default_genre_guard_profile()
    overrides = _genre_guard_overrides()
    wildcard = overrides.get("*")
    if isinstance(wildcard, dict):
        profile = _merge_guard_profile(profile, wildcard)
    specific = overrides.get(genre.strip().lower())
    if isinstance(specific, dict):
        profile = _merge_guard_profile(profile, specific)
    return profile


def _default_genre_guard_profile() -> dict[str, float | int]:
    return {
        "min_samples": max(1, int(getattr(settings, "v4_genre_auto_min_samples", 4))),
        "decay": _clamp01(_safe_float(getattr(settings, "v4_genre_auto_decay", 0.9), default=0.9)),
        "bias_limit": _clamp_range(
            _safe_float(getattr(settings, "v4_genre_auto_bias_limit", 0.12), default=0.12),
            lower=0.01,
            upper=0.5,
        ),
        "max_volatility": _clamp_range(
            _safe_float(getattr(settings, "v4_genre_auto_max_volatility", 0.58), default=0.58),
            lower=0.01,
            upper=2.0,
        ),
        "max_signal_divergence": _clamp_range(
            _safe_float(
                getattr(settings, "v4_genre_auto_max_signal_divergence", 0.32),
                default=0.32,
            ),
            lower=0.01,
            upper=2.0,
        ),
        "extreme_signal": _clamp01(
            _safe_float(getattr(settings, "v4_genre_auto_extreme_signal", 0.82), default=0.82),
        ),
        "extreme_min_samples": max(
            1,
            int(getattr(settings, "v4_genre_auto_extreme_min_samples", 10)),
        ),
        "reversal_divergence_min": _clamp_range(
            _safe_float(
                getattr(settings, "v4_genre_auto_reversal_divergence_min", 0.24),
                default=0.24,
            ),
            lower=0.01,
            upper=2.0,
        ),
    }


def _genre_guard_overrides() -> dict[str, dict[str, float | int]]:
    global _GENRE_GUARD_OVERRIDE_CACHE
    raw = getattr(settings, "v4_genre_guard_overrides_json", None)
    if not isinstance(raw, str):
        raw = ""
    if _GENRE_GUARD_OVERRIDE_CACHE[0] == raw:
        return _GENRE_GUARD_OVERRIDE_CACHE[1]
    parsed = _parse_guard_overrides(raw)
    _GENRE_GUARD_OVERRIDE_CACHE = (raw, parsed)
    return parsed


def _parse_guard_overrides(raw: str) -> dict[str, dict[str, float | int]]:
    content = raw.strip()
    if not content:
        return {}
    try:
        payload = json.loads(content)
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    parsed: dict[str, dict[str, float | int]] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        normalized_key = key.strip().lower()
        if not normalized_key:
            continue
        parsed[normalized_key] = _coerce_guard_profile(value)
    return parsed


def _coerce_guard_profile(raw: dict[str, object]) -> dict[str, float | int]:
    profile: dict[str, float | int] = {}
    if "min_samples" in raw:
        profile["min_samples"] = max(1, _safe_int(raw.get("min_samples"), default=1) or 1)
    if "decay" in raw:
        profile["decay"] = _clamp01(_safe_float(raw.get("decay"), default=0.9))
    if "bias_limit" in raw:
        profile["bias_limit"] = _clamp_range(
            _safe_float(raw.get("bias_limit"), default=0.12),
            lower=0.01,
            upper=0.5,
        )
    if "max_volatility" in raw:
        profile["max_volatility"] = _clamp_range(
            _safe_float(raw.get("max_volatility"), default=0.58),
            lower=0.01,
            upper=2.0,
        )
    if "max_signal_divergence" in raw:
        profile["max_signal_divergence"] = _clamp_range(
            _safe_float(raw.get("max_signal_divergence"), default=0.32),
            lower=0.01,
            upper=2.0,
        )
    if "extreme_signal" in raw:
        profile["extreme_signal"] = _clamp01(_safe_float(raw.get("extreme_signal"), default=0.82))
    if "extreme_min_samples" in raw:
        profile["extreme_min_samples"] = max(
            1,
            _safe_int(raw.get("extreme_min_samples"), default=1) or 1,
        )
    if "reversal_divergence_min" in raw:
        profile["reversal_divergence_min"] = _clamp_range(
            _safe_float(raw.get("reversal_divergence_min"), default=0.24),
            lower=0.01,
            upper=2.0,
        )
    return profile


def _merge_guard_profile(
    base: dict[str, float | int],
    override: dict[str, float | int],
) -> dict[str, float | int]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged:
            merged[key] = value
    return merged


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _clamp_range(value: float, *, lower: float, upper: float) -> float:
    return max(lower, min(upper, round(value, 4)))


def _genre_bias_updates_from_signal(
    feedback_signal: float,
    *,
    bias_limit: float,
) -> dict[str, float]:
    clamped_signal = _clamp_signed(feedback_signal)
    amplitude = abs(clamped_signal)
    if amplitude < 0.05:
        return {}
    if clamped_signal >= 0:
        updates = {
            "directness_bias": 0.06 * amplitude,
            "assertiveness_bias": 0.07 * amplitude,
            "risk_appetite_bias": 0.09 * amplitude,
            "avoidance_bias": -0.07 * amplitude,
            "self_protection_bias": -0.04 * amplitude,
        }
    else:
        updates = {
            "directness_bias": -0.05 * amplitude,
            "assertiveness_bias": -0.06 * amplitude,
            "risk_appetite_bias": -0.09 * amplitude,
            "avoidance_bias": 0.08 * amplitude,
            "calmness_bias": 0.05 * amplitude,
            "pragmatism_bias": 0.04 * amplitude,
        }
    return {
        key: _clip_bias(round(value, 4), bias_limit=bias_limit)
        for key, value in updates.items()
        if abs(value) >= 0.002
    }


def _clamp_signed(value: float) -> float:
    return max(-1.0, min(1.0, round(value, 4)))


def _clip_bias(value: float, *, bias_limit: float) -> float:
    limit = max(0.01, min(0.5, abs(float(bias_limit))))
    return max(-limit, min(limit, round(value, 4)))


def _build_relationship_timeline(
    relationship_history: list[dict[str, object]],
    *,
    relationship_displacements: object,
    chapter_index: int | None,
    limit: int,
) -> list[dict[str, object]]:
    by_chapter: dict[int, list[dict[str, object]]] = {}
    for item in relationship_history:
        if not isinstance(item, dict):
            continue
        row_chapter_index = _safe_int(item.get("chapter_index"), default=None)
        if row_chapter_index is None:
            continue
        by_chapter.setdefault(row_chapter_index, []).append(item)

    displacement_by_chapter = _displacement_metrics_by_chapter(
        relationship_displacements,
        default_chapter_index=chapter_index,
    )

    timeline: list[dict[str, object]] = []
    all_chapters = sorted(set(by_chapter) | set(displacement_by_chapter))
    for row_chapter_index in all_chapters:
        rows = by_chapter.get(row_chapter_index, [])
        displacement_metrics = displacement_by_chapter.get(row_chapter_index, {})
        displacement_count = _safe_int(displacement_metrics.get("count"), default=0) or 0
        peak_delta_tension = round(
            _safe_float(displacement_metrics.get("peak_abs_delta"), default=0.0),
            4,
        )
        if rows:
            average_tension = round(
                sum(_safe_float(row.get("tension_score"), default=0.0) for row in rows) / len(rows),
                4,
            )
            dominant_gap = _dominant_gap_from_rows(rows)
            sample_count = len(rows)
        else:
            current_tension_sum = _safe_float(displacement_metrics.get("current_tension_sum"), default=0.0)
            current_tension_count = _safe_int(displacement_metrics.get("current_tension_count"), default=0) or 0
            average_tension = round(
                current_tension_sum / current_tension_count,
                4,
            ) if current_tension_count > 0 else 0.0
            dominant_gap = _dominant_gap_from_counts(
                displacement_metrics.get("dominant_gap_counts"),
            )
            sample_count = 0
        timeline.append(
            {
                "chapter_index": row_chapter_index,
                "average_tension": average_tension,
                "dominant_gap": dominant_gap,
                "sample_count": sample_count,
                "displacement_count": displacement_count,
                "peak_delta_tension": peak_delta_tension,
            }
        )

    if len(timeline) <= limit:
        return timeline
    return timeline[-limit:]


def _build_candidate_timeline(
    feedback_history: list[dict[str, object]],
    *,
    fallback_chapter_index: int | None,
    limit: int,
) -> list[dict[str, object]]:
    by_chapter: dict[int, list[dict[str, object]]] = {}
    for item in feedback_history:
        if not isinstance(item, dict):
            continue
        row_chapter_index = _safe_int(item.get("chapter_index"), default=fallback_chapter_index)
        if row_chapter_index is None:
            continue
        by_chapter.setdefault(row_chapter_index, []).append(item)

    timeline: list[dict[str, object]] = []
    for row_chapter_index in sorted(by_chapter):
        rows = by_chapter[row_chapter_index]
        if not rows:
            continue
        sample_count = len(rows)
        accept_count = sum(1 for row in rows if bool(row.get("accepted", False)))
        feedback_signal = round(sum(_feedback_signal(row) for row in rows) / sample_count, 4)
        timeline.append(
            {
                "chapter_index": row_chapter_index,
                "feedback_signal": feedback_signal,
                "accept_rate": round(accept_count / sample_count, 4),
                "sample_count": sample_count,
            }
        )

    if len(timeline) <= limit:
        return timeline
    return timeline[-limit:]


def _build_candidate_fallback_timeline(
    selected_candidate: object,
    *,
    chapter_index: int | None,
) -> list[dict[str, object]]:
    if not isinstance(selected_candidate, dict):
        return []
    row_chapter_index = chapter_index if chapter_index is not None else 0
    retention_score = _safe_float(selected_candidate.get("retention_score"), default=0.0)
    tension_score = _safe_float(selected_candidate.get("tension_score"), default=0.0)
    feedback_signal = round(retention_score - tension_score * 0.5, 4)
    accept_rate = max(0.0, min(1.0, round(0.5 + feedback_signal * 0.5, 4)))
    return [
        {
            "chapter_index": row_chapter_index,
            "feedback_signal": feedback_signal,
            "accept_rate": accept_rate,
            "sample_count": 1,
        }
    ]


def _dominant_gap_from_rows(rows: list[dict[str, object]]) -> str:
    gap_counts: dict[str, int] = {}
    for row in rows:
        gap = str(row.get("dominant_gap", "status"))
        gap_counts[gap] = gap_counts.get(gap, 0) + 1
    if not gap_counts:
        return "status"
    return max(gap_counts.items(), key=lambda item: item[1])[0]


def _build_graph_fallback_timeline(
    relationship_graph: object,
    *,
    chapter_index: int | None,
    relationship_displacements: object,
) -> list[dict[str, object]]:
    if not isinstance(relationship_graph, dict):
        return []
    edges = relationship_graph.get("high_tension_edges", [])
    if not isinstance(edges, list) or not edges:
        return []
    if chapter_index is None:
        chapter_index = 0
    displacement_by_chapter = _displacement_metrics_by_chapter(
        relationship_displacements,
        default_chapter_index=chapter_index,
    )
    displacement_metrics = displacement_by_chapter.get(chapter_index, {})
    graph_displacement_count = _safe_int(relationship_graph.get("displacement_count"), default=0) or 0
    average_tension = round(
        sum(_safe_float(item.get("tension_score"), default=0.0) for item in edges if isinstance(item, dict))
        / max(1, len(edges)),
        4,
    )
    first_edge = edges[0] if isinstance(edges[0], dict) else {}
    return [
        {
            "chapter_index": chapter_index,
            "average_tension": average_tension,
            "dominant_gap": str(first_edge.get("dominant_gap", "status")),
            "sample_count": len(edges),
            "displacement_count": max(
                graph_displacement_count,
                _safe_int(displacement_metrics.get("count"), default=0) or 0,
            ),
            "peak_delta_tension": round(
                _safe_float(displacement_metrics.get("peak_abs_delta"), default=0.0),
                4,
            ),
        }
    ]


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _displacement_metrics_by_chapter(
    relationship_displacements: object,
    *,
    default_chapter_index: int | None,
) -> dict[int, dict[str, object]]:
    if not isinstance(relationship_displacements, list):
        return {}

    metrics_by_chapter: dict[int, dict[str, object]] = {}
    for item in relationship_displacements:
        if not isinstance(item, dict):
            continue
        row_chapter_index = _safe_int(item.get("chapter_index"), default=default_chapter_index)
        if row_chapter_index is None:
            continue

        metrics = metrics_by_chapter.setdefault(
            row_chapter_index,
            {
                "count": 0,
                "peak_abs_delta": 0.0,
                "current_tension_sum": 0.0,
                "current_tension_count": 0,
                "dominant_gap_counts": {},
            },
        )
        metrics["count"] = (_safe_int(metrics.get("count"), default=0) or 0) + 1

        delta_tension = abs(_safe_float(item.get("delta_tension"), default=0.0))
        previous_peak = _safe_float(metrics.get("peak_abs_delta"), default=0.0)
        if delta_tension > previous_peak:
            metrics["peak_abs_delta"] = delta_tension

        current_tension = _safe_float(item.get("current_tension"), default=0.0)
        metrics["current_tension_sum"] = _safe_float(metrics.get("current_tension_sum"), default=0.0) + current_tension
        metrics["current_tension_count"] = (
            _safe_int(metrics.get("current_tension_count"), default=0) or 0
        ) + 1

        dominant_gap = str(
            item.get("current_dominant_gap")
            or item.get("previous_dominant_gap")
            or "status"
        )
        gap_counts = metrics.get("dominant_gap_counts")
        if isinstance(gap_counts, dict):
            gap_counts[dominant_gap] = int(gap_counts.get(dominant_gap, 0)) + 1

    return metrics_by_chapter


def _dominant_gap_from_counts(gap_counts: object) -> str:
    if not isinstance(gap_counts, dict) or not gap_counts:
        return "status"
    normalized_counts = {
        str(key): _safe_int(value, default=0) or 0
        for key, value in gap_counts.items()
    }
    return max(normalized_counts.items(), key=lambda item: item[1])[0]


def _v2_state_to_v4_context(
    state: dict[str, object],
    *,
    context_id: str,
    raw_context: dict[str, object],
) -> dict[str, object]:
    mainline = _bounded_float(state.get("mainline_progress"), 0.5)
    sideplot = _bounded_float(state.get("sideplot_progress"), 0.4)
    conflict = _bounded_float(state.get("conflict_intensity"), 0.5)
    emotion = _bounded_float(state.get("emotional_temperature"), 0.5)
    pacing = _bounded_float(state.get("pacing_speed"), 0.5)
    foreshadow = _bounded_float(state.get("foreshadowing_load"), 0.4)
    payoff = _bounded_float(state.get("payoff_pressure"), 0.4)
    chapter_index = _safe_int(state.get("chapter_index"), default=0)
    tags = state.get("tags", [])
    genre = ""
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                genre = tag.strip()
                break

    hero = {
        "id": f"{context_id}-hero",
        "status": _bounded_float(0.2 + mainline * 0.55, 0.5),
        "knowledge": _bounded_float(0.25 + foreshadow * 0.65, 0.5),
        "emotion": emotion,
        "interest_conflict": _bounded_float(0.35 + conflict * 0.5, 0.5),
        "control": _bounded_float(0.28 + mainline * 0.45, 0.5),
        "dependency": _bounded_float(0.58 - sideplot * 0.35, 0.5),
        "trust": _bounded_float(0.62 - conflict * 0.42, 0.5),
        "impulsiveness": _bounded_float(0.22 + emotion * 0.55, 0.5),
        "calmness": _bounded_float(0.72 - emotion * 0.45, 0.5),
        "resilience": _bounded_float(0.45 + mainline * 0.45, 0.5),
        "directness": _bounded_float(0.4 + pacing * 0.45, 0.5),
        "pragmatism": _bounded_float(0.46 + foreshadow * 0.38, 0.5),
        "idealism": _bounded_float(0.64 - foreshadow * 0.45, 0.5),
        "assertiveness": _bounded_float(0.44 + conflict * 0.38, 0.5),
        "avoidance": _bounded_float(0.5 - conflict * 0.25, 0.5),
        "self_protection": _bounded_float(0.46 + payoff * 0.4, 0.5),
        "sacrifice_tendency": _bounded_float(0.62 - payoff * 0.35, 0.5),
        "risk_appetite": _bounded_float(0.34 + conflict * 0.42, 0.5),
    }
    rival = {
        "id": f"{context_id}-rival",
        "status": _bounded_float(0.82 - mainline * 0.36, 0.5),
        "knowledge": _bounded_float(0.72 - foreshadow * 0.32, 0.5),
        "emotion": _bounded_float(0.88 - emotion * 0.55, 0.5),
        "interest_conflict": _bounded_float(0.42 + conflict * 0.52, 0.5),
        "control": _bounded_float(0.58 + mainline * 0.26, 0.5),
        "dependency": _bounded_float(0.42 - sideplot * 0.22, 0.5),
        "trust": _bounded_float(0.42 - conflict * 0.35, 0.5),
        "impulsiveness": _bounded_float(0.66 - emotion * 0.35, 0.5),
        "calmness": _bounded_float(0.34 + emotion * 0.42, 0.5),
        "resilience": _bounded_float(0.35 + mainline * 0.36, 0.5),
        "directness": _bounded_float(0.36 + pacing * 0.4, 0.5),
        "pragmatism": _bounded_float(0.58 + foreshadow * 0.3, 0.5),
        "idealism": _bounded_float(0.48 - foreshadow * 0.25, 0.5),
        "assertiveness": _bounded_float(0.52 + conflict * 0.34, 0.5),
        "avoidance": _bounded_float(0.46 - conflict * 0.21, 0.5),
        "self_protection": _bounded_float(0.56 + payoff * 0.28, 0.5),
        "sacrifice_tendency": _bounded_float(0.46 - payoff * 0.22, 0.5),
        "risk_appetite": _bounded_float(0.36 + conflict * 0.34, 0.5),
    }

    relationship_history = raw_context.get("relationship_history")
    if not isinstance(relationship_history, list):
        relationship_history = [
            {
                "source_character": hero["id"],
                "target_character": rival["id"],
                "tension_score": _bounded_float(conflict - 0.14, 0.35),
                "dominant_gap": "emotion" if emotion >= conflict else "status",
                "chapter_index": max(0, chapter_index - 1),
            }
        ]
    v3_feedback_history = raw_context.get("v3_feedback_history")
    if not isinstance(v3_feedback_history, list):
        v3_feedback_history = [
            {
                "accepted": payoff >= 0.45,
                "retention_delta": round(payoff - 0.5, 4),
                "abandonment_delta": round(max(0.0, 0.5 - payoff), 4),
                "chapter_index": chapter_index,
            }
        ]

    return {
        "v4_enabled": True,
        "chapter_index": chapter_index,
        "genre": genre,
        "genre_profile": {"genre": genre} if genre else {},
        "characters": [hero, rival],
        "relationship_history": relationship_history,
        "pressure_items": [
            {"type": "survival", "intensity": conflict},
            {"type": "relationship_break", "intensity": payoff},
            {"type": "time_limit", "intensity": pacing},
            {"type": "humiliation", "intensity": emotion},
        ],
        "v3_feedback_history": v3_feedback_history,
        "v3_retention_context": {
            "retention_weight": _bounded_float(0.56 + payoff * 0.34, 0.7),
            "tension_weight": _bounded_float(0.22 + conflict * 0.42, 0.3),
            "template_penalty": _bounded_float(0.06 + foreshadow * 0.16, 0.08),
        },
    }


def _workbench_candidate_view(candidate: object) -> dict[str, object] | None:
    if not isinstance(candidate, dict):
        return None

    return {
        "candidate_id": str(candidate.get("candidate_id", "")),
        "predicted_action": str(candidate.get("predicted_action", "")),
        "predicted_turning_point": str(candidate.get("predicted_turning_point", "")),
        "predicted_conflict_type": str(candidate.get("predicted_conflict_type", "")),
        "predicted_payoff_type": str(candidate.get("predicted_payoff_type", "")),
        "retention_score": _bounded_float(candidate.get("retention_score"), 0.0),
        "tension_score": _bounded_float(candidate.get("tension_score"), 0.0),
        "explanation": str(candidate.get("explanation", "")),
        "risk_flags": list(candidate.get("risk_flags", []))
        if isinstance(candidate.get("risk_flags"), list)
        else [],
    }
