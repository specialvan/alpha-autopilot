from __future__ import annotations

from dataclasses import dataclass

from alpha_autopilot_v2.domain import NarrativeAction, RuleCheck, SearchResult, StoryState


ACTION_LIBRARY: dict[str, NarrativeAction] = {
    "push_conflict": NarrativeAction(
        action="push_conflict",
        delta={"conflict_intensity": 0.16, "mainline_progress": 0.08, "pacing_speed": 0.04},
        explanation="Raise direct confrontation to keep the chapter advancing.",
    ),
    "reveal_clue": NarrativeAction(
        action="reveal_clue",
        delta={"foreshadowing_load": -0.08, "payoff_pressure": 0.12, "mainline_progress": 0.06},
        explanation="Reveal a key clue to convert setup into forward momentum.",
    ),
    "deliver_payoff": NarrativeAction(
        action="deliver_payoff",
        delta={"payoff_pressure": -0.28, "emotional_temperature": 0.18, "mainline_progress": 0.10},
        explanation="Cash in prepared setups to produce a strong chapter payoff.",
    ),
    "close_sideplot": NarrativeAction(
        action="close_sideplot",
        delta={"sideplot_progress": -0.16, "mainline_progress": 0.05, "payoff_pressure": -0.08},
        explanation="Close a side thread before it dilutes endgame focus.",
    ),
    "open_new_thread": NarrativeAction(
        action="open_new_thread",
        delta={"sideplot_progress": 0.18, "foreshadowing_load": 0.10, "pacing_speed": 0.06},
        explanation="Open a fresh branch to broaden narrative possibility.",
    ),
}


@dataclass
class SearchService:
    def search(self, state: StoryState, checks: list[RuleCheck]) -> list[SearchResult]:
        candidates: list[SearchResult] = []
        for check in checks:
            if check.status != "legal":
                continue
            action = ACTION_LIBRARY.get(check.action)
            if action is None:
                continue
            details = self._build_details(state, action, check)
            candidates.append(
                SearchResult(
                    action=action,
                    rule_check=check,
                    score=self._rough_score(details),
                    details=details,
                )
            )
        return sorted(candidates, key=lambda item: item.score, reverse=True)

    def _build_details(
        self,
        state: StoryState,
        action: NarrativeAction,
        check: RuleCheck,
    ) -> dict[str, float]:
        projected = self._project_state(state, action.delta)
        structure_value = _clamp01(
            0.55 * projected.mainline_progress
            + 0.35 * projected.conflict_intensity
            + max(0.0, action.delta.get("mainline_progress", 0.0)) * 0.6
        )
        continuity_safety = _clamp01(
            1.0
            - abs(projected.pacing_speed - self._target_pacing(state.stage))
            - max(0.0, projected.sideplot_progress - 0.85)
        )
        emotional_payoff = _clamp01(
            0.5 * projected.emotional_temperature
            + 0.3 * projected.payoff_pressure
            + max(0.0, action.delta.get("emotional_temperature", 0.0)) * 0.7
        )
        foreshadow_balance = _clamp01(1.0 - abs(projected.foreshadowing_load - projected.payoff_pressure))
        stage_fit = self._stage_fit(action.action, state.stage)
        feasibility = _clamp01(1.0 - 0.12 * len(check.blockers) - 0.08 * len(check.risk_flags))
        return {
            "structure_value": round(structure_value, 4),
            "continuity_safety": round(continuity_safety, 4),
            "emotional_payoff": round(emotional_payoff, 4),
            "foreshadow_balance": round(foreshadow_balance, 4),
            "stage_fit": round(stage_fit, 4),
            "feasibility": round(feasibility, 4),
        }

    def _project_state(self, state: StoryState, delta: dict[str, float]) -> StoryState:
        projected = StoryState(
            chapter_index=state.chapter_index + 1,
            stage=state.stage,
            mainline_progress=state.mainline_progress,
            sideplot_progress=state.sideplot_progress,
            conflict_intensity=state.conflict_intensity,
            emotional_temperature=state.emotional_temperature,
            pacing_speed=state.pacing_speed,
            foreshadowing_load=state.foreshadowing_load,
            payoff_pressure=state.payoff_pressure,
            characters=dict(state.characters),
            tags=list(state.tags),
        )
        for field, value in delta.items():
            if hasattr(projected, field):
                setattr(projected, field, _clamp01(float(getattr(projected, field)) + float(value)))
        return projected

    def _target_pacing(self, stage: str) -> float:
        return {
            "opening": 0.58,
            "middle": 0.52,
            "mid_late": 0.50,
            "late": 0.56,
        }.get(stage, 0.52)

    def _stage_fit(self, action: str, stage: str) -> float:
        table = {
            "push_conflict": {"opening": 0.82, "middle": 1.0, "mid_late": 0.9, "late": 0.58},
            "reveal_clue": {"opening": 0.66, "middle": 0.95, "mid_late": 0.82, "late": 0.54},
            "deliver_payoff": {"opening": 0.22, "middle": 0.40, "mid_late": 0.9, "late": 1.0},
            "close_sideplot": {"opening": 0.32, "middle": 0.62, "mid_late": 0.88, "late": 0.95},
            "open_new_thread": {"opening": 1.0, "middle": 0.84, "mid_late": 0.46, "late": 0.1},
        }
        return table.get(action, {}).get(stage, 0.5)

    def _rough_score(self, details: dict[str, float]) -> float:
        weighted = (
            0.28 * details.get("structure_value", 0.0)
            + 0.22 * details.get("continuity_safety", 0.0)
            + 0.20 * details.get("emotional_payoff", 0.0)
            + 0.18 * details.get("foreshadow_balance", 0.0)
            + 0.12 * details.get("stage_fit", 0.0)
        ) * details.get("feasibility", 1.0)
        return round(weighted, 4)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
