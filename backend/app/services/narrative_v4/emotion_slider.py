from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


CORE_EMOTION_SLIDER_DIMENSIONS: tuple[str, ...] = (
    "stress_baseline",
    "dominance",
    "trust_level",
    "emotional_volatility",
    "verbal_aggression",
    "risk_appetite",
    "moral_flexibility",
    "empathy",
    "self_disclosure",
    "goal_persistence",
    "social_energy",
    "humor_tendency",
)


class EmotionSliderMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline: dict[str, float] = Field(default_factory=dict)
    scene_overrides: dict[str, dict[str, float]] = Field(default_factory=dict)
    mbti: str | None = None
    enneagram: int | None = Field(default=None, ge=1, le=9)

    @model_validator(mode="after")
    def _validate_slider_bounds(self) -> "EmotionSliderMap":
        _validate_slider_values(self.baseline)
        for scene_payload in self.scene_overrides.values():
            _validate_slider_values(scene_payload)
        return self

    def merged_for_scene(self, scene_id: str | None) -> dict[str, float]:
        merged: dict[str, float] = {
            dimension: 0.0 for dimension in CORE_EMOTION_SLIDER_DIMENSIONS
        }
        for key, value in self.baseline.items():
            merged[key] = round(float(value), 4)
        if scene_id:
            scene_override = self.scene_overrides.get(scene_id, {})
            for key, value in scene_override.items():
                merged[key] = round(float(value), 4)
        return merged

    def build_prompt_constraint(
        self,
        *,
        character_id: str,
        scene_id: str,
    ) -> dict[str, object]:
        merged = self.merged_for_scene(scene_id)
        constraints: list[str] = []
        stress = merged.get("stress_baseline", 0.0)
        if stress > 5:
            constraints.append(
                "High stress response: use clipped dialogue, threat scanning, and rapid defensive choices."
            )
        trust = merged.get("trust_level", 0.0)
        if trust < -5:
            constraints.append(
                "Very low trust: avoid easy disclosures and keep motives guarded."
            )
        volatility = merged.get("emotional_volatility", 0.0)
        if volatility > 5:
            constraints.append(
                "Emotion volatility is high: reactions can escalate quickly under pressure."
            )
        if not constraints:
            constraints.append(
                "Keep behavior aligned with the merged emotional slider baseline for this scene."
            )
        return {
            "character_id": character_id,
            "scene_id": scene_id,
            "merged_sliders": merged,
            "system_prompt_constraint": " ".join(constraints),
            "mbti": self.mbti,
            "enneagram": self.enneagram,
        }


def _validate_slider_values(values: dict[str, float]) -> None:
    for key, raw_value in values.items():
        value = float(raw_value)
        if value < -10.0 or value > 10.0:
            raise ValueError(f"{key} must be in [-10, 10], got {value}")
