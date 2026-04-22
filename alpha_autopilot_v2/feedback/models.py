from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeedbackRecord:
    stage: str
    action: str
    predicted: float
    target: float
    feedback: float
