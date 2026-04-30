from __future__ import annotations

from dataclasses import dataclass
import re

from .schemas import (
    GraphRAGHit,
    GraphRAGRetrieveRequest,
    GraphRAGRetrieveResponse,
    GroupMemoryEvent,
    NarrativeSeed,
    OpenThread,
    PlotEvent,
    RelationshipTriple,
    WorldRule,
)


_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{1,6}")


@dataclass(frozen=True)
class _Candidate:
    node_id: str
    node_type: str
    text: str
    confidence: float
    hidden: bool
    chapter_start: int | None
    chapter_end: int | None
    evidence: str


class GraphRAGRetriever:
    def retrieve(self, request: GraphRAGRetrieveRequest) -> GraphRAGRetrieveResponse:
        candidates = self._build_candidates(request)
        query_tokens = self._tokens(request.query)
        hits: list[GraphRAGHit] = []
        for candidate in candidates:
            if candidate.hidden and not request.include_hidden:
                continue
            if not self._in_chapter_range(
                chapter_start=candidate.chapter_start,
                chapter_end=candidate.chapter_end,
                chapter_index=request.chapter_index,
            ):
                continue
            score = self._score_candidate(candidate, query_tokens)
            if score <= 0.0:
                continue
            hits.append(
                GraphRAGHit(
                    node_id=candidate.node_id,
                    node_type=candidate.node_type,
                    summary=candidate.text,
                    score=score,
                    confidence=round(max(0.0, min(1.0, candidate.confidence)), 4),
                    evidence=candidate.evidence,
                    hidden=candidate.hidden,
                )
            )

        ranked = sorted(
            hits,
            key=lambda item: (
                item.score,
                item.confidence,
                item.node_id,
            ),
            reverse=True,
        )
        top = ranked[: request.top_k]
        fallback_used = False
        fallback_reason: str | None = None
        if not top:
            fallback_used = True
            fallback_reason = "no-lexical-hit"
            top = self._fallback_hits(candidates, request.top_k, request.include_hidden, request.chapter_index)

        return GraphRAGRetrieveResponse(
            query=request.query,
            top_k=request.top_k,
            hits=top,
            retrieval_mode="deterministic",
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )

    def _build_candidates(self, request: GraphRAGRetrieveRequest) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        seed = request.narrative_seed
        if seed is not None:
            candidates.extend(self._seed_candidates(seed))
        if request.group_memory_graph is not None:
            candidates.extend(self._group_memory_candidates(request.group_memory_graph.group_memories))
        if isinstance(request.relationship_graph_input, dict):
            candidates.extend(self._relationship_graph_candidates(request.relationship_graph_input))
        return candidates

    def _seed_candidates(self, seed: NarrativeSeed) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        for index, character in enumerate(seed.characters):
            snippet = "; ".join(character.evidence_snippets[:2]) or f"{character.name} character evidence missing"
            candidates.append(
                _Candidate(
                    node_id=f"char-{index}-{character.character_id}",
                    node_type="character",
                    text=f"{character.name}: {snippet}",
                    confidence=character.confidence,
                    hidden=False,
                    chapter_start=character.first_appeared_chapter,
                    chapter_end=None,
                    evidence=snippet,
                )
            )
        for index, relationship in enumerate(seed.relationship_triples):
            candidates.append(self._relationship_candidate(index, relationship))
        for index, rule in enumerate(seed.world_rules):
            candidates.append(self._world_rule_candidate(index, rule))
        for index, event in enumerate(seed.plot_events):
            candidates.append(self._plot_event_candidate(index, event))
        for index, thread in enumerate(seed.open_threads):
            candidates.append(self._open_thread_candidate(index, thread))
        return candidates

    def _relationship_candidate(self, index: int, relationship: RelationshipTriple) -> _Candidate:
        relation_text = f"{relationship.subject}->{relationship.target}:{relationship.relation}"
        evidence = relationship.evidence_sentence or relation_text
        return _Candidate(
            node_id=f"rel-{index}",
            node_type="relationship",
            text=relation_text,
            confidence=relationship.confidence,
            hidden=relationship.hidden,
            chapter_start=relationship.chapter_start,
            chapter_end=relationship.chapter_end,
            evidence=evidence,
        )

    def _world_rule_candidate(self, index: int, rule: WorldRule) -> _Candidate:
        return _Candidate(
            node_id=f"rule-{index}",
            node_type="world_rule",
            text=rule.rule,
            confidence=rule.confidence,
            hidden=False,
            chapter_start=None,
            chapter_end=None,
            evidence=rule.evidence_sentence or rule.rule,
        )

    def _plot_event_candidate(self, index: int, event: PlotEvent) -> _Candidate:
        participants = ",".join(event.participants) if event.participants else "unknown"
        summary = f"{event.event} | participants={participants} | consequence={event.consequence}"
        return _Candidate(
            node_id=f"event-{index}",
            node_type="plot_event",
            text=summary,
            confidence=event.confidence,
            hidden=False,
            chapter_start=event.chapter_start,
            chapter_end=event.chapter_end,
            evidence=event.evidence_sentence or event.event,
        )

    def _open_thread_candidate(self, index: int, thread: OpenThread) -> _Candidate:
        return _Candidate(
            node_id=f"thread-{index}",
            node_type="open_thread",
            text=thread.thread,
            confidence=thread.confidence,
            hidden=False,
            chapter_start=thread.chapter_hint,
            chapter_end=None,
            evidence=thread.evidence_sentence or thread.thread,
        )

    def _group_memory_candidates(self, memories: list[GroupMemoryEvent]) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        for index, memory in enumerate(memories):
            influence_bits = ",".join(
                f"{name}:{round(value, 3)}"
                for name, value in sorted(memory.influence.items())
            )
            summary = f"{memory.group_id}:{memory.summary}"
            if influence_bits:
                summary = f"{summary} | influence={influence_bits}"
            candidates.append(
                _Candidate(
                    node_id=f"group-memory-{index}-{memory.memory_id}",
                    node_type="group_memory",
                    text=summary,
                    confidence=max(0.2, min(1.0, memory.propagation_strength)),
                    hidden=memory.hidden,
                    chapter_start=memory.chapter_start,
                    chapter_end=memory.chapter_end,
                    evidence=memory.summary,
                )
            )
        return candidates

    def _relationship_graph_candidates(self, graph_payload: dict[str, object]) -> list[_Candidate]:
        edges = graph_payload.get("edges", [])
        if not isinstance(edges, list):
            return []
        candidates: list[_Candidate] = []
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("from", "")).strip()
            target = str(edge.get("to", "")).strip()
            relation = str(edge.get("relation_type", "ally")).strip()
            if not source or not target:
                continue
            intensity = self._safe_float(edge.get("intensity"), default=0.5)
            chapter_range = edge.get("chapter_range")
            chapter_start, chapter_end = self._normalize_chapter_range(chapter_range)
            summary = f"{source}->{target}:{relation}(intensity={round(intensity, 3)})"
            candidates.append(
                _Candidate(
                    node_id=f"graph-edge-{index}",
                    node_type="relationship_graph_edge",
                    text=summary,
                    confidence=max(0.0, min(1.0, intensity)),
                    hidden=bool(edge.get("hidden", False)),
                    chapter_start=chapter_start,
                    chapter_end=chapter_end,
                    evidence=summary,
                )
            )
        return candidates

    def _score_candidate(self, candidate: _Candidate, query_tokens: list[str]) -> float:
        if not query_tokens:
            return round(0.2 + candidate.confidence * 0.4 + self._node_type_boost(candidate.node_type), 4)

        candidate_text = candidate.text.lower()
        overlap = 0
        for token in query_tokens:
            if token and token in candidate_text:
                overlap += 1
        if overlap <= 0:
            return 0.0

        lexical = overlap / max(1, len(query_tokens))
        base = 0.2 + self._node_type_boost(candidate.node_type)
        score = base + lexical * 0.5 + candidate.confidence * 0.25
        return round(max(0.0, min(1.0, score)), 4)

    def _fallback_hits(
        self,
        candidates: list[_Candidate],
        top_k: int,
        include_hidden: bool,
        chapter_index: int | None,
    ) -> list[GraphRAGHit]:
        filtered = [
            item
            for item in candidates
            if (include_hidden or not item.hidden)
            and self._in_chapter_range(
                chapter_start=item.chapter_start,
                chapter_end=item.chapter_end,
                chapter_index=chapter_index,
            )
        ]
        ranked = sorted(
            filtered,
            key=lambda item: (
                item.confidence + self._node_type_boost(item.node_type),
                item.node_id,
            ),
            reverse=True,
        )
        hits: list[GraphRAGHit] = []
        for candidate in ranked[:top_k]:
            hits.append(
                GraphRAGHit(
                    node_id=candidate.node_id,
                    node_type=candidate.node_type,
                    summary=candidate.text,
                    score=round(0.2 + candidate.confidence * 0.4, 4),
                    confidence=round(max(0.0, min(1.0, candidate.confidence)), 4),
                    evidence=candidate.evidence,
                    hidden=candidate.hidden,
                )
            )
        return hits

    def _tokens(self, query: str) -> list[str]:
        tokens = [item.lower() for item in _TOKEN_PATTERN.findall(query)]
        return [item for item in tokens if item.strip()]

    def _node_type_boost(self, node_type: str) -> float:
        mapping = {
            "plot_event": 0.22,
            "open_thread": 0.2,
            "group_memory": 0.18,
            "relationship": 0.16,
            "relationship_graph_edge": 0.14,
            "world_rule": 0.1,
            "character": 0.08,
        }
        return mapping.get(node_type, 0.06)

    def _in_chapter_range(
        self,
        *,
        chapter_start: int | None,
        chapter_end: int | None,
        chapter_index: int | None,
    ) -> bool:
        if chapter_index is None:
            return True
        start_value = chapter_start if chapter_start is not None else 1
        end_value = chapter_end
        if chapter_index < start_value:
            return False
        if end_value is not None and chapter_index > end_value:
            return False
        return True

    def _normalize_chapter_range(self, raw: object) -> tuple[int | None, int | None]:
        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            return (self._safe_int(raw[0]), self._safe_int(raw[1]))
        return (None, None)

    def _safe_float(self, value: object, *, default: float) -> float:
        try:
            return float(value)  # type: ignore[arg-type]
        except Exception:
            return default

    def _safe_int(self, value: object) -> int | None:
        try:
            if value is None:
                return None
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return None
