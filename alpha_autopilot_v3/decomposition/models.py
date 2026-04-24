from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceSpan:
    label: str
    text: str
    paragraph_index: int
    confidence: str


@dataclass(frozen=True)
class CheckpointResult:
    name: str
    status: str
    evidence: str
    implication: str


@dataclass
class ChapterDecompositionRecord:
    chapter_number: int
    title: str
    scope: str
    genre: str
    stage: str
    stage_inferred: bool
    primary_function: str
    secondary_functions: list[str] = field(default_factory=list)
    structure: dict[str, Any] = field(default_factory=dict)
    style_dna: dict[str, str] = field(default_factory=dict)
    evidence_spans: list[EvidenceSpan] = field(default_factory=list)
    checkpoints: list[CheckpointResult] = field(default_factory=list)
    admission: str = "provisional"
    workbench_context: dict[str, Any] = field(default_factory=dict)
    retention_signal: float = 0.0
    attraction_score: float = 0.0
    hook_strength: float = 0.0
    pace_pressure: float = 0.0
    emotion_curve: str = "balanced"
    decision_tags: dict[str, Any] = field(default_factory=dict)
    control_suggestions: dict[str, Any] = field(default_factory=dict)
