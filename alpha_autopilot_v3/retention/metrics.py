from __future__ import annotations

from typing import Any

from ..decomposition.models import ChapterDecompositionRecord
from .models import RetentionMetrics


def _clip(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _checkpoint_status(checkpoints: dict[str, Any], name: str) -> str:
    checkpoint = checkpoints.get(name)
    return str(getattr(checkpoint, "status", "unknown")).strip().lower() or "unknown"


def build_retention_metrics(record: ChapterDecompositionRecord) -> RetentionMetrics:
    structure = record.structure
    style = record.style_dna
    checkpoints = {item.name: item for item in record.checkpoints}

    conflict_progression_status = _checkpoint_status(checkpoints, "conflict-progression")
    read_through_drive_status = _checkpoint_status(checkpoints, "read-through-drive")
    continuity_stability_status = _checkpoint_status(checkpoints, "continuity-stability")

    conflict_progression = 1.0 if conflict_progression_status == "pass" else 0.55
    read_through_drive = 1.0 if read_through_drive_status == "pass" else 0.5
    continuity_stability = 1.0 if continuity_stability_status == "pass" else 0.0

    hook_strength = 0.75 if structure.get("ending_hook") else 0.35
    suspense_drive = 0.82 if record.primary_function in {"information-reveal", "conflict-escalation"} else 0.46
    emotional_drive = 0.78 if style.get("emotional_directness") == "explicit" else 0.52
    pacing_drive = 0.7 if style.get("pace") == "brisk" else 0.5
    template_risk = 0.24 if structure.get("opening_hook") and structure.get("ending_hook") else 0.42

    chapter_attraction_score = _clip(
        0.2 * read_through_drive
        + 0.18 * conflict_progression
        + 0.16 * hook_strength
        + 0.14 * suspense_drive
        + 0.14 * emotional_drive
        + 0.12 * pacing_drive
        + 0.06 * continuity_stability
        - 0.08 * template_risk
    )

    continue_reading_intent = _clip(
        0.55 * chapter_attraction_score + 0.2 * hook_strength + 0.15 * suspense_drive + 0.1 * pacing_drive
    )

    return RetentionMetrics(
        chapter_attraction_score=chapter_attraction_score,
        continue_reading_intent=continue_reading_intent,
        emotional_drive=_clip(emotional_drive),
        pacing_drive=_clip(pacing_drive),
        suspense_drive=_clip(suspense_drive),
        conflict_drive=_clip(conflict_progression),
        hook_strength=_clip(hook_strength),
        template_risk=_clip(template_risk),
        evidence={
            "conflict_progression": conflict_progression_status,
            "read_through_drive": read_through_drive_status,
            "continuity_stability": continuity_stability_status,
            "primary_function": record.primary_function,
            "structure": structure,
            "style_dna": style,
        },
    )
