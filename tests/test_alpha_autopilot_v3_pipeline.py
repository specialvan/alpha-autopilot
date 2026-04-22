from __future__ import annotations

from alpha_autopilot_v3.decomposition.pipeline import decompose_chapter_text


def test_v3_pipeline_emits_evidence_style_qc_and_admission() -> None:
    chapter = (
        "债主在天亮前堵门。\n\n"
        "他先把欠条摔在桌上，又叫人砸碎门框。\n\n"
        "主角没有退，反而当众掀桌。\n\n"
        "巷口最后出现了一名更强的敌人。"
    )

    result = decompose_chapter_text(
        chapter_number=8,
        title="Pressure Rises in the Midpoint",
        text=chapter,
        genre="xuanhuan",
        stage="middle",
    )

    assert result.primary_function == "conflict-escalation"
    assert result.evidence_spans
    assert result.workbench_context["narrative_signals"]["conflict_intensity"] > 0.6
    assert result.admission in {"approved", "provisional", "rejected"}
