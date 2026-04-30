from __future__ import annotations

from backend.app.services.narrative_v6.schemas import NarrativeSeedExtractionRequest
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def test_seed_extractor_builds_required_structures_and_relationship_graph() -> None:
    extractor = NarrativeSeedExtractor()
    request = NarrativeSeedExtractionRequest(
        chapters=[
            {
                "chapter_number": 11,
                "title": "北城夜行",
                "text": "林墨说我们必须在日落前撤离北城。苏澈点头。王廷禁忌是不得私藏灵石。夜里林墨和苏澈成为盟友。",
            },
            {
                "chapter_number": 12,
                "title": "裂痕",
                "text": "苏澈背叛了林墨，导致北城宣战。失踪的钥匙到底去了哪里？",
            },
        ],
        mode="full",
    )

    response = extractor.extract(request)
    seed = response.seed

    assert len(seed.characters) >= 2
    assert len(seed.relationship_triples) >= 1
    assert len(seed.world_rules) >= 1
    assert len(seed.plot_events) >= 1
    assert len(seed.open_threads) >= 1

    graph_input = response.relationship_graph_input
    assert "edges" in graph_input
    assert isinstance(graph_input["edges"], list)
    assert graph_input["edges"]
    assert graph_input["edges"][0]["relation_type"] in {
        "ally",
        "friend",
        "rival",
        "enemy",
        "lover",
        "mentor",
    }


def test_seed_extractor_routes_low_confidence_fields_to_needs_review() -> None:
    extractor = NarrativeSeedExtractor()
    request = NarrativeSeedExtractionRequest(
        chapters=[
            {
                "chapter_number": 1,
                "text": "有人说可能会出事。也许会有变化。",
            }
        ],
        mode="chapter_only",
    )

    response = extractor.extract(request)

    assert response.seed.needs_review
    assert any(item.startswith("characters[") or item.startswith("world_rules[") for item in response.seed.needs_review)
