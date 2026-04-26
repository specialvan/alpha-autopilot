from __future__ import annotations

from .decision_policy import analyze_personality
from .models import PersonalityProfile


def analyze_personalities(
    characters: list[dict[str, object]],
    *,
    genre_profile: dict[str, object] | None = None,
) -> list[PersonalityProfile]:
    return [
        analyze_personality(item, genre_profile=genre_profile)
        for item in characters
        if isinstance(item, dict)
    ]
