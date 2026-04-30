from __future__ import annotations

from .schemas import DecisionRequest, DecisionResponse, DecisionType, NarrativeDecision, RiskLevel
from .threshold_band import ThresholdBandEngine


class DecisionFeedbackController:
    def __init__(self, *, threshold_engine: ThresholdBandEngine | None = None) -> None:
        self._threshold_engine = threshold_engine or ThresholdBandEngine()

    def decide(self, payload: DecisionRequest) -> DecisionResponse:
        vector = payload.vector
        benchmark = payload.market_state.benchmark_state
        story_state = payload.market_state.story_state
        composite = vector.composite
        if payload.override_confirmed:
            decision = NarrativeDecision(
                decision_type=DecisionType.OBSERVE,
                risk_level=RiskLevel.P2,
                route_id="R-OVERRIDE",
                reasons=["Author override confirmed for current cycle"],
                suggested_actions=["continue_generation", "collect_next_cycle_metrics"],
                observe_next_metrics=["NQM", "T8", "T9", "A6"],
            )
            return DecisionResponse(decision=decision)

        # R-04: opening gate
        if int(story_state.get("chapter_index", 1)) <= 3 and vector.metrics.get("T8", 1.0) < benchmark.opening_gate_t8:
            decision = NarrativeDecision(
                decision_type=DecisionType.STOP_LOSS,
                risk_level=RiskLevel.P0,
                route_id="R-04",
                reasons=["T8 opening hook below gate threshold"],
                suggested_actions=["pause_generation", "run_opening_diagnosis", "repair_then_retry"],
                observe_next_metrics=["T8", "T4", "P3"],
            )
            return DecisionResponse(decision=decision)

        # R-08: anti-pattern critical
        if bool(story_state.get("antipattern_critical", False)):
            decision = NarrativeDecision(
                decision_type=DecisionType.STOP_LOSS,
                risk_level=RiskLevel.P0,
                route_id="R-08",
                reasons=["Anti-pattern reached CRITICAL level"],
                suggested_actions=["force_intervention", "rollback_branch", "author_confirm"],
                observe_next_metrics=["T9", "W5", "A6"],
            )
            return DecisionResponse(decision=decision)

        # R-05: deadlock
        if bool(story_state.get("deadlock_triggered", False)):
            decision = NarrativeDecision(
                decision_type=DecisionType.RETRACE_REPAIR,
                risk_level=RiskLevel.P1,
                route_id="R-05",
                reasons=["Deadlock condition detected across recent chapters"],
                suggested_actions=["parallel_path_inject", "backward_plan", "foreshadow_recycle"],
                observe_next_metrics=["T2", "T4", "P3"],
            )
            return DecisionResponse(decision=decision)

        # R-06: no hook near chapter tail
        if vector.metrics.get("T4", 0.0) <= 0.01:
            decision = NarrativeDecision(
                decision_type=DecisionType.ADD,
                risk_level=RiskLevel.P1,
                route_id="R-06",
                reasons=["Tail hook density is zero"],
                suggested_actions=["inject_hook", "raise_information_gap"],
                observe_next_metrics=["T4", "T8"],
            )
            return DecisionResponse(decision=decision)

        # R-07: antagonist pressure collapse
        if float(story_state.get("t9_delta_5chapters", 0.0)) < -0.2:
            decision = NarrativeDecision(
                decision_type=DecisionType.RETRACE_REPAIR,
                risk_level=RiskLevel.P1,
                route_id="R-07",
                reasons=["Antagonist pressure dropped too quickly"],
                suggested_actions=["restore_antagonist_capability", "add_cost_or_explanation"],
                observe_next_metrics=["T9", "P3", "W5"],
            )
            return DecisionResponse(decision=decision)

        # R-09: IP flavor corridor loss
        if float(story_state.get("a6_sigma_delta", 0.0)) < -2.0:
            decision = NarrativeDecision(
                decision_type=DecisionType.REDUCE,
                risk_level=RiskLevel.P1,
                route_id="R-09",
                reasons=["A6 dropped below IP flavor corridor"],
                suggested_actions=["re-align_flavor_vector", "reinforce_selling_point_contract"],
                observe_next_metrics=["A6", "A4", "T8"],
            )
            return DecisionResponse(decision=decision)

        # R-10: death payoff warning
        if bool(story_state.get("is_death_chapter", False)) and vector.metrics.get("W6", 1.0) < 0.4:
            decision = NarrativeDecision(
                decision_type=DecisionType.RETRACE_REPAIR,
                risk_level=RiskLevel.P1,
                route_id="R-10",
                reasons=["Death emotional payoff below quality baseline"],
                suggested_actions=["add_regret_arc", "delay_truth_reveal", "inject_vacancy_resonance"],
                observe_next_metrics=["W6", "T2", "T5"],
            )
            return DecisionResponse(decision=decision)

        zone = self._threshold_engine.classify_zone(composite, benchmark)
        if zone == "hard_intervention":
            decision = NarrativeDecision(
                decision_type=DecisionType.STOP_LOSS,
                risk_level=RiskLevel.P0,
                route_id="R-01",
                reasons=["NQM composite fell below L threshold"],
                suggested_actions=["anchor_parallel_facts", "force_repair", "manual_confirm"],
                observe_next_metrics=["NQM", "T2", "A6"],
            )
            return DecisionResponse(decision=decision)

        if zone == "elastic_injection":
            if composite >= benchmark.high_threshold - 0.02:
                decision = NarrativeDecision(
                    decision_type=DecisionType.BREAKOUT_FOLLOW,
                    risk_level=RiskLevel.P2,
                    route_id="R-02B",
                    reasons=["Composite approaching breakout threshold within elastic zone"],
                    suggested_actions=["prepare_breakout_confirmation", "avoid_oversteering"],
                    observe_next_metrics=["NQM", "T5", "T7", "A5"],
                )
                return DecisionResponse(decision=decision)
            decision = NarrativeDecision(
                decision_type=DecisionType.RETRACE_REPAIR,
                risk_level=RiskLevel.P2,
                route_id="R-02",
                reasons=["NQM composite within elastic injection zone"],
                suggested_actions=["soft_inject_parallel_event", "keep_author_intent"],
                observe_next_metrics=["NQM", "T4", "A4"],
            )
            return DecisionResponse(decision=decision)

        decision = NarrativeDecision(
            decision_type=DecisionType.OBSERVE,
            risk_level=RiskLevel.P2,
            route_id="R-03",
            reasons=["NQM composite above H threshold"],
            suggested_actions=["continue_generation", "lower_sampling_frequency"],
            observe_next_metrics=["NQM", "T9", "A6"],
        )
        return DecisionResponse(decision=decision)
