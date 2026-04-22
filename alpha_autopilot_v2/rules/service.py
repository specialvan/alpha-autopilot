from __future__ import annotations

from dataclasses import dataclass

from alpha_autopilot_v2.domain import RuleCheck, StoryState


@dataclass
class RuleService:
    def evaluate(self, state: StoryState) -> list[RuleCheck]:
        return [
            self._check_push_conflict(state),
            self._check_reveal_clue(state),
            self._check_deliver_payoff(state),
            self._check_close_sideplot(state),
            self._check_open_new_thread(state),
        ]

    def _check_push_conflict(self, state: StoryState) -> RuleCheck:
        prerequisites = ["mainline_progress>=0.20"]
        blockers: list[str] = []
        status = "legal"
        if state.mainline_progress < 0.20:
            status = "prerequisite_missing"
            blockers.append("mainline_progress_low")
        risk_flags = ["pace_overload"] if state.pacing_speed > 0.70 else []
        return RuleCheck(
            action="push_conflict",
            status=status,
            prerequisites=prerequisites,
            blockers=blockers,
            risk_flags=risk_flags,
        )

    def _check_reveal_clue(self, state: StoryState) -> RuleCheck:
        prerequisites = ["foreshadowing_load>=0.25"]
        blockers: list[str] = []
        status = "legal"
        if state.foreshadowing_load < 0.25:
            status = "prerequisite_missing"
            blockers.append("foreshadowing_load_low")
        risk_flags = ["clue_too_late"] if state.payoff_pressure > 0.82 else []
        return RuleCheck(
            action="reveal_clue",
            status=status,
            prerequisites=prerequisites,
            blockers=blockers,
            risk_flags=risk_flags,
        )

    def _check_deliver_payoff(self, state: StoryState) -> RuleCheck:
        prerequisites = ["payoff_pressure>=0.60", "stage in {mid_late,late}"]
        blockers: list[str] = []
        status = "legal"
        if state.payoff_pressure < 0.60:
            status = "blocked"
            blockers.append("payoff_pressure_low")
        elif state.stage not in {"mid_late", "late"}:
            status = "blocked"
            blockers.append("stage_not_ready")
        risk_flags = ["thin_setup"] if state.foreshadowing_load < 0.20 else []
        return RuleCheck(
            action="deliver_payoff",
            status=status,
            prerequisites=prerequisites,
            blockers=blockers,
            risk_flags=risk_flags,
        )

    def _check_close_sideplot(self, state: StoryState) -> RuleCheck:
        prerequisites = ["sideplot_progress>=0.30"]
        blockers: list[str] = []
        status = "legal"
        if state.sideplot_progress < 0.30:
            status = "prerequisite_missing"
            blockers.append("sideplot_progress_low")
        risk_flags = ["premature_convergence"] if state.stage == "opening" else []
        return RuleCheck(
            action="close_sideplot",
            status=status,
            prerequisites=prerequisites,
            blockers=blockers,
            risk_flags=risk_flags,
        )

    def _check_open_new_thread(self, state: StoryState) -> RuleCheck:
        prerequisites = ["stage!=late", "sideplot_progress<=0.75"]
        blockers: list[str] = []
        status = "legal"
        if state.stage == "late":
            status = "prerequisite_missing"
            blockers.append("late_stage_locked")
        elif state.sideplot_progress > 0.75:
            status = "blocked"
            blockers.append("sideplot_capacity_exceeded")
        risk_flags = ["focus_drift"] if state.payoff_pressure > 0.70 else []
        return RuleCheck(
            action="open_new_thread",
            status=status,
            prerequisites=prerequisites,
            blockers=blockers,
            risk_flags=risk_flags,
        )
