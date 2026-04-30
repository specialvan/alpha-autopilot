from __future__ import annotations

from collections import defaultdict
import re
from typing import Iterable

from .schemas import (
    CharacterSeed,
    NarrativePotential,
    NarrativeSeed,
    NarrativeSeedExtractionRequest,
    NarrativeSeedExtractionResponse,
    OpenThread,
    PlotEvent,
    RelationshipTriple,
    WorldRule,
)


_CHARACTER_ACTION_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9_]{1,20}|[\u4e00-\u9fff]{2,4})(?:说|问|道|看着|想|喊|笑|点头|背叛了|帮助了?|reply|asked)",
    re.IGNORECASE,
)
_ENGLISH_NAME_PATTERN = re.compile(r"\b[A-Z][a-z]{2,20}\b")
_SENTENCE_SPLIT_PATTERN = re.compile(r"[。！？!?\n]+")

_RELATION_PATTERNS: tuple[tuple[re.Pattern[str], str, float], ...] = (
    (re.compile(r"([\u4e00-\u9fff]{2,4})和([\u4e00-\u9fff]{2,4})(?:成为|是)(盟友|朋友)"), "ally", 0.82),
    (re.compile(r"([\u4e00-\u9fff]{2,4})背叛了([\u4e00-\u9fff]{2,4})"), "enemy", 0.86),
    (re.compile(r"([\u4e00-\u9fff]{2,4})帮助了?([\u4e00-\u9fff]{2,4})"), "ally", 0.74),
    (re.compile(r"([\u4e00-\u9fff]{2,4})怀疑([\u4e00-\u9fff]{2,4})"), "rival", 0.71),
)

_WORLD_RULE_KEYWORDS: tuple[str, ...] = (
    "规则",
    "禁忌",
    "必须",
    "不得",
    "法则",
    "must",
    "cannot",
)

_EVENT_KEYWORDS: tuple[str, ...] = (
    "宣战",
    "背叛",
    "死亡",
    "袭击",
    "救下",
    "失踪",
    "reveal",
    "attacked",
    "betrayed",
    "killed",
    "discovered",
)

_OPEN_THREAD_KEYWORDS: tuple[str, ...] = (
    "?",
    "？",
    "悬念",
    "未解",
    "秘密",
    "unknown",
    "where",
    "who",
)

_ENGLISH_STOPWORDS: set[str] = {
    "The",
    "And",
    "Then",
    "Chapter",
    "North",
    "South",
    "Today",
    "Night",
}


class NarrativeSeedExtractor:
    def extract(self, request: NarrativeSeedExtractionRequest) -> NarrativeSeedExtractionResponse:
        chapter_rows = [
            {
                "chapter_number": chapter.chapter_number,
                "title": chapter.title or "",
                "text": chapter.text,
            }
            for chapter in request.chapters
        ]
        names_by_chapter, evidence_by_name = self._extract_character_mentions(chapter_rows)
        characters = self._build_characters(names_by_chapter, evidence_by_name)
        relationships = self._extract_relationships(chapter_rows, characters)
        world_rules = self._extract_world_rules(chapter_rows)
        plot_events = self._extract_plot_events(chapter_rows, characters)
        open_threads = self._extract_open_threads(chapter_rows)

        needs_review = self._build_needs_review(
            characters=characters,
            relationships=relationships,
            world_rules=world_rules,
            plot_events=plot_events,
            open_threads=open_threads,
        )
        extraction_evidence = {
            "characters": [item for character in characters for item in character.evidence_snippets],
            "relationship_triples": [item.evidence_sentence for item in relationships],
            "world_rules": [item.evidence_sentence for item in world_rules],
            "plot_events": [item.evidence_sentence for item in plot_events],
            "open_threads": [item.evidence_sentence for item in open_threads],
        }

        seed = NarrativeSeed(
            characters=characters,
            relationship_triples=relationships,
            world_rules=world_rules,
            plot_events=plot_events,
            open_threads=open_threads,
            narrative_potential=self._build_narrative_potential(plot_events, open_threads),
            extraction_evidence=extraction_evidence,
            needs_review=needs_review,
        )
        return NarrativeSeedExtractionResponse(
            seed=seed,
            relationship_graph_input=self._to_relationship_graph_input(relationships),
            character_behavior_events=self._to_behavior_events(plot_events),
        )

    def _extract_character_mentions(
        self,
        chapter_rows: list[dict[str, object]],
    ) -> tuple[dict[int, list[str]], dict[str, list[str]]]:
        names_by_chapter: dict[int, list[str]] = defaultdict(list)
        evidence_by_name: dict[str, list[str]] = defaultdict(list)

        for index, row in enumerate(chapter_rows, start=1):
            chapter_number = self._chapter_number(row.get("chapter_number"), fallback=index)
            text = str(row.get("text", ""))
            for match in _CHARACTER_ACTION_PATTERN.finditer(text):
                name = self._normalize_name(match.group(1))
                if not name:
                    continue
                names_by_chapter[chapter_number].append(name)
                evidence_by_name[name].append(self._snippet(text, match.start(), match.end()))

            for match in _ENGLISH_NAME_PATTERN.finditer(text):
                candidate = match.group(0)
                if candidate in _ENGLISH_STOPWORDS:
                    continue
                name = self._normalize_name(candidate)
                if not name:
                    continue
                names_by_chapter[chapter_number].append(name)
                evidence_by_name[name].append(self._snippet(text, match.start(), match.end()))

        if not evidence_by_name:
            names_by_chapter[1].append("主角")
            evidence_by_name["主角"].append("未检出明确人名，采用默认主角占位")
        return names_by_chapter, evidence_by_name

    def _build_characters(
        self,
        names_by_chapter: dict[int, list[str]],
        evidence_by_name: dict[str, list[str]],
    ) -> list[CharacterSeed]:
        chapter_first_seen: dict[str, int] = {}
        appearance_count: dict[str, int] = defaultdict(int)

        for chapter, names in names_by_chapter.items():
            for name in names:
                appearance_count[name] += 1
                chapter_first_seen.setdefault(name, chapter)

        characters: list[CharacterSeed] = []
        for name, count in sorted(
            appearance_count.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            evidence = evidence_by_name.get(name, [])[:3]
            confidence = 0.35 if name == "主角" else min(0.95, 0.45 + count * 0.1)
            characters.append(
                CharacterSeed(
                    character_id=self._character_id(name),
                    name=name,
                    aliases=[],
                    first_appeared_chapter=chapter_first_seen.get(name),
                    appearance_count=count,
                    evidence_snippets=evidence,
                    confidence=round(confidence, 3),
                )
            )
        return characters

    def _extract_relationships(
        self,
        chapter_rows: list[dict[str, object]],
        characters: list[CharacterSeed],
    ) -> list[RelationshipTriple]:
        names = {character.name for character in characters}
        relationships: list[RelationshipTriple] = []

        for index, row in enumerate(chapter_rows, start=1):
            chapter_number = self._chapter_number(row.get("chapter_number"), fallback=index)
            text = str(row.get("text", ""))
            for pattern, relation, confidence in _RELATION_PATTERNS:
                for match in pattern.finditer(text):
                    subject = self._normalize_name(match.group(1))
                    target = self._normalize_name(match.group(2))
                    if subject not in names or target not in names or subject == target:
                        continue
                    relationships.append(
                        RelationshipTriple(
                            subject=subject,
                            relation=relation,
                            target=target,
                            chapter_start=chapter_number,
                            chapter_end=chapter_number,
                            hidden=False,
                            confidence=confidence,
                            evidence_sentence=self._snippet(text, match.start(), match.end()),
                        )
                    )

        if relationships:
            return relationships

        if len(characters) >= 2:
            first = characters[0].name
            second = characters[1].name
            return [
                RelationshipTriple(
                    subject=first,
                    relation="ally",
                    target=second,
                    chapter_start=characters[0].first_appeared_chapter,
                    chapter_end=characters[1].first_appeared_chapter,
                    hidden=False,
                    confidence=0.49,
                    evidence_sentence="未命中显式关系句，采用默认同场关系占位",
                )
            ]
        return []

    def _extract_world_rules(self, chapter_rows: list[dict[str, object]]) -> list[WorldRule]:
        rules: list[WorldRule] = []
        for row in chapter_rows:
            text = str(row.get("text", ""))
            for sentence in self._sentences(text):
                if any(keyword.lower() in sentence.lower() for keyword in _WORLD_RULE_KEYWORDS):
                    rules.append(
                        WorldRule(
                            rule=sentence,
                            confidence=0.72,
                            evidence_sentence=sentence,
                        )
                    )
                if len(rules) >= 3:
                    return rules
        if rules:
            return rules
        return [
            WorldRule(
                rule="世界规则证据不足，需作者补充边界条件",
                confidence=0.44,
                evidence_sentence="未命中规则关键词，进入人工复核",
            )
        ]

    def _extract_plot_events(
        self,
        chapter_rows: list[dict[str, object]],
        characters: list[CharacterSeed],
    ) -> list[PlotEvent]:
        events: list[PlotEvent] = []
        names = [character.name for character in characters]

        for index, row in enumerate(chapter_rows, start=1):
            chapter_number = self._chapter_number(row.get("chapter_number"), fallback=index)
            text = str(row.get("text", ""))
            for sentence in self._sentences(text):
                if not any(keyword.lower() in sentence.lower() for keyword in _EVENT_KEYWORDS):
                    continue
                participants = [name for name in names if name in sentence]
                if not participants:
                    continue
                events.append(
                    PlotEvent(
                        event=sentence,
                        participants=participants,
                        impact_targets=participants[1:] if len(participants) > 1 else participants,
                        chapter_start=chapter_number,
                        chapter_end=chapter_number,
                        consequence="tension_up",
                        confidence=0.74,
                        evidence_sentence=sentence,
                    )
                )
        if events:
            return events

        fallback_sentence = "关键剧情事件证据不足，建议补充冲突触发事件"
        return [
            PlotEvent(
                event=fallback_sentence,
                participants=[characters[0].name] if characters else [],
                impact_targets=[characters[0].name] if characters else [],
                chapter_start=1,
                chapter_end=1,
                consequence="needs_review",
                confidence=0.43,
                evidence_sentence=fallback_sentence,
            )
        ]

    def _extract_open_threads(self, chapter_rows: list[dict[str, object]]) -> list[OpenThread]:
        threads: list[OpenThread] = []
        for index, row in enumerate(chapter_rows, start=1):
            chapter_number = self._chapter_number(row.get("chapter_number"), fallback=index)
            text = str(row.get("text", ""))
            for sentence in self._sentences(text):
                if any(keyword in sentence for keyword in _OPEN_THREAD_KEYWORDS):
                    threads.append(
                        OpenThread(
                            thread=sentence,
                            chapter_hint=chapter_number,
                            confidence=0.66,
                            evidence_sentence=sentence,
                        )
                    )
        if threads:
            return threads

        fallback_sentence = "主要悬念尚未明确，建议作者补充 open thread"
        return [
            OpenThread(
                thread=fallback_sentence,
                chapter_hint=1,
                confidence=0.42,
                evidence_sentence=fallback_sentence,
            )
        ]

    def _build_narrative_potential(
        self,
        plot_events: list[PlotEvent],
        open_threads: list[OpenThread],
    ) -> NarrativePotential:
        top_events = [event.event for event in plot_events[:2]]
        top_threads = [thread.thread for thread in open_threads[:2]]
        return NarrativePotential(
            highest_tension_points=top_events,
            potential_payoffs=top_threads,
            potential_crises=top_events,
            simulation_directions=[
                "relationship_burst",
                "suspense_reveal",
                "retention_hook_first",
            ],
        )

    def _build_needs_review(
        self,
        *,
        characters: list[CharacterSeed],
        relationships: list[RelationshipTriple],
        world_rules: list[WorldRule],
        plot_events: list[PlotEvent],
        open_threads: list[OpenThread],
    ) -> list[str]:
        review_fields: list[str] = []
        for idx, character in enumerate(characters):
            if character.confidence < 0.5:
                review_fields.append(f"characters[{idx}]")
        for idx, relation in enumerate(relationships):
            if relation.confidence < 0.5:
                review_fields.append(f"relationship_triples[{idx}]")
        for idx, rule in enumerate(world_rules):
            if rule.confidence < 0.5:
                review_fields.append(f"world_rules[{idx}]")
        for idx, event in enumerate(plot_events):
            if event.confidence < 0.5:
                review_fields.append(f"plot_events[{idx}]")
        for idx, thread in enumerate(open_threads):
            if thread.confidence < 0.5:
                review_fields.append(f"open_threads[{idx}]")
        return review_fields

    def _to_relationship_graph_input(
        self,
        relationships: Iterable[RelationshipTriple],
    ) -> dict[str, object]:
        edges: list[dict[str, object]] = []
        characters: set[str] = set()
        relation_map = {
            "ally": "ally",
            "friend": "friend",
            "rival": "rival",
            "enemy": "enemy",
            "lover": "lover",
            "mentor": "mentor",
        }
        for relationship in relationships:
            relation_type = relation_map.get(relationship.relation, "ally")
            edges.append(
                {
                    "from": relationship.subject,
                    "to": relationship.target,
                    "relation_type": relation_type,
                    "intensity": round(min(max(relationship.confidence, 0.0), 1.0), 4),
                    "bidirectional": relation_type in {"ally", "friend", "lover", "mentor"},
                    "hidden": relationship.hidden,
                    "chapter_range": [relationship.chapter_start, relationship.chapter_end],
                }
            )
            characters.add(relationship.subject)
            characters.add(relationship.target)
        return {
            "characters": sorted(characters),
            "edges": edges,
        }

    def _to_behavior_events(self, plot_events: list[PlotEvent]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for event in plot_events:
            for participant in event.participants:
                rows.append(
                    {
                        "character": participant,
                        "event": event.event,
                        "pressure": event.consequence,
                        "confidence": event.confidence,
                        "chapter_start": event.chapter_start,
                    }
                )
        return rows

    def _chapter_number(self, value: object, *, fallback: int) -> int:
        try:
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return fallback

    def _sentences(self, text: str) -> list[str]:
        return [segment.strip() for segment in _SENTENCE_SPLIT_PATTERN.split(text) if segment.strip()]

    def _normalize_name(self, raw: str) -> str:
        name = raw.strip()
        if not name:
            return ""
        if len(name) == 1:
            return ""
        return name

    def _character_id(self, name: str) -> str:
        return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", name.lower()).strip("-") or "character"

    def _snippet(self, text: str, start: int, end: int, span: int = 18) -> str:
        left = max(0, start - span)
        right = min(len(text), end + span)
        return text[left:right].strip()
