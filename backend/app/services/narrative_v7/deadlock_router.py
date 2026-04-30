from __future__ import annotations

from .schemas import DeadlockCheckRequest, DeadlockCheckResponse


class DeadlockRouter:
    def check_and_route(self, payload: DeadlockCheckRequest) -> DeadlockCheckResponse:
        recent = payload.recent_units[-3:]
        if len(recent) < 3:
            return DeadlockCheckResponse(triggered=False, strategy="none", deadlock_log={"reason": "insufficient_window"})

        triggered = all(unit.t2_slope < 0.05 and unit.t4 < 0.2 and unit.p3 < 0.4 for unit in recent)
        if not triggered:
            return DeadlockCheckResponse(triggered=False, strategy="none", deadlock_log={"reason": "conditions_not_met"})

        strategy = self._choose_strategy(recent)
        return DeadlockCheckResponse(
            triggered=True,
            strategy=strategy,
            deadlock_log={
                "window": [unit.chapter_index for unit in recent],
                "trigger": "t2_t4_p3_joint",
                "strategy": strategy,
            },
        )

    def _choose_strategy(self, recent_units) -> str:
        avg_p3 = sum(unit.p3 for unit in recent_units) / len(recent_units)
        avg_t4 = sum(unit.t4 for unit in recent_units) / len(recent_units)
        if avg_p3 < 0.25:
            return "parallel_world_variable_injection"
        if avg_t4 < 0.10:
            return "foreshadow_recycle"
        return "goal_backtrace"
