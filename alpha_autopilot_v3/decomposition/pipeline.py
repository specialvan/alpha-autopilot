from __future__ import annotations

from typing import Any

from ..generation_control.policy import build_generation_control_plan
from ..retention.metrics import build_retention_metrics
from ..retention.models import RetentionDesireVector
from .models import ChapterDecompositionRecord, CheckpointResult, EvidenceSpan


def _split_paragraphs(text: str) -> list[str]:
    return [item.strip() for item in text.split("\n\n") if item.strip()]


def _infer_primary_function(paragraphs: list[str]) -> str:
    joined = " ".join(paragraphs)
    lowered = joined.lower()
    if any(token in lowered for token in ("payoff", "reveal", "truth", "unmask")) or any(
        token in joined for token in ("兑现", "回收", "真相", "揭开")
    ):
        return "payoff-delivery"
    if any(
        token in lowered
        for token in ("appear", "stronger enemy", "threat", "smash", "flip the table", "conflict")
    ) or any(token in joined for token in ("出现", "更强的敌人", "威胁", "砸碎", "掀桌", "冲突", "堵门")):
        return "conflict-escalation"
    if any(token in lowered for token in ("clue", "discover", "learn", "found")) or any(
        token in joined for token in ("线索", "发现", "知道", "得知")
    ):
        return "information-reveal"
    return "transition-breathing"


def _build_style_dna(paragraphs: list[str]) -> dict[str, str]:
    joined = " ".join(paragraphs)
    lowered = joined.lower()
    dialogue_marks = joined.count('"') + joined.count("'") + joined.count("“") + joined.count("”")
    emotional_directness = (
        "explicit"
        if any(token in lowered for token in ("anger", "hate", "pain", "shock"))
        or any(token in joined for token in ("怒", "恨", "痛", "惊", "怕"))
        else "balanced"
    )
    return {
        "pace": "brisk" if len(paragraphs) <= 4 else "measured",
        "dialogue_reliance": "medium" if dialogue_marks else "low",
        "emotional_directness": emotional_directness,
    }


def _build_checkpoints(primary_function: str, paragraphs: list[str]) -> list[CheckpointResult]:
    has_opening = bool(paragraphs)
    has_escalation = len(paragraphs) >= 2
    has_ending_hook = len(paragraphs) >= 4

    return [
        CheckpointResult(
            name="chapter-function-fit",
            status=(
                "pass"
                if primary_function in {
                    "conflict-escalation",
                    "payoff-delivery",
                    "information-reveal",
                    "transition-breathing",
                }
                else "mixed"
            ),
            evidence=f"Primary function resolved to {primary_function}.",
            implication="Function label is stable enough for downstream use.",
        ),
        CheckpointResult(
            name="conflict-progression",
            status="pass" if has_escalation else "mixed",
            evidence="Escalation paragraphs detected." if has_escalation else "No escalation beat detected.",
            implication="Conflict signal is strong." if has_escalation else "Record may require manual review.",
        ),
        CheckpointResult(
            name="read-through-drive",
            status="pass" if has_ending_hook else "mixed",
            evidence="Final paragraph introduces a future threat." if has_ending_hook else "Ending hook is weak.",
            implication="Reader pursuit pressure exists." if has_ending_hook else "May require manual review.",
        ),
        CheckpointResult(
            name="continuity-stability",
            status="pass" if has_opening else "fail",
            evidence="Chapter identity and opening beat detected." if has_opening else "No usable chapter start.",
            implication="Context can be projected safely." if has_opening else "Reject from training pool.",
        ),
    ]


def _admission_for_checkpoints(checkpoints: list[CheckpointResult]) -> str:
    statuses = {item.status for item in checkpoints}
    if "fail" in statuses:
        return "rejected"
    if "mixed" in statuses:
        return "provisional"
    return "approved"


def decompose_chapter_text(
    *,
    chapter_number: int,
    title: str,
    text: str,
    genre: str,
    stage: str,
    retention_desire_vector: RetentionDesireVector | None = None,
    macro_structure: str | None = None,
) -> ChapterDecompositionRecord:
    paragraphs = _split_paragraphs(text)
    primary_function = _infer_primary_function(paragraphs)
    checkpoints = _build_checkpoints(primary_function, paragraphs)
    admission = _admission_for_checkpoints(checkpoints)
    conflict_intensity = min(1.0, round(0.38 + len(paragraphs) * 0.08, 4))
    payoff_pressure = min(1.0, round(0.16 + max(len(paragraphs) - 1, 0) * 0.05, 4))
    retention_rough_signal = min(1.0, round(0.4 + conflict_intensity * 0.25 + payoff_pressure * 0.18, 4))

    record = ChapterDecompositionRecord(
        chapter_number=chapter_number,
        title=title,
        scope="single",
        genre=genre,
        stage=stage,
        stage_inferred=False,
        primary_function=primary_function,
        secondary_functions=[],
        structure={
            "goal": paragraphs[1] if len(paragraphs) > 1 else paragraphs[0] if paragraphs else "",
            "opening_hook": paragraphs[0] if paragraphs else "",
            "escalations": paragraphs[1:3],
            "reversal_or_reveal": paragraphs[2] if len(paragraphs) > 2 else "",
            "payoff": paragraphs[-2] if len(paragraphs) > 1 else "",
            "ending_hook": paragraphs[-1] if paragraphs else "",
        },
        style_dna=_build_style_dna(paragraphs),
        evidence_spans=[
            EvidenceSpan(
                label="opening_hook",
                text=paragraphs[0],
                paragraph_index=0,
                confidence="direct",
            )
        ]
        if paragraphs
        else [],
        checkpoints=checkpoints,
        admission=admission,
        workbench_context={
            "recommended_stage": stage,
            "narrative_signals": {
                "conflict_intensity": conflict_intensity,
                "payoff_pressure": payoff_pressure,
            },
            "notes": f"Derived from {len(paragraphs)} paragraphs with {primary_function}.",
        },
        retention_signal=retention_rough_signal,
    )

    retention_metrics = build_retention_metrics(record)
    control_plan = build_generation_control_plan(
        record,
        desire_vector=retention_desire_vector,
        macro_structure=macro_structure,
    )

    record.attraction_score = retention_metrics.chapter_attraction_score
    record.hook_strength = retention_metrics.hook_strength
    record.pace_pressure = retention_metrics.pacing_drive
    record.emotion_curve = control_plan.emotional_curve
    record.decision_tags = control_plan.decision_tags
    record.control_suggestions = control_plan.suggestions
    record.workbench_context = {
        **record.workbench_context,
        "retention": {
            "target_function": control_plan.target_function.name,
            "primary_objective": control_plan.target_function.primary_objective,
            "chapter_attraction_score": retention_metrics.chapter_attraction_score,
            "continue_reading_intent": retention_metrics.continue_reading_intent,
            "template_risk": retention_metrics.template_risk,
        },
        "control_plan": {
            "focus_mode": control_plan.focus_mode,
            "emotion_curve": control_plan.emotional_curve,
            "pacing_curve": control_plan.pacing_curve,
            "suspense_curve": control_plan.suspense_curve,
            "conflict_curve": control_plan.conflict_curve,
            "hook_strategy": control_plan.hook_strategy,
            "anti_pattern_warnings": control_plan.anti_pattern_warnings,
        },
    }

    return record


def build_records_from_plotpilot_report(
    payload: dict[str, Any],
    *,
    genre: str,
) -> list[ChapterDecompositionRecord]:
    results = payload.get("results")
    if not isinstance(results, list):
        return []

    chapter_numbers = [
        int(item.get("chapter", index + 1))
        for index, item in enumerate(results)
        if isinstance(item, dict) and item.get("success") is not False
    ]
    max_chapter = max(chapter_numbers, default=1)
    records: list[ChapterDecompositionRecord] = []

    for item in results:
        if not isinstance(item, dict):
            continue
        if item.get("success") is False:
            continue

        chapter_number = int(item.get("chapter", len(records) + 1))
        title = str(item.get("title", f"chapter_{chapter_number:02d}")).replace("_", " ")
        preview = str(item.get("preview", "")).strip()
        ratio = chapter_number / max_chapter if max_chapter else 1.0
        if max_chapter == 1 or ratio <= 0.3:
            stage = "opening"
        elif ratio < 0.6:
            stage = "middle"
        elif ratio <= 0.85:
            stage = "mid_late"
        else:
            stage = "late"

        records.append(
            decompose_chapter_text(
                chapter_number=chapter_number,
                title=title,
                text=preview,
                genre=genre,
                stage=stage,
            )
        )

    return records
