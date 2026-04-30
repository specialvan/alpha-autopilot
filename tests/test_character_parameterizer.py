from __future__ import annotations

from backend.app.services.narrative_v6.character_parameterizer import CharacterParameterizer
from backend.app.services.narrative_v6.schemas import (
    CharacterFunctionType,
    CharacterParameterizeRequest,
    EmotionSliderMap,
    NarrativeSeedExtractionRequest,
    OverridePatch,
)
from backend.app.services.narrative_v6.seed_extractor import NarrativeSeedExtractor


def _build_seed():
    extractor = NarrativeSeedExtractor()
    request = NarrativeSeedExtractionRequest(
        chapters=[
            {
                "chapter_number": 3,
                "text": "林墨说先稳住阵脚。苏澈问是否宣战。林墨帮助了苏澈。",
            },
            {
                "chapter_number": 4,
                "text": "苏澈背叛了林墨，林墨立刻反击并宣战。",
            },
        ]
    )
    return extractor.extract(request).seed


def test_character_parameterizer_generates_compatible_profiles() -> None:
    seed = _build_seed()
    parameterizer = CharacterParameterizer()

    response = parameterizer.parameterize(CharacterParameterizeRequest(seed=seed))

    assert response.profiles
    profile = response.profiles[0]
    assert -10.0 <= profile.emotion_slider_map.stress_baseline <= 10.0
    assert -10.0 <= profile.emotion_slider_map.impulsiveness <= 10.0
    assert profile.function_type in set(CharacterFunctionType)
    assert profile.evidence
    assert profile.desire_profile.current_goal


def test_character_parameterizer_override_has_higher_priority() -> None:
    seed = _build_seed()
    parameterizer = CharacterParameterizer()

    primary = seed.characters[0]
    response = parameterizer.parameterize(
        CharacterParameterizeRequest(
            seed=seed,
            overrides=[
                OverridePatch(
                    character_id=primary.character_id,
                    emotion_slider_map=EmotionSliderMap(
                        stress_baseline=9.2,
                        impulsiveness=1.0,
                        empathy=0.0,
                        dominance=4.0,
                    ),
                    function_type=CharacterFunctionType.MENTOR,
                    dialogue_style_summary="作者指定口吻：克制且带威压",
                )
            ],
        )
    )

    profile = next(item for item in response.profiles if item.character_id == primary.character_id)
    assert profile.emotion_slider_map.stress_baseline == 9.2
    assert profile.function_type == CharacterFunctionType.MENTOR
    assert profile.dialogue_style_summary == "作者指定口吻：克制且带威压"
    assert profile.override_log
    assert set(profile.override_log[0].applied_fields) == {
        "emotion_slider_map",
        "function_type",
        "dialogue_style_summary",
    }
