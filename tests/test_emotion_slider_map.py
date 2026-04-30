from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.services.narrative_v4.emotion_slider import EmotionSliderMap


def test_emotion_slider_map_supports_round_trip_serialization() -> None:
    model = EmotionSliderMap.model_validate(
        {
            "baseline": {
                "stress_baseline": 2.0,
                "trust_level": -1.0,
                "social_energy": 4.0,
            },
            "scene_overrides": {
                "scene-001": {
                    "stress_baseline": 6.0,
                }
            },
            "mbti": "INTJ",
            "enneagram": 5,
        }
    )

    dumped = model.model_dump(mode="json")
    restored = EmotionSliderMap.model_validate(dumped)
    assert restored.mbti == "INTJ"
    assert restored.enneagram == 5
    assert restored.scene_overrides["scene-001"]["stress_baseline"] == 6.0


def test_emotion_slider_map_falls_back_to_baseline_when_scene_override_missing() -> None:
    model = EmotionSliderMap.model_validate(
        {
            "baseline": {"stress_baseline": 3.5, "trust_level": -2.0},
            "scene_overrides": {},
        }
    )

    merged = model.merged_for_scene("unknown-scene")
    assert merged["stress_baseline"] == 3.5
    assert merged["trust_level"] == -2.0


def test_emotion_slider_map_applies_scene_override_when_scene_matches() -> None:
    model = EmotionSliderMap.model_validate(
        {
            "baseline": {"stress_baseline": 3.0, "trust_level": -1.0},
            "scene_overrides": {
                "chapter-12": {"stress_baseline": 7.0, "trust_level": -6.0}
            },
        }
    )

    merged = model.merged_for_scene("chapter-12")
    assert merged["stress_baseline"] == 7.0
    assert merged["trust_level"] == -6.0


def test_emotion_slider_map_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        EmotionSliderMap.model_validate(
            {
                "baseline": {"stress_baseline": 12.0},
                "scene_overrides": {},
            }
        )


def test_emotion_slider_map_high_stress_injects_explicit_behavior_constraint() -> None:
    model = EmotionSliderMap.model_validate(
        {
            "baseline": {"stress_baseline": 7.2},
            "scene_overrides": {},
        }
    )

    constraint = model.build_prompt_constraint(
        character_id="hero",
        scene_id="chapter-18",
    )
    assert "High stress response" in str(constraint["system_prompt_constraint"])
