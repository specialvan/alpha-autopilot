from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from alpha_autopilot import StoryState, TrainingSample


_KNOWN_STAGES = {"opening", "middle", "mid_late", "late"}
_ACTION_BY_FUNCTION = {
    "conflict-escalation": "push_conflict",
    "payoff-delivery": "deliver_payoff",
    "information-reveal": "plant_foreshadow",
    "transition-breathing": "stabilize_continuity",
}


def default_projection_paths(artifacts_dir: Path) -> list[Path]:
    return [
        artifacts_dir / "v3" / "matrix_projection.json",
        artifacts_dir / "v3_records" / "matrix_projection.json",
        artifacts_dir / "testing" / "plotpilot" / "v3_records" / "matrix_projection.json",
    ]


def load_matrix_projection(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], Path | None]:
    for path in paths:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, list):
            continue
        records = [item for item in payload if isinstance(item, dict)]
        return records, path
    return [], None


def build_training_samples_from_projection(records: Iterable[dict[str, Any]]) -> list[TrainingSample]:
    rows = [row for row in records if isinstance(row, dict)]
    if not rows:
        return []

    max_chapter = max(_to_int(item.get("chapter_number"), index + 1) for index, item in enumerate(rows))
    samples: list[TrainingSample] = []
    for index, item in enumerate(rows):
        chapter_number = _to_int(item.get("chapter_number"), index + 1)
        ratio = chapter_number / max(max_chapter, 1)
        stage = _normalize_stage(item.get("recommended_stage"))
        action = _action_for_function(str(item.get("primary_function", "")).strip().lower())
        admission = str(item.get("admission", "provisional")).strip().lower()
        signals = item.get("narrative_signals", {})
        if not isinstance(signals, dict):
            signals = {}
        style_dna = item.get("style_dna", {})
        if not isinstance(style_dna, dict):
            style_dna = {}
        tags = [str(item.get("genre", "power")).strip().lower(), stage, "v3_projection", f"admission:{admission}"]

        state = StoryState(
            chapter_index=chapter_number,
            stage=stage,
            mainline_progress=_clamp01(ratio * 0.96),
            sideplot_progress=_clamp01(0.15 + ratio * 0.42),
            conflict_intensity=_clamp01(
                _to_float(signals.get("conflict_intensity"), _default_conflict_for_action(action))
            ),
            emotional_temperature=_clamp01(_default_emotional_temperature(action, stage)),
            pacing_speed=_clamp01(_pace_from_style(style_dna)),
            foreshadowing_load=_clamp01(_default_foreshadowing_load(action, ratio)),
            payoff_pressure=_clamp01(_to_float(signals.get("payoff_pressure"), 0.16 + ratio * 0.6)),
            tags=tags,
        )
        target_score = _target_score(admission)
        samples.append(
            TrainingSample(
                state=state,
                target_action=action,
                target_score=target_score,
                feedback=_clamp01(target_score - 0.03),
            )
        )
    return samples


def _normalize_stage(raw: object) -> str:
    stage = str(raw or "middle").strip().lower()
    if stage not in _KNOWN_STAGES:
        return "middle"
    return stage


def _action_for_function(primary_function: str) -> str:
    return _ACTION_BY_FUNCTION.get(primary_function, "focus_character")


def _default_conflict_for_action(action: str) -> float:
    if action in {"push_conflict", "deliver_payoff"}:
        return 0.68
    if action == "plant_foreshadow":
        return 0.56
    if action == "stabilize_continuity":
        return 0.48
    return 0.54


def _default_emotional_temperature(action: str, stage: str) -> float:
    base = {"opening": 0.48, "middle": 0.54, "mid_late": 0.59, "late": 0.63}.get(stage, 0.54)
    if action in {"deliver_payoff", "focus_character"}:
        base += 0.05
    return base


def _pace_from_style(style_dna: dict[str, Any]) -> float:
    pace = str(style_dna.get("pace", "")).strip().lower()
    if pace == "brisk":
        return 0.62
    if pace == "measured":
        return 0.47
    return 0.52


def _default_foreshadowing_load(action: str, ratio: float) -> float:
    base = 0.2 + ratio * 0.35
    if action == "plant_foreshadow":
        base += 0.08
    return base


def _target_score(admission: str) -> float:
    if admission == "approved":
        return 0.91
    if admission == "rejected":
        return 0.65
    return 0.82


def _to_int(value: object, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _to_float(value: object, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))
