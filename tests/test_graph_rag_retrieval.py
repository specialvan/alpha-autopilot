from __future__ import annotations

from backend.app.services.narrative_v6.graph_rag import GraphRAGRetriever
from backend.app.services.narrative_v6.group_memory import GroupMemoryService
from backend.app.services.narrative_v6.schemas import (
    GraphRAGRetrieveRequest,
    GroupMemoryApplyRequest,
    NarrativeSeedExtractionRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _seed_payload():
    response = NarrativeSeedExtractor().extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {
                    "chapter_number": 8,
                    "text": "林墨说必须抢在黎明前拿到钥匙。苏澈问是否联手。",
                },
                {
                    "chapter_number": 9,
                    "text": "苏澈背叛了林墨，北城宣战，钥匙到底在谁手里？",
                },
            ],
        )
    )
    return response.seed, response.relationship_graph_input


def _group_memory_graph():
    return GroupMemoryService().apply(
        GroupMemoryApplyRequest(
            groups=[{"group_id": "g-1", "name": "北城守军"}],
            memberships=[{"group_id": "g-1", "character_id": "林墨", "role": "captain"}],
            group_memories=[
                {
                    "memory_id": "gm-1",
                    "group_id": "g-1",
                    "summary": "曾遭盟友背叛",
                    "influence": {"alertness": 0.6},
                    "chapter_start": 1,
                    "chapter_end": 20,
                    "hidden": True,
                    "propagation_strength": 0.8,
                }
            ],
            chapter_index=9,
            reveal_hidden=True,
        )
    )


def test_graph_rag_retriever_returns_ranked_hits_with_lexical_match() -> None:
    seed, relationship_graph_input = _seed_payload()
    retriever = GraphRAGRetriever()

    response = retriever.retrieve(
        GraphRAGRetrieveRequest(
            query="苏澈 背叛 钥匙",
            narrative_seed=seed,
            relationship_graph_input=relationship_graph_input,
            top_k=4,
        )
    )

    assert response.hits
    assert response.fallback_used is False
    assert any("背叛" in hit.summary for hit in response.hits)
    assert response.hits[0].score >= response.hits[-1].score


def test_graph_rag_retriever_uses_fallback_when_no_lexical_hit() -> None:
    seed, relationship_graph_input = _seed_payload()
    retriever = GraphRAGRetriever()

    response = retriever.retrieve(
        GraphRAGRetrieveRequest(
            query="银河舰队量子引擎",
            narrative_seed=seed,
            relationship_graph_input=relationship_graph_input,
            top_k=3,
        )
    )

    assert response.hits
    assert response.fallback_used is True
    assert response.fallback_reason == "no-lexical-hit"


def test_graph_rag_retriever_honors_hidden_filter() -> None:
    seed, relationship_graph_input = _seed_payload()
    graph = _group_memory_graph()
    retriever = GraphRAGRetriever()

    without_hidden = retriever.retrieve(
        GraphRAGRetrieveRequest(
            query="背叛",
            narrative_seed=seed,
            relationship_graph_input=relationship_graph_input,
            group_memory_graph=graph,
            include_hidden=False,
            top_k=6,
        )
    )
    with_hidden = retriever.retrieve(
        GraphRAGRetrieveRequest(
            query="背叛",
            narrative_seed=seed,
            relationship_graph_input=relationship_graph_input,
            group_memory_graph=graph,
            include_hidden=True,
            top_k=6,
        )
    )

    hidden_nodes_without = [hit for hit in without_hidden.hits if hit.hidden]
    hidden_nodes_with = [hit for hit in with_hidden.hits if hit.hidden]
    assert not hidden_nodes_without
    assert hidden_nodes_with
