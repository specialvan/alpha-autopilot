from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RetentionDesireDominant(str, Enum):
    PRIMAL_DESIRE = "primal_desire"
    VALUE_RECOGNITION = "value_recognition"
    KNOWLEDGE_CURIOSITY = "knowledge_curiosity"
    INFORMATION_GAP = "information_gap"


class RetentionDesireVector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primal_desire: float = Field(default=0.25, ge=0.0, le=1.0)
    value_recognition: float = Field(default=0.25, ge=0.0, le=1.0)
    knowledge_curiosity: float = Field(default=0.25, ge=0.0, le=1.0)
    information_gap: float = Field(default=0.25, ge=0.0, le=1.0)
    dominant: RetentionDesireDominant | None = None
    dominant_override: RetentionDesireDominant | None = None

    @model_validator(mode="after")
    def _resolve_dominant(self) -> "RetentionDesireVector":
        if self.dominant_override is not None:
            self.dominant = self.dominant_override
            return self

        weighted = [
            (RetentionDesireDominant.PRIMAL_DESIRE, self.primal_desire),
            (RetentionDesireDominant.VALUE_RECOGNITION, self.value_recognition),
            (RetentionDesireDominant.KNOWLEDGE_CURIOSITY, self.knowledge_curiosity),
            (RetentionDesireDominant.INFORMATION_GAP, self.information_gap),
        ]
        self.dominant = max(weighted, key=lambda item: item[1])[0]
        return self
