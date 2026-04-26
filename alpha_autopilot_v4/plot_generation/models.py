from __future__ import annotations

from dataclasses import dataclass, field

from ..personality.models import PersonalityProfile
from ..pressure.models import PressureProfile
from ..relations.models import RelationshipDisplacementEvent, RelationshipGraphSummary, RelationshipProfile


@dataclass(frozen=True)
class PlotCandidate:
    candidate_id: str
    triggering_relationships: list[RelationshipProfile]
    triggering_personalities: list[PersonalityProfile]
    triggering_pressure: PressureProfile
    predicted_action: str
    predicted_turning_point: str
    predicted_conflict_type: str
    predicted_payoff_type: str
    retention_score: float
    tension_score: float
    explanation: str
    risk_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlotGenerationResult:
    source_context: dict[str, object]
    plot_candidates: list[PlotCandidate]
    selected_candidate: PlotCandidate | None
    selection_reason: str
    generation_notes: str
    retention_context_used: dict[str, object] = field(default_factory=dict)
    relationship_graph: RelationshipGraphSummary | None = None
    relationship_displacements: list[RelationshipDisplacementEvent] = field(default_factory=list)
