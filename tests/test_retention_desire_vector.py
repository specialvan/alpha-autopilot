from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.services.narrative_v2.retention_desire import (
    RetentionDesireDominant,
    RetentionDesireVector,
)


def test_retention_desire_vector_allows_independent_weights() -> None:
    vector = RetentionDesireVector.model_validate(
        {
            "primal_desire": 0.9,
            "value_recognition": 0.8,
            "knowledge_curiosity": 0.7,
            "information_gap": 0.6,
        }
    )

    assert vector.primal_desire == 0.9
    assert vector.value_recognition == 0.8
    assert vector.knowledge_curiosity == 0.7
    assert vector.information_gap == 0.6


def test_retention_desire_vector_resolves_dominant_from_highest_dimension() -> None:
    vector = RetentionDesireVector.model_validate(
        {
            "primal_desire": 0.32,
            "value_recognition": 0.67,
            "knowledge_curiosity": 0.49,
            "information_gap": 0.31,
        }
    )

    assert vector.dominant == RetentionDesireDominant.VALUE_RECOGNITION


def test_retention_desire_vector_supports_dominant_override() -> None:
    vector = RetentionDesireVector.model_validate(
        {
            "primal_desire": 0.88,
            "value_recognition": 0.12,
            "knowledge_curiosity": 0.2,
            "information_gap": 0.1,
            "dominant_override": "knowledge_curiosity",
        }
    )

    assert vector.dominant == RetentionDesireDominant.KNOWLEDGE_CURIOSITY


def test_retention_desire_vector_rejects_out_of_range_values() -> None:
    with pytest.raises(ValidationError):
        RetentionDesireVector.model_validate(
            {
                "primal_desire": 1.2,
                "value_recognition": 0.5,
                "knowledge_curiosity": 0.5,
                "information_gap": 0.1,
            }
        )
