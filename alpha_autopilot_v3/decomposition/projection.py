from __future__ import annotations

from .models import ChapterDecompositionRecord


def project_record_for_matrix(record: ChapterDecompositionRecord) -> dict[str, object]:
    return {
        "chapter_number": record.chapter_number,
        "title": record.title,
        "genre": record.genre,
        "primary_function": record.primary_function,
        "style_dna": record.style_dna,
        "admission": record.admission,
        "recommended_stage": record.workbench_context.get("recommended_stage", record.stage),
        "narrative_signals": record.workbench_context.get("narrative_signals", {}),
    }
