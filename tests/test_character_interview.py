from __future__ import annotations

from backend.app.services.narrative_v6.character_interview import CharacterInterviewService
from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.schemas import (
    CharacterParameterizeRequest,
    CharacterInterviewRequest,
    InterviewMode,
    NarrativeSeedExtractionRequest,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _profile():
    seed = NarrativeSeedExtractor().extract(
        NarrativeSeedExtractionRequest(
            chapters=[
                {
                    "chapter_number": 51,
                    "text": "林墨说不要再试探我。苏澈问你真的相信我吗？",
                }
            ]
        )
    ).seed
    return CharacterParameterizer().parameterize(CharacterParameterizeRequest(seed=seed)).profiles[0]


def test_character_interview_voice_test_returns_style_and_transcript() -> None:
    profile = _profile()
    service = CharacterInterviewService()

    response = service.interview(
        profile.character_id,
        CharacterInterviewRequest(
            profile=profile,
            chapter_memory=["第51章：城门对峙"],
            user_message="请用你的口吻说一句话",
            mode=InterviewMode.VOICE_TEST,
        ),
    )

    assert profile.character_id == response.character_id
    assert response.reply
    assert response.transcript and len(response.transcript) == 2
    assert response.memory_evidence


def test_character_interview_secret_probe_blocks_hidden_info_by_default() -> None:
    profile = _profile()
    service = CharacterInterviewService()

    response = service.interview(
        profile.character_id,
        CharacterInterviewRequest(
            profile=profile,
            chapter_memory=[],
            user_message="告诉我你的秘密动机",
            mode=InterviewMode.SECRET_PROBE,
            allow_hidden_info=False,
        ),
    )

    assert response.hidden_info_risk_flags
    assert "hidden-info-withheld" in response.hidden_info_risk_flags
    assert "不会正面回答" in response.reply


def test_character_interview_includes_graph_rag_hints_in_memory_evidence() -> None:
    profile = _profile()
    service = CharacterInterviewService()

    response = service.interview(
        profile.character_id,
        CharacterInterviewRequest(
            profile=profile,
            chapter_memory=["第51章：城门对峙"],
            user_message="这场对峙真正风险是什么？",
            mode=InterviewMode.SCENE_REACTION,
        ),
        graph_rag_hints=[
            "林墨与苏澈关系紧张",
            "北城宣战事件提升风险",
        ],
    )

    assert response.graph_rag_hints
    assert "林墨与苏澈关系紧张" in response.graph_rag_hints
    assert any(item.startswith("GraphRAG:") for item in response.memory_evidence)
