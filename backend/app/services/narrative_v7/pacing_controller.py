from __future__ import annotations

from statistics import mean, pstdev

from .schemas import PacingRequest, PacingResponse


class PacingInformationFlowController:
    def evaluate(self, payload: PacingRequest) -> PacingResponse:
        if not payload.segment_scores:
            return PacingResponse(status="dragging", suggestions=["缺少节奏样本，先补章节分段评分"])

        avg_score = mean(payload.segment_scores)
        volatility = pstdev(payload.segment_scores) if len(payload.segment_scores) > 1 else 0.0
        info_ratio = payload.info_drop_ratio

        if avg_score < 0.4:
            return PacingResponse(
                status="dragging",
                suggestions=["整体节奏偏慢，压缩铺垫并前置冲突"],
            )
        if volatility > 0.25:
            return PacingResponse(
                status="volatile",
                suggestions=["节奏波动过大，补过渡桥段并平滑信息投放"],
            )
        if avg_score > 0.82 and info_ratio > 0.75:
            return PacingResponse(
                status="overheat",
                suggestions=["高热状态持续，建议加入喘息口防止疲劳"],
            )

        return PacingResponse(
            status="healthy",
            suggestions=["节奏与信息分配健康，保持三段给料策略"],
        )
