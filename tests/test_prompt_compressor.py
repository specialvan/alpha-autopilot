from __future__ import annotations

from backend.app.services.narrative_v4.bridge import build_v4_bridge_payload_with_memory
from backend.app.services.narrative_v4.memory_store import V4MemoryStore
from backend.app.services.narrative_v4.prompt_compressor import PromptCompressor


def _long_rule_document(rule_count: int = 2200) -> str:
    return "\n".join(
        f"Rule {index}: must preserve continuity and should keep causality stable."
        for index in range(rule_count)
    )


def test_prompt_compressor_auto_triggers_above_threshold_and_meets_ratio() -> None:
    compressor = PromptCompressor(threshold_tokens=2000, target_ratio=0.3, enabled=True)
    original = _long_rule_document()

    result = compressor.compress(original, mode="bullet")

    assert result["triggered"] is True
    assert result["fallback_used"] is False
    assert result["compressed_tokens"] <= int(result["original_tokens"] * 0.3) + 1
    assert result["coverage_source"] == "heuristic"


def test_prompt_compressor_supports_disable_toggle() -> None:
    compressor = PromptCompressor(threshold_tokens=2000, target_ratio=0.3, enabled=True)
    original = _long_rule_document()

    result = compressor.compress(original, mode="bullet", compress=False)

    assert result["triggered"] is False
    assert result["compressed_tokens"] == result["original_tokens"]
    assert result["coverage_source"] == "passthrough"


def test_prompt_compressor_reports_constraint_coverage_signal() -> None:
    compressor = PromptCompressor(threshold_tokens=100, target_ratio=0.3, enabled=True)
    original = _long_rule_document(rule_count=300)

    result = compressor.compress(original, mode="bullet")

    assert result["coverage_score"] >= 0.85
    assert result["coverage_source"] == "heuristic"


def test_prompt_compressor_supports_pluggable_llm_judge_for_coverage() -> None:
    compressor = PromptCompressor(
        threshold_tokens=100,
        target_ratio=0.3,
        enabled=True,
        coverage_judge=lambda _original, _compressed: 0.91,
    )
    original = _long_rule_document(rule_count=300)

    result = compressor.compress(original, mode="bullet")

    assert result["triggered"] is True
    assert result["coverage_score"] == 0.91
    assert result["coverage_source"] == "llm_judge"


def test_prompt_compressor_falls_back_to_heuristic_when_llm_judge_errors() -> None:
    def broken_judge(_original: str, _compressed: str) -> float:
        raise RuntimeError("judge-unavailable")

    compressor = PromptCompressor(
        threshold_tokens=100,
        target_ratio=0.3,
        enabled=True,
        coverage_judge=broken_judge,
    )
    original = _long_rule_document(rule_count=300)

    result = compressor.compress(original, mode="bullet")

    assert result["triggered"] is True
    assert 0.0 <= float(result["coverage_score"]) <= 1.0
    assert result["coverage_source"] == "heuristic_fallback"


def test_bridge_logs_prompt_compression_metrics_and_respects_core_instruction_passthrough(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-prompt-compress",
            "chapter_index": 18,
            "v4_enabled": True,
            "characters": [],
            "pressure_items": [],
            "prompt_documents": {
                "style_document": _long_rule_document(),
                "core_instruction_document": _long_rule_document(rule_count=200),
            },
        },
        memory_store=memory_store,
        context_id="ctx-prompt-compress",
        history_window=20,
    )

    logs = payload["prompt_compression_logs"]
    assert isinstance(logs, list)
    assert len(logs) == 2
    style_log = next(item for item in logs if item["document_key"] == "style_document")
    core_log = next(item for item in logs if item["document_key"] == "core_instruction_document")
    assert style_log["triggered"] is True
    assert style_log["mode"] == "bullet"
    assert style_log["coverage_source"] in {"heuristic", "heuristic_fallback", "llm_judge"}
    assert style_log["coverage_mode_requested"] in {"heuristic", "llm_judge"}
    assert style_log["coverage_mode_effective"] in {"heuristic", "llm_judge"}
    assert core_log["compress_enabled"] is False
    assert core_log["coverage_source"] == "passthrough"
    assert payload["memory_summary"]["prompt_compression_original_tokens"] >= payload["memory_summary"]["prompt_compression_compressed_tokens"]


def test_bridge_supports_canary_coverage_judge_mode_with_explicit_injected_judge(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-prompt-compress-canary",
            "chapter_index": 18,
            "v4_enabled": True,
            "characters": [],
            "pressure_items": [],
            "prompt_compress_coverage_mode": "llm_judge",
            "_prompt_compression_coverage_judge": lambda _original, _compressed: 0.92,
            "prompt_documents": {
                "style_document": _long_rule_document(),
            },
        },
        memory_store=memory_store,
        context_id="ctx-prompt-compress-canary",
        history_window=20,
    )

    logs = payload["prompt_compression_logs"]
    assert isinstance(logs, list)
    assert len(logs) == 1
    log = logs[0]
    assert log["coverage_mode_requested"] == "llm_judge"
    assert log["coverage_mode_effective"] == "llm_judge"
    assert log["coverage_source"] == "llm_judge"
    assert float(log["coverage_score"]) == 0.92
