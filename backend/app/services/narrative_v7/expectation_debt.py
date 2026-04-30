from __future__ import annotations

from .common import clamp
from .schemas import HookGuardRequest, HookGuardResponse


class ExpectationDebtManager:
    def check_hook_guard(self, payload: HookGuardRequest) -> HookGuardResponse:
        text = payload.text
        tail = text[-payload.tail_window_chars :]
        unresolved_hook_count = sum(tail.count(marker) for marker in ("?", "？", "真相", "秘密", "到底"))
        density = clamp(unresolved_hook_count / 4.0)
        triggered = density <= 0.01
        suggestions: list[str] = []
        if triggered:
            suggestions = [
                "神秘物品钩子：在章末投放带未知用途的关键物件",
                "异常事件钩子：章末发生无法解释的突变或袭击",
                "灵魂拷问钩子：角色必须在道德与生存之间二选一",
            ]

        return HookGuardResponse(
            t4_hook_density=density,
            triggered=triggered,
            suggestions=suggestions,
        )
