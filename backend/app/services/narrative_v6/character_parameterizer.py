from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .schemas import (
    BehaviorTrigger,
    CharacterFunctionType,
    CharacterParameterizeRequest,
    CharacterParameterizeResponse,
    DesireProfile,
    EmotionSliderMap,
    OverridePatch,
    OverrideRecord,
    ParameterizedCharacterProfile,
)


class CharacterParameterizer:
    def parameterize(self, request: CharacterParameterizeRequest) -> CharacterParameterizeResponse:
        selected = {item.strip().lower() for item in request.selected_character_ids if item.strip()}
        existing_profiles = {
            profile.character_id: profile
            for profile in request.existing_profiles
        }
        overrides = {patch.character_id: patch for patch in request.overrides}
        events_by_character = self._events_by_character(request.seed.plot_events)
        relationships_by_character = self._relationships_by_character(request.seed.relationship_triples)

        profiles: list[ParameterizedCharacterProfile] = []
        for index, character in enumerate(request.seed.characters):
            if selected and character.character_id.lower() not in selected and character.name.lower() not in selected:
                continue

            existing = existing_profiles.get(character.character_id)
            if existing is not None:
                profile = existing.model_copy(deep=True)
            else:
                profile = self._infer_profile(
                    index=index,
                    character=character,
                    events=events_by_character.get(character.name, []),
                    relationships=relationships_by_character.get(character.name, []),
                )

            patch = overrides.get(character.character_id)
            if patch is not None:
                profile = self._apply_override(profile, patch)
            profiles.append(profile)

        return CharacterParameterizeResponse(profiles=profiles)

    def _infer_profile(
        self,
        *,
        index: int,
        character,
        events: list[str],
        relationships: list[tuple[str, str]],
    ) -> ParameterizedCharacterProfile:
        enemy_rel = sum(1 for relation, _target in relationships if relation in {"enemy", "rival"})
        ally_rel = sum(1 for relation, _target in relationships if relation in {"ally", "friend", "mentor"})
        mention_score = max(1, character.appearance_count)

        stress_baseline = self._clamp(-10.0, 10.0, enemy_rel * 2.5 + len(events) * 1.4)
        impulsiveness = self._clamp(-10.0, 10.0, len([item for item in events if self._is_impulsive_event(item)]) * 2.0)
        empathy = self._clamp(-10.0, 10.0, 2.5 + ally_rel * 1.2 - enemy_rel * 1.3)
        dominance = self._clamp(-10.0, 10.0, mention_score * 0.8 + (enemy_rel - ally_rel) * 1.6)

        function_type = self._infer_function_type(index, enemy_rel=enemy_rel, ally_rel=ally_rel, relationships=relationships)
        dialogue_style_summary = self._summarize_dialogue(character.evidence_snippets, events)
        desire_profile = self._infer_desire_profile(character.name, events, enemy_rel=enemy_rel)
        behavior_triggers = self._infer_behavior_triggers(character.name, enemy_rel=enemy_rel, ally_rel=ally_rel)

        confidence = self._clamp(0.0, 1.0, character.confidence + min(0.25, len(events) * 0.05 + len(relationships) * 0.03))
        evidence = list(character.evidence_snippets[:3])
        evidence.extend(events[:2])

        return ParameterizedCharacterProfile(
            character_id=character.character_id,
            name=character.name,
            aliases=character.aliases,
            emotion_slider_map=EmotionSliderMap(
                stress_baseline=round(stress_baseline, 3),
                impulsiveness=round(impulsiveness, 3),
                empathy=round(empathy, 3),
                dominance=round(dominance, 3),
            ),
            function_type=function_type,
            mbti_suggestion=self._infer_mbti(impulsiveness=impulsiveness, empathy=empathy, dominance=dominance),
            enneagram_suggestion=self._infer_enneagram(enemy_rel=enemy_rel, ally_rel=ally_rel),
            dialogue_style_summary=dialogue_style_summary,
            desire_profile=desire_profile,
            behavior_triggers=behavior_triggers,
            confidence=round(confidence, 3),
            evidence=evidence,
            override_log=[],
        )

    def _apply_override(
        self,
        profile: ParameterizedCharacterProfile,
        patch: OverridePatch,
    ) -> ParameterizedCharacterProfile:
        applied_fields: list[str] = []

        if patch.emotion_slider_map is not None:
            profile.emotion_slider_map = patch.emotion_slider_map
            applied_fields.append("emotion_slider_map")

        if patch.function_type is not None:
            profile.function_type = patch.function_type
            applied_fields.append("function_type")

        if patch.dialogue_style_summary is not None:
            profile.dialogue_style_summary = patch.dialogue_style_summary
            applied_fields.append("dialogue_style_summary")

        if patch.desire_profile is not None:
            profile.desire_profile = patch.desire_profile
            applied_fields.append("desire_profile")

        if applied_fields:
            profile.override_log.append(
                OverrideRecord(
                    source="author_override",
                    applied_fields=applied_fields,
                )
            )
            profile.confidence = round(self._clamp(0.0, 1.0, profile.confidence + 0.08), 3)

        return profile

    def _events_by_character(self, plot_events: Iterable) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = defaultdict(list)
        for event in plot_events:
            for participant in event.participants:
                grouped[participant].append(event.event)
        return grouped

    def _relationships_by_character(self, relationship_triples: Iterable) -> dict[str, list[tuple[str, str]]]:
        grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for triple in relationship_triples:
            grouped[triple.subject].append((triple.relation, triple.target))
            grouped[triple.target].append((triple.relation, triple.subject))
        return grouped

    def _infer_function_type(
        self,
        index: int,
        *,
        enemy_rel: int,
        ally_rel: int,
        relationships: list[tuple[str, str]],
    ) -> CharacterFunctionType:
        if any(relation == "mentor" for relation, _target in relationships):
            return CharacterFunctionType.MENTOR
        if enemy_rel >= 2:
            return CharacterFunctionType.ANTAGONIST
        if enemy_rel >= 1 and ally_rel <= 1:
            return CharacterFunctionType.RIVAL
        if index == 0:
            return CharacterFunctionType.PROTAGONIST
        if index == 1:
            return CharacterFunctionType.DEUTERAGONIST
        if ally_rel >= 2:
            return CharacterFunctionType.CONFIDANT
        return CharacterFunctionType.CATALYST

    def _summarize_dialogue(self, snippets: list[str], events: list[str]) -> str:
        sample = snippets[0] if snippets else "证据片段不足"
        if any(self._is_impulsive_event(event) for event in events):
            return f"句式偏短促，情绪起伏明显；证据：{sample}"
        return f"语气偏克制，表达偏信息型；证据：{sample}"

    def _infer_desire_profile(self, name: str, events: list[str], *, enemy_rel: int) -> DesireProfile:
        if enemy_rel >= 1:
            explicit = "保住当前阵营优势"
            hidden = "证明自身判断正确"
            fear = "关键盟友倒戈"
            bottom_line = "不接受被公开羞辱"
            goal = "在下一章抢占叙事主动"
        elif events:
            explicit = "解决当前冲突并推进主线"
            hidden = "在团队中建立不可替代性"
            fear = "行动节奏被外部压力打断"
            bottom_line = "不能牺牲核心伙伴"
            goal = "确保下一步行动可执行"
        else:
            explicit = "厘清局势并获取更多信息"
            hidden = "避免暴露真实弱点"
            fear = "被动卷入高压冲突"
            bottom_line = "不能失去关键资源"
            goal = "先稳住局面再选择站位"

        return DesireProfile(
            explicit_desire=explicit,
            hidden_desire=hidden,
            fear=fear,
            bottom_line=bottom_line,
            current_goal=goal,
        )

    def _infer_behavior_triggers(
        self,
        name: str,
        *,
        enemy_rel: int,
        ally_rel: int,
    ) -> list[BehaviorTrigger]:
        triggers = [
            BehaviorTrigger(
                pressure="公开羞辱或威胁同伴",
                action="立即反击",
                rationale=f"{name} 在外部压力下优先维护主导权",
            )
        ]
        if enemy_rel >= ally_rel:
            triggers.append(
                BehaviorTrigger(
                    pressure="资源被对手截断",
                    action="先诈后攻",
                    rationale="敌对关系占优时更倾向风险博弈",
                )
            )
        else:
            triggers.append(
                BehaviorTrigger(
                    pressure="团队信任出现裂缝",
                    action="优先修复联盟",
                    rationale="同盟关系占优时更重视稳定合作",
                )
            )
        return triggers

    def _infer_mbti(self, *, impulsiveness: float, empathy: float, dominance: float) -> str:
        if impulsiveness >= 4 and dominance >= 2:
            return "ENTJ"
        if empathy >= 4 and impulsiveness <= 2:
            return "INFJ"
        if dominance >= 3:
            return "ESTJ"
        return "INTJ"

    def _infer_enneagram(self, *, enemy_rel: int, ally_rel: int) -> str:
        if enemy_rel > ally_rel:
            return "8w7"
        if ally_rel >= enemy_rel + 1:
            return "2w3"
        return "3w4"

    def _is_impulsive_event(self, event: str) -> bool:
        keywords = ("立刻", "冲", "怒", "宣战", "袭击", "attacked")
        return any(keyword in event for keyword in keywords)

    def _clamp(self, low: float, high: float, value: float) -> float:
        return max(low, min(high, value))
