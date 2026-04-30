from __future__ import annotations

from .common import clamp
from .schemas import OpeningGateRequest, OpeningGateResponse


_TOXIC_PATTERNS: dict[str, tuple[str, ...]] = {
    "背景大科普": ("世界观", "设定如下", "历史上"),
    "碎念独白": ("我觉得", "我认为", "我想了很久"),
    "无意义日常": ("起床", "洗漱", "吃早饭"),
    "逻辑自相矛盾": ("前后矛盾", "不可能却"),
    "圣母过载": ("原谅所有人", "毫无底线"),
    "人物过载": ("张三", "李四", "王五", "赵六"),
    "梦境回忆开场": ("我做了个梦", "回忆起"),
    "系统刷屏": ("叮", "系统提示", "任务发布"),
    "文笔堆砌": ("华丽辞藻", "排比", "形容词"),
    "目标缺失": ("不知道要做什么", "漫无目的"),
}


class OpeningGate:
    def run(self, payload: OpeningGateRequest) -> OpeningGateResponse:
        t8_score = self._compute_t8(payload.text)
        toxic_hits = self._detect_toxic_hits(payload.text)
        blocked = t8_score < 0.60
        override_logged = False

        if blocked and payload.allow_override:
            blocked = False
            override_logged = True

        suggestions = self._build_suggestions(t8_score=t8_score, toxic_hits=toxic_hits)
        return OpeningGateResponse(
            blocked=blocked,
            t8_score=t8_score,
            toxic_hits=toxic_hits,
            suggestions=suggestions,
            override_logged=override_logged,
        )

    def _compute_t8(self, text: str) -> float:
        opening = text[: max(300, min(len(text), 1200))]
        conflict_signal = _contains_any(opening, ("冲突", "危机", "追杀", "威胁", "倒计时"))
        protagonist_focus = _contains_any(opening, ("我", "他", "她", "主角"))
        target_clarity = _contains_any(opening, ("必须", "目标", "要做", "完成"))
        info_gap = _contains_any(opening, ("?", "？", "真相", "为什么", "到底"))

        raw_score = (
            0.28 * conflict_signal
            + 0.24 * protagonist_focus
            + 0.24 * target_clarity
            + 0.24 * info_gap
        )
        return clamp(raw_score)

    def _detect_toxic_hits(self, text: str) -> list[str]:
        hits: list[str] = []
        for toxic_name, tokens in _TOXIC_PATTERNS.items():
            if _contains_any(text, tokens) >= 0.8:
                hits.append(toxic_name)
        return hits

    def _build_suggestions(self, *, t8_score: float, toxic_hits: list[str]) -> list[str]:
        suggestions: list[str] = []
        if t8_score < 0.60:
            suggestions.append("在前300字前置冲突和倒计时，明确主角要解决的危机")
            suggestions.append("加一处信息差钩子：读者知道但主角未知，或反过来")
        if toxic_hits:
            suggestions.append("移除命中毒点段落，保留冲突线和目标线")
        if not suggestions:
            suggestions.append("开篇通过门禁，可进入下一章生成")
        return suggestions


def _contains_any(text: str, tokens: tuple[str, ...]) -> float:
    lowered = text.lower()
    hits = 0
    for token in tokens:
        if token.lower() in lowered:
            hits += 1
    return clamp(hits / max(1.0, len(tokens)))
