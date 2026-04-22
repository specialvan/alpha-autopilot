from __future__ import annotations

import json
from pathlib import Path


def _slug_to_title(raw: str) -> str:
    return raw.replace("_", " ").strip()


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


def build_workbench_contexts_from_plotpilot_report(payload: dict[str, object]) -> list[dict[str, object]]:
    results = payload.get("results")
    if not isinstance(results, list):
        return []

    chapter_numbers = [
        int(item.get("chapter", index + 1))
        for index, item in enumerate(results)
        if isinstance(item, dict)
    ]
    total = max(chapter_numbers, default=len(results))
    model = str(payload.get("model", "unknown-model"))
    contexts: list[dict[str, object]] = []

    for item in results:
        if not isinstance(item, dict):
            continue
        if item.get("success") is False:
            continue

        chapter_number = int(item.get("chapter", len(contexts) + 1))
        title = _slug_to_title(str(item.get("title", f"chapter_{chapter_number:02d}")))
        chars = int(item.get("chars", 0))
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

    return contexts


def load_imported_workbench_contexts(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("contexts"), list):
        return payload
    return None
