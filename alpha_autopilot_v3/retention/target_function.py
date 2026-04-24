from __future__ import annotations

from .models import RetentionTargetFunction


DEFAULT_PRIORITY_ORDER = [
    "continue-reading-intent",
    "chapter-attraction",
    "emotional-drive",
    "pacing-drive",
    "suspense-drive",
    "conflict-drive",
    "hook-strength",
]

DEFAULT_GUARDRAILS = [
    "preserve-structure-constraints",
    "preserve-style-consistency",
    "preserve-fact-and-worldstate-constraints",
    "avoid-template-overfit",
]


def build_retention_target_function() -> RetentionTargetFunction:
    return RetentionTargetFunction(
        name="reader-retention",
        primary_objective="maximize-reader-continue-reading-intent",
        priority_order=list(DEFAULT_PRIORITY_ORDER),
        guardrails=list(DEFAULT_GUARDRAILS),
        description=(
            "Append a reader-retention objective on top of the existing structure-first system, "
            "so emotional drive, pacing, suspense, conflict, and hook decisions influence generation."
        ),
    )
