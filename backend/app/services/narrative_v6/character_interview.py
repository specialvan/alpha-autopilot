from __future__ import annotations

from .schemas import CharacterInterviewRequest, CharacterInterviewResponse, InterviewMode


class CharacterInterviewService:
    def interview(
        self,
        character_id: str,
        request: CharacterInterviewRequest,
        *,
        graph_rag_hints: list[str] | None = None,
    ) -> CharacterInterviewResponse:
        profile = request.profile
        normalized_hints = [item.strip() for item in (graph_rag_hints or []) if item and item.strip()]
        memory_evidence = (
            list(request.chapter_memory[:2])
            + list(profile.evidence[:2])
            + [f"GraphRAG:{hint}" for hint in normalized_hints[:2]]
        )
        emotion_state_shift = self._emotion_shift(profile.emotion_slider_map.stress_baseline, request.user_message)
        hidden_risk_flags: list[str] = []
        ooc_risk_flags: list[str] = []

        if profile.character_id != character_id:
            ooc_risk_flags.append("character-id-mismatch")

        if self._asks_for_bottom_line_break(request.user_message, profile.desire_profile.bottom_line):
            ooc_risk_flags.append("bottom-line-violation-risk")

        if request.mode == InterviewMode.SECRET_PROBE and not request.allow_hidden_info:
            hidden_risk_flags.append("hidden-info-withheld")

        reply = self._build_reply(character_id, request, hidden_risk_flags)
        transcript = [
            {"role": "user", "content": request.user_message},
            {"role": "character", "content": reply},
        ]

        foreshadow = [
            f"{profile.name} 的隐性欲望可能在后续章节反噬主线",
            f"围绕 {profile.desire_profile.current_goal} 设计兑现/反噬双分支",
        ]

        return CharacterInterviewResponse(
            character_id=character_id,
            reply=reply,
            memory_evidence=memory_evidence,
            emotion_state_shift=emotion_state_shift,
            ooc_risk_flags=ooc_risk_flags,
            hidden_info_risk_flags=hidden_risk_flags,
            transcript=transcript,
            plot_foreshadow_candidates=foreshadow,
            graph_rag_hints=normalized_hints[:3],
        )

    def _build_reply(
        self,
        character_id: str,
        request: CharacterInterviewRequest,
        hidden_risk_flags: list[str],
    ) -> str:
        profile = request.profile
        style = profile.dialogue_style_summary or "语气平稳"

        if request.mode == InterviewMode.VOICE_TEST:
            return (
                f"[{character_id}] 我会按这个口吻说话：{style}。"
                f"当前目标是{profile.desire_profile.current_goal}。"
            )

        if request.mode == InterviewMode.SCENE_REACTION:
            return (
                f"[{character_id}] 在当前场景下，我优先{profile.desire_profile.explicit_desire}，"
                f"但不会越过底线：{profile.desire_profile.bottom_line}。"
            )

        if request.mode == InterviewMode.SECRET_PROBE:
            if hidden_risk_flags:
                return (
                    f"[{character_id}] 这个问题我不会正面回答。"
                    "你可以先证明你不是在试探我的底牌。"
                )
            return (
                f"[{character_id}] 你既然问到秘密，那我承认真正驱动力是"
                f"{profile.desire_profile.hidden_desire}。"
            )

        return (
            f"[{character_id}] 我听到了你的问题。"
            f"我会围绕{profile.desire_profile.current_goal}行动，"
            f"同时保持{style}。"
        )

    def _emotion_shift(self, stress_baseline: float, message: str) -> str:
        text = message.lower()
        if any(keyword in text for keyword in ("threat", "kill", "betray", "威胁", "背叛", "杀")):
            return "alerted"
        if stress_baseline >= 7.5:
            return "volatile"
        if stress_baseline <= -3.0:
            return "calm"
        return "stable"

    def _asks_for_bottom_line_break(self, message: str, bottom_line: str) -> bool:
        normalized = message.strip().lower()
        if not normalized:
            return False
        keywords = ("betray", "背叛", "违背", "抛弃", "kill ally", "杀同伴")
        if any(keyword in normalized for keyword in keywords):
            return True
        return bottom_line and bottom_line in message
