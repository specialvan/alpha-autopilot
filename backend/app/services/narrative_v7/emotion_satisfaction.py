from __future__ import annotations

from .common import clamp
from .schemas import EmotionSatisfactionRequest, EmotionSatisfactionResponse


class EmotionSatisfactionScorer:
    def score(self, payload: EmotionSatisfactionRequest) -> EmotionSatisfactionResponse:
        text = payload.text
        dimensions = {
            "security": self._density(text, ("安全", "守住", "稳定", "依靠")),
            "control": self._density(text, ("掌控", "计划", "布局", "预判")),
            "social_validation": self._density(text, ("众人", "喝彩", "见证", "认可")),
            "random_reward": self._density(text, ("突然", "意外", "竟然", "额外")),
            "ritual": self._density(text, ("仪式", "宣告", "誓言", "封赏")),
            "contrast": self._density(text, ("反差", "翻盘", "逆袭", "打脸")),
            "release": self._density(text, ("爆发", "发泄", "怒吼", "释放")),
        }

        # reader signals can override volume proxy strength
        signal_bonus = 0.0
        for key in ("comments", "follow", "collect", "pay", "fanwork"):
            signal_bonus += max(0.0, float(payload.reader_signals.get(key, 0.0)))

        score = clamp(sum(dimensions.values()) / len(dimensions))
        volume_proxy = max(0.0, 800.0 * score + 15.0 * signal_bonus)
        return EmotionSatisfactionResponse(score=score, dimensions=dimensions, volume_proxy=volume_proxy)

    def _density(self, text: str, keywords: tuple[str, ...]) -> float:
        lowered = text.lower()
        hits = 0
        for keyword in keywords:
            hits += lowered.count(keyword.lower())
        return clamp(hits / max(1.0, len(text) / 260.0))
