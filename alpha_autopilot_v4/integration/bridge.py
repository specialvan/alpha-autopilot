from __future__ import annotations

from .models import V4ToV3BridgeResult
from ..plot_generation.generator import generate_plot_candidates
from ..plot_generation.models import PlotGenerationResult
from ..qc.rules import evaluate_plot_qc


def build_v4_to_v3_bridge_result(context: dict[str, object]) -> V4ToV3BridgeResult:
    if context.get("v4_enabled") is False:
        empty_result = PlotGenerationResult(
            source_context=context,
            plot_candidates=[],
            selected_candidate=None,
            selection_reason="v4-disabled",
            generation_notes="V4 disabled; fallback to V3 path.",
        )
        return V4ToV3BridgeResult(
            enabled=False,
            retention_sort_key="retention_score",
            plot_generation_result=empty_result,
            v3_context={
                "retention_sort_key": "retention_score",
                "candidate_count": 0,
                "selected_candidate_id": None,
                "fallback_to_v3": True,
                "relationship_graph": {
                    "node_count": 0,
                    "edge_count": 0,
                    "displacement_count": 0,
                    "high_tension_edges": [],
                },
                "relationship_displacements": [],
                "retention_writeback": {
                    "feedback_count": 0,
                    "feedback_signal": 0.0,
                    "adaptation_mode": "v4-disabled",
                },
            },
            fallback_reason="v4_disabled",
            qc_summary={"warnings": ["v4-disabled"]},
        )

    plot_result = generate_plot_candidates(context)
    qc = evaluate_plot_qc(plot_result)
    retention_sort_key = "retention_score"
    relationship_graph = {
        "node_count": plot_result.relationship_graph.node_count if plot_result.relationship_graph else 0,
        "edge_count": plot_result.relationship_graph.edge_count if plot_result.relationship_graph else 0,
        "displacement_count": (
            plot_result.relationship_graph.displacement_count if plot_result.relationship_graph else 0
        ),
        "high_tension_edges": (
            plot_result.relationship_graph.high_tension_edges if plot_result.relationship_graph else []
        ),
    }
    relationship_displacements = [
        {
            "source_character": item.source_character,
            "target_character": item.target_character,
            "chapter_index": item.chapter_index,
            "previous_tension": item.previous_tension,
            "current_tension": item.current_tension,
            "delta_tension": item.delta_tension,
            "previous_dominant_gap": item.previous_dominant_gap,
            "current_dominant_gap": item.current_dominant_gap,
            "dominant_gap_shifted": item.dominant_gap_shifted,
            "relation_layer": item.relation_layer,
            "relation_hint": item.relation_hint,
        }
        for item in plot_result.relationship_displacements
    ]
    retention_writeback = plot_result.retention_context_used.get("retention_writeback", {})
    return V4ToV3BridgeResult(
        enabled=True,
        retention_sort_key=retention_sort_key,
        plot_generation_result=plot_result,
        v3_context={
            "retention_sort_key": retention_sort_key,
            "candidate_count": len(plot_result.plot_candidates),
            "selected_candidate_id": (
                plot_result.selected_candidate.candidate_id if plot_result.selected_candidate else None
            ),
            "fallback_to_v3": False,
            "relationship_graph": relationship_graph,
            "relationship_displacements": relationship_displacements,
            "retention_writeback": retention_writeback,
        },
        qc_summary={
            "template_risk": qc.template_risk,
            "relationship_stasis_risk": qc.relationship_stasis_risk,
            "personality_drift_risk": qc.personality_drift_risk,
            "pressure_weakness_risk": qc.pressure_weakness_risk,
            "warnings": qc.warnings,
        },
    )
