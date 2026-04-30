from __future__ import annotations

from .schemas import LoopStructureRequest, LoopStructureResponse


class LoopStructureAnalyzer:
    def analyze(self, payload: LoopStructureRequest) -> LoopStructureResponse:
        scores = payload.unit_scores
        if not scores:
            return LoopStructureResponse(aligned=False, trend="flat", suggestions=["缺少单元评分，先补采样"]) 

        rising_steps = 0
        falling_steps = 0
        for index in range(1, len(scores)):
            if scores[index] > scores[index - 1]:
                rising_steps += 1
            elif scores[index] < scores[index - 1]:
                falling_steps += 1

        if rising_steps > falling_steps:
            trend = "up"
        elif falling_steps > rising_steps:
            trend = "down"
        else:
            trend = "flat"

        aligned = trend != "down"
        suggestions: list[str] = []
        if trend == "down":
            suggestions.append("卷级期待持续下行，建议补一处高价值兑现点")
        if len(set(payload.cycle_tags)) < 2:
            suggestions.append("循环类型过少，建议补人物循环或套路循环")
        if not suggestions:
            suggestions.append("多级循环走势可接受，继续保持同向共振")

        return LoopStructureResponse(aligned=aligned, trend=trend, suggestions=suggestions)
