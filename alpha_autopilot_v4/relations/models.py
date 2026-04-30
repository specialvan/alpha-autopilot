from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CharacterFunctionType(str, Enum):
    # Triggers emotional events for protagonist/readers.
    EMOTIONAL = "emotional"
    # Creates obstacles and bottlenecks.
    OBSTACLE = "obstacle"
    # Provides methods/resources for resolution.
    METHOD = "method"
    # Direct conflict opponent.
    CONFLICT = "conflict"
    # Worldbuilding background role.
    BACKGROUND = "background"
    # Hides true motives to create information gaps.
    DISGUISE = "disguise"
    # Stage-limited role that exits after milestone.
    TASK = "task"
    # Long-span anchor role across the whole story.
    ANCHOR = "anchor"


@dataclass(frozen=True)
class RelationshipDelta:
    status_gap: float
    info_gap: float
    emotion_gap: float
    interest_conflict: float
    control_dependency: float
    trust_state: float
    betrayal_risk: float


@dataclass(frozen=True)
class RelationshipProfile:
    source_character: str
    target_character: str
    delta: RelationshipDelta
    dominant_gap: str
    relationship_velocity: float
    tension_score: float
    relation_layer: str = "surface"
    relation_hint: str = ""


@dataclass(frozen=True)
class RelationshipDisplacementEvent:
    source_character: str
    target_character: str
    chapter_index: int | None
    previous_tension: float
    current_tension: float
    delta_tension: float
    previous_dominant_gap: str
    current_dominant_gap: str
    dominant_gap_shifted: bool
    relation_layer: str = "surface"
    relation_hint: str = ""


@dataclass(frozen=True)
class RelationshipGraphSummary:
    node_count: int
    edge_count: int
    displacement_count: int
    high_tension_edges: list[dict[str, object]]


@dataclass(frozen=True)
class RelationshipTensionResult:
    profiles: list[RelationshipProfile]
    aggregate_tension: float
    dominant_gap: str
    relationship_graph: RelationshipGraphSummary
    displacement_events: list[RelationshipDisplacementEvent]
