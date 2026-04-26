from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from .report_arbitration import resolve_plotpilot_report_candidate

NUMERIC_STATE_FIELDS = (
    "mainline_progress",
    "sideplot_progress",
    "conflict_intensity",
    "emotional_temperature",
    "pacing_speed",
    "foreshadowing_load",
    "payoff_pressure",
)


def _slug_to_title(raw: str) -> str:
    return raw.replace("_", " ").strip()


def _normalize_title(raw: object) -> str:
    return " ".join(str(raw).replace("_", " ").lower().split())


def _coerce_chapter_number(raw: object) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _stage_for_position(chapter_number: int, total: int) -> str:
    if total <= 1:
        return "middle"

    ratio = chapter_number / total
    if ratio <= 0.3:
        return "opening"
    if ratio < 0.6:
        return "middle"
    if ratio <= 0.85:
        return "mid_late"
    return "late"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _state_from_position(chapter_number: int, total: int, chars: int) -> dict[str, object]:
    ratio = chapter_number / max(total, 1)
    stage = _stage_for_position(chapter_number, total)
    char_signal = min(chars / 5000.0, 1.0)
    return {
        "chapter_index": chapter_number,
        "stage": stage,
        "mainline_progress": _clamp01(ratio * 0.95),
        "sideplot_progress": _clamp01(0.18 + ratio * 0.42),
        "conflict_intensity": _clamp01(0.48 + char_signal * 0.28),
        "emotional_temperature": _clamp01(0.44 + char_signal * 0.2),
        "pacing_speed": _clamp01(0.42 + char_signal * 0.22),
        "foreshadowing_load": _clamp01(0.2 + ratio * 0.38),
        "payoff_pressure": _clamp01(0.14 + ratio * 0.66),
        "characters": {},
        "tags": ["plotpilot_import", stage],
    }


def _load_quality_records_from_json(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _load_quality_records_from_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    records: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _record_identity(record: dict[str, object]) -> tuple[int | None, str]:
    return (
        _coerce_chapter_number(record.get("chapter_number")),
        _normalize_title(record.get("title", "")),
    )


def _merge_quality_records(
    base_records: list[dict[str, object]],
    override_records: list[dict[str, object]],
) -> list[dict[str, object]]:
    merged: dict[tuple[int | None, str], dict[str, object]] = {}
    ordered_keys: list[tuple[int | None, str]] = []

    for batch in (base_records, override_records):
        for record in batch:
            key = _record_identity(record)
            existing = merged.get(key)
            if existing is None:
                merged[key] = deepcopy(record)
                ordered_keys.append(key)
                continue

            combined = dict(existing)
            for field, value in record.items():
                if (
                    field == "workbench_context"
                    and isinstance(existing.get(field), dict)
                    and isinstance(value, dict)
                ):
                    combined[field] = {**existing[field], **value}
                else:
                    combined[field] = value
            merged[key] = combined

    return [merged[key] for key in ordered_keys]


def _load_quality_records_for_contexts(path: Path) -> list[dict[str, object]]:
    return load_quality_records_for_plotpilot_bundle(path.parent)


def load_quality_records_for_plotpilot_bundle(bundle_root: Path) -> list[dict[str, object]]:
    quality_dir = bundle_root / "v3_records"
    projection_records = _load_quality_records_from_json(quality_dir / "matrix_projection.json")
    reverse_outline_records = _load_quality_records_from_jsonl(
        quality_dir / "reverse_outline_records.jsonl"
    )
    return _merge_quality_records(projection_records, reverse_outline_records)


def _build_checkpoint_summary(checkpoints: object) -> str | None:
    if not isinstance(checkpoints, list):
        return None

    parts: list[str] = []
    for checkpoint in checkpoints:
        if not isinstance(checkpoint, dict):
            continue
        name = str(checkpoint.get("name", "")).strip()
        status = str(checkpoint.get("status", "")).strip()
        implication = str(checkpoint.get("implication", "")).strip()
        if not any((name, status, implication)):
            continue
        parts.append(" ".join(part for part in (name, status, implication) if part))
    return "; ".join(parts) or None


def _quality_notes_from_record(record: dict[str, object]) -> str | None:
    explicit_notes = record.get("quality_notes")
    if isinstance(explicit_notes, str) and explicit_notes.strip():
        return explicit_notes.strip()

    workbench_context = record.get("workbench_context")
    if isinstance(workbench_context, dict):
        notes = workbench_context.get("notes")
        if isinstance(notes, str) and notes.strip():
            return notes.strip()

    return _build_checkpoint_summary(record.get("checkpoints"))


def _quality_enrichment_from_record(record: dict[str, object]) -> dict[str, object]:
    enrichment: dict[str, object] = {}

    for field in ("admission", "primary_function"):
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            enrichment[field] = value.strip()

    style_dna = record.get("style_dna")
    if isinstance(style_dna, dict):
        enrichment["style_dna"] = deepcopy(style_dna)

    checkpoints = record.get("checkpoints")
    if isinstance(checkpoints, list):
        enrichment["checkpoints"] = deepcopy(checkpoints)

    quality_notes = _quality_notes_from_record(record)
    if quality_notes:
        enrichment["quality_notes"] = quality_notes

    return enrichment


def _match_quality_record(
    context: dict[str, object],
    by_chapter: dict[int, dict[str, object]],
    by_title: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    chapter_number = _coerce_chapter_number(context.get("chapterNumber"))
    if chapter_number is not None and chapter_number in by_chapter:
        return by_chapter[chapter_number]

    title = _normalize_title(context.get("title", ""))
    if title and title in by_title:
        return by_title[title]

    return None


def enrich_workbench_contexts_with_quality(
    contexts: list[dict[str, object]],
    quality_records: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    if not quality_records:
        return [deepcopy(context) for context in contexts]

    by_chapter = {
        chapter_number: record
        for record in quality_records
        if (chapter_number := _coerce_chapter_number(record.get("chapter_number"))) is not None
    }
    by_title = {
        normalized_title: record
        for record in quality_records
        if (normalized_title := _normalize_title(record.get("title", "")))
    }

    enriched_contexts: list[dict[str, object]] = []
    for context in contexts:
        enriched_context = deepcopy(context)
        record = _match_quality_record(enriched_context, by_chapter, by_title)
        if record is not None:
            enriched_context.update(_quality_enrichment_from_record(record))
        enriched_contexts.append(enriched_context)
    return enriched_contexts


def build_workbench_contexts_from_plotpilot_report(
    payload: dict[str, object],
    quality_records: list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    results = payload.get("results")
    if not isinstance(results, list):
        return []

    chapter_numbers = [
        chapter_number
        for index, item in enumerate(results)
        if isinstance(item, dict)
        if (chapter_number := _coerce_chapter_number(item.get("chapter", index + 1))) is not None
    ]
    total = max(chapter_numbers, default=len(results))
    model = str(payload.get("model", "unknown-model"))
    contexts: list[dict[str, object]] = []

    for item in results:
        if not isinstance(item, dict):
            continue
        if item.get("success") is False:
            continue

        chapter_number = _coerce_chapter_number(item.get("chapter", len(contexts) + 1)) or (len(contexts) + 1)
        title = _slug_to_title(str(item.get("title", f"chapter_{chapter_number:02d}")))
        chars = _coerce_chapter_number(item.get("chars", 0)) or 0
        preview = str(item.get("preview", "")).strip()
        summary = f"PlotPilot {model} fixture | {preview[:160]}".strip()
        contexts.append(
            {
                "id": f"plotpilot-chapter-{chapter_number:02d}",
                "chapterNumber": chapter_number,
                "title": title,
                "stage": _stage_for_position(chapter_number, total),
                "summary": summary,
                "state": _state_from_position(chapter_number, total, chars),
            }
        )

    return _attach_compare_baseline(
        enrich_workbench_contexts_with_quality(contexts, quality_records)
    )


def _safe_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return None


def _state_delta(
    baseline_state: dict[str, object],
    current_state: dict[str, object],
) -> dict[str, float]:
    delta: dict[str, float] = {}
    for field in NUMERIC_STATE_FIELDS:
        baseline_value = _safe_float(baseline_state.get(field))
        current_value = _safe_float(current_state.get(field))
        if baseline_value is None or current_value is None:
            continue
        delta[field] = round(current_value - baseline_value, 4)
    return delta


def _attach_compare_baseline(contexts: list[dict[str, object]]) -> list[dict[str, object]]:
    if not contexts:
        return []

    enriched = [deepcopy(context) for context in contexts]
    previous_context: dict[str, object] | None = None
    for context in enriched:
        state = context.get("state")
        if not isinstance(state, dict):
            previous_context = context
            continue
        if previous_context is None:
            previous_context = context
            continue

        baseline_state = previous_context.get("state")
        if not isinstance(baseline_state, dict):
            previous_context = context
            continue

        context["compare_baseline"] = {
            "baseline_context_id": previous_context.get("id"),
            "baseline_chapter_number": previous_context.get("chapterNumber"),
            "delta": _state_delta(baseline_state, state),
        }
        previous_context = context

    return enriched


def load_workbench_contexts_from_plotpilot_report(
    report_path: Path,
    *,
    quality_records: list[dict[str, object]] | None = None,
) -> dict[str, object] | None:
    if not report_path.exists():
        return None

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None

    contexts = build_workbench_contexts_from_plotpilot_report(
        payload,
        quality_records=quality_records,
    )
    if not contexts:
        return None

    return {
        "contexts": contexts,
        "source": "plotpilot_report",
        "context_contract": "real_chapter_context_v1",
        "report_path": str(report_path),
    }


def load_latest_plotpilot_report_contexts(
    report_root: Path,
    *,
    quality_records: list[dict[str, object]] | None = None,
    manifest_root: Path | None = None,
    preferred_model: str | None = None,
) -> dict[str, object] | None:
    candidate = resolve_plotpilot_report_candidate(
        report_root,
        manifest_root=manifest_root,
        preferred_model=preferred_model,
    )
    if candidate is None:
        return None

    loaded = load_workbench_contexts_from_plotpilot_report(
        candidate.report_path,
        quality_records=quality_records,
    )
    if loaded is None:
        return None
    payload = dict(loaded)
    payload["context_contract"] = "real_chapter_context_v2"
    payload["run_id"] = candidate.run_id
    payload["manifest_path"] = str(candidate.manifest_path) if candidate.manifest_path else None
    payload["preferred_model"] = preferred_model
    payload["resolved_model"] = candidate.model
    payload["report_success_rate"] = candidate.success_rate
    payload["report_timestamp"] = candidate.timestamp
    payload["arbitration_strategy"] = "manifest-model-success-rate-v1"
    payload["source_diagnostics"] = {
        "local_report": {
            "status": "ok",
            "report_path": str(candidate.report_path),
            "run_id": candidate.run_id,
            "manifest_path": (
                str(candidate.manifest_path)
                if candidate.manifest_path is not None
                else None
            ),
            "preferred_model": preferred_model,
            "resolved_model": candidate.model,
            "report_success_rate": candidate.success_rate,
            "arbitration_strategy": "manifest-model-success-rate-v1",
        }
    }
    return payload


def load_imported_workbench_contexts(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if isinstance(payload, dict) and isinstance(payload.get("contexts"), list):
        contexts = [item for item in payload["contexts"] if isinstance(item, dict)]
        if not contexts:
            return None
        enriched_payload = dict(payload)
        enriched_payload["contexts"] = contexts
        try:
            enriched_payload["contexts"] = enrich_workbench_contexts_with_quality(
                contexts,
                _load_quality_records_for_contexts(path),
            )
            enriched_payload["contexts"] = _attach_compare_baseline(enriched_payload["contexts"])
        except Exception:
            # Quality enrichment must never break context loading.
            enriched_payload["contexts"] = contexts
        return enriched_payload
    return None
