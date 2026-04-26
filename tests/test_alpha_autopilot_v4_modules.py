from __future__ import annotations

from alpha_autopilot_v4.integration import build_v4_to_v3_bridge_result
from alpha_autopilot_v4.personality import analyze_personality
from alpha_autopilot_v4.plot_generation import (
    apply_retention_feedback_writeback,
    generate_plot_candidates,
    rank_plot_candidates,
)
from alpha_autopilot_v4.pressure import PressureIntensity, PressureProfile, PressureSource, analyze_pressure
from alpha_autopilot_v4.qc import evaluate_plot_qc
from alpha_autopilot_v4.relations import analyze_relationships
from backend.app.core.config import settings
from backend.app.services.narrative_v4 import (
    V4MemoryStore,
    build_v4_bridge_payload_with_memory,
    build_v4_observability_snapshot,
    build_v4_workbench_preview,
)
from backend.app.services.narrative_v4.alert_channel import V4AlertChannel, route_v4_observability_alerts


def sample_context() -> dict[str, object]:
    return {
        "characters": [
            {
                "id": "hero",
                "status": 0.2,
                "knowledge": 0.4,
                "emotion": 0.7,
                "interest_conflict": 0.6,
                "control": 0.5,
                "dependency": 0.3,
                "trust": 0.4,
                "impulsiveness": 0.8,
                "calmness": 0.3,
                "resilience": 0.7,
                "directness": 0.9,
                "pragmatism": 0.7,
                "idealism": 0.2,
                "assertiveness": 0.8,
                "avoidance": 0.1,
                "self_protection": 0.4,
                "sacrifice_tendency": 0.3,
                "risk_appetite": 0.8,
            },
            {
                "id": "rival",
                "status": 0.8,
                "knowledge": 0.7,
                "emotion": 0.2,
                "interest_conflict": 0.8,
                "control": 0.7,
                "dependency": 0.2,
                "trust": 0.1,
                "impulsiveness": 0.3,
                "calmness": 0.8,
                "resilience": 0.5,
                "directness": 0.4,
                "pragmatism": 0.8,
                "idealism": 0.2,
                "assertiveness": 0.6,
                "avoidance": 0.2,
                "self_protection": 0.8,
                "sacrifice_tendency": 0.2,
                "risk_appetite": 0.4,
            },
        ],
        "pressure_items": [
            {"type": "survival", "intensity": 0.8},
            {"type": "humiliation", "intensity": 0.6},
        ],
        "v3_retention_context": {"retention_weight": 0.8, "tension_weight": 0.2, "template_penalty": 0.1},
    }


def test_relationship_analysis_produces_tension_and_balanced_interest_conflict() -> None:
    result = analyze_relationships(sample_context()["characters"])  # type: ignore[arg-type]
    assert result.profiles
    first = result.profiles[0]
    # (0.6 + 0.8) / 2 should be kept instead of source + target/2.
    assert first.delta.interest_conflict == 0.7
    assert result.aggregate_tension > 0
    assert result.dominant_gap in {"status", "info", "emotion"}


def test_personality_analysis_sets_preference_and_clips_values() -> None:
    profile = analyze_personality(sample_context()["characters"][0])  # type: ignore[index]
    assert profile.character_id == "hero"
    assert profile.action_preference.preferred_moves
    assert 0 <= profile.action_preference.risk_level <= 1


def test_personality_analysis_applies_genre_calibration_profile() -> None:
    profile = analyze_personality(
        sample_context()["characters"][0],  # type: ignore[index]
        genre_profile={
            "genre": "power_fantasy",
            "risk_bias": 0.08,
            "directness_bias": 0.05,
        },
    )
    assert profile.genre_calibration == "power_fantasy"
    assert profile.action_preference.risk_level > 0.8


def test_pressure_analysis_exports_profile_and_intensity() -> None:
    profile = analyze_pressure(sample_context())
    assert isinstance(profile, PressureProfile)
    assert isinstance(profile.intensity, PressureIntensity)
    assert profile.sources
    assert all(isinstance(item, PressureSource) for item in profile.sources)
    assert profile.intensity.total > 0


def test_plot_generation_produces_at_least_two_candidates_with_explanations() -> None:
    result = generate_plot_candidates(sample_context())
    assert len(result.plot_candidates) >= 2
    assert result.selected_candidate is not None
    assert result.selected_candidate.retention_score >= 0
    assert result.plot_candidates[0].explanation


def test_plot_ranker_sorts_with_retention_context_weights() -> None:
    result = generate_plot_candidates(sample_context())
    ranked = rank_plot_candidates(
        list(reversed(result.plot_candidates)),
        retention_context={"retention_weight": 1.0, "tension_weight": 0.0},
    )
    assert ranked[0].retention_score >= ranked[-1].retention_score


def test_qc_evaluates_plot_result() -> None:
    result = generate_plot_candidates(sample_context())
    qc = evaluate_plot_qc(result)
    assert qc.template_risk >= 0
    assert isinstance(qc.warnings, list)


def test_relationship_analysis_tracks_cross_chapter_displacement() -> None:
    current_characters = sample_context()["characters"]  # type: ignore[assignment]
    result = analyze_relationships(
        current_characters,  # type: ignore[arg-type]
        history=[
            {
                "source_character": "hero",
                "target_character": "rival",
                "tension_score": 0.32,
                "dominant_gap": "emotion",
                "chapter_index": 17,
            }
        ],
        chapter_index=18,
    )
    assert result.relationship_graph.node_count >= 2
    assert result.relationship_graph.edge_count >= 1
    assert result.displacement_events
    assert result.displacement_events[0].chapter_index == 18
    assert result.displacement_events[0].delta_tension > 0


def test_v4_bridge_result_contains_v3_context_and_qc_summary() -> None:
    bridge = build_v4_to_v3_bridge_result(sample_context())
    assert bridge.enabled is True
    assert bridge.v3_context["candidate_count"] >= 1
    assert bridge.plot_generation_result.selected_candidate is not None
    assert bridge.qc_summary is not None
    assert "warnings" in bridge.qc_summary
    assert "relationship_graph" in bridge.v3_context
    assert "retention_writeback" in bridge.v3_context


def test_v4_bridge_can_be_disabled_for_safe_fallback() -> None:
    bridge = build_v4_to_v3_bridge_result({"v4_enabled": False, **sample_context()})
    assert bridge.enabled is False
    assert bridge.fallback_reason == "v4_disabled"
    assert bridge.v3_context["fallback_to_v3"] is True
    assert bridge.plot_generation_result.plot_candidates == []


def test_v4_workbench_preview_maps_v2_state_into_structured_v4_candidates() -> None:
    preview = build_v4_workbench_preview(
        {
            "id": "live-chapter-18",
            "state": {
                "chapter_index": 18,
                "stage": "middle",
                "mainline_progress": 0.61,
                "sideplot_progress": 0.37,
                "conflict_intensity": 0.64,
                "emotional_temperature": 0.53,
                "pacing_speed": 0.49,
                "foreshadowing_load": 0.36,
                "payoff_pressure": 0.31,
                "characters": {},
                "tags": ["power", "middle"],
            },
        }
    )

    assert preview["enabled"] is True
    assert preview["candidate_count"] >= 2
    assert preview["selected_candidate"] is not None
    assert preview["top_candidates"]
    assert preview["top_candidates"][0]["predicted_action"]
    assert preview["v4_input_profile"]["stage"] == "middle"
    assert preview["v4_input_profile"]["chapter_index"] == 18
    assert "relationship_graph" in preview
    assert "retention_writeback" in preview
    assert isinstance(preview["relationship_timeline"], list)


def test_v4_memory_store_persists_relationship_history_across_calls(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    context = {
        "id": "ctx-memory",
        **sample_context(),
        "chapter_index": 18,
    }
    first = build_v4_bridge_payload_with_memory(
        context,
        memory_store=memory_store,
        context_id="ctx-memory",
        history_window=50,
    )
    second = build_v4_bridge_payload_with_memory(
        context,
        memory_store=memory_store,
        context_id="ctx-memory",
        history_window=50,
    )
    assert first["memory_summary"]["context_id"] == "ctx-memory"
    assert second["memory_summary"]["relationship_history_count"] >= first["memory_summary"]["relationship_history_count"]
    stored_history = memory_store.read_relationship_history("ctx-memory", limit=50)
    assert stored_history
    assert isinstance(second["relationship_timeline"], list)
    assert isinstance(second["candidate_timeline"], list)
    assert second["memory_summary"]["relationship_timeline_count"] >= 1
    assert second["memory_summary"]["candidate_timeline_count"] >= 1
    assert all("displacement_count" in item for item in second["relationship_timeline"])
    assert all("peak_delta_tension" in item for item in second["relationship_timeline"])
    assert second["memory_summary"]["relationship_timeline_displacement_count"] >= 0
    assert second["memory_summary"]["memory_strategy"] == "append-window-decay-denoise-v2"


def test_v4_memory_store_closes_feedback_loop_across_calls(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    context_with_feedback = {
        "id": "ctx-feedback",
        **sample_context(),
        "genre": "power_fantasy",
        "genre_profile": {"genre": "power_fantasy"},
        "v3_feedback_history": [
            {"accepted": False, "retention_delta": -0.2, "abandonment_delta": 0.25},
            {"accepted": True, "retention_delta": 0.09, "abandonment_delta": -0.02},
        ],
    }
    build_v4_bridge_payload_with_memory(
        context_with_feedback,
        memory_store=memory_store,
        context_id="ctx-feedback",
        history_window=50,
    )
    second = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-feedback",
            **sample_context(),
            "genre": "power_fantasy",
            "genre_profile": {"genre": "power_fantasy"},
        },
        memory_store=memory_store,
        context_id="ctx-feedback",
        history_window=50,
    )
    assert second["memory_summary"]["feedback_history_count"] >= 2
    assert second["retention_writeback"]["feedback_count"] >= 2
    assert second["memory_summary"]["feedback_denoised_count"] >= 0
    assert second["memory_summary"]["candidate_timeline_count"] >= 1
    assert second["genre_calibration"]["genre"] == "power_fantasy"
    stored_genre_feedback = memory_store.read_feedback_history_by_genre("power_fantasy", limit=20)
    assert len(stored_genre_feedback) >= 2


def test_v4_genre_auto_calibration_learns_bias_from_feedback_history(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-genre-learning",
            **sample_context(),
            "genre": "power_fantasy",
            "genre_profile": {"genre": "power_fantasy"},
            "v3_feedback_history": [
                {"accepted": True, "retention_delta": 0.14, "abandonment_delta": -0.02},
                {"accepted": True, "retention_delta": 0.12, "abandonment_delta": 0.01},
                {"accepted": True, "retention_delta": 0.09, "abandonment_delta": -0.02},
                {"accepted": False, "retention_delta": -0.04, "abandonment_delta": 0.05},
                {"accepted": True, "retention_delta": 0.11, "abandonment_delta": 0.0},
            ],
        },
        memory_store=memory_store,
        context_id="ctx-genre-learning",
        history_window=20,
    )
    genre_calibration = payload["genre_calibration"]
    assert genre_calibration["genre"] == "power_fantasy"
    assert genre_calibration["learning_mode"] == "feedback-adaptive-v1"
    assert genre_calibration["applied"] is True
    assert genre_calibration["sample_count"] >= 4
    assert genre_calibration["feedback_signal"] > 0
    assert genre_calibration["bias_updates"]["risk_appetite_bias"] > 0
    assert genre_calibration["bias_updates"]["avoidance_bias"] < 0
    summary = payload["memory_summary"]
    assert summary["genre_auto_learning_mode"] == "feedback-adaptive-v1"
    assert summary["genre_auto_learning_applied"] is True
    assert summary["genre_auto_learning_sample_count"] >= 4
    assert summary["genre_auto_learning_bias_count"] >= 1


def test_v4_genre_auto_calibration_guard_blocks_unstable_bias_update(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-genre-guard",
            **sample_context(),
            "genre": "power_fantasy",
            "genre_profile": {"genre": "power_fantasy"},
            "v3_feedback_history": [
                {"accepted": True, "retention_delta": 0.35, "abandonment_delta": -0.1},
                {"accepted": False, "retention_delta": -0.35, "abandonment_delta": 0.3},
                {"accepted": True, "retention_delta": 0.3, "abandonment_delta": -0.2},
                {"accepted": False, "retention_delta": -0.3, "abandonment_delta": 0.25},
                {"accepted": True, "retention_delta": 0.28, "abandonment_delta": -0.12},
                {"accepted": False, "retention_delta": -0.32, "abandonment_delta": 0.27},
            ],
        },
        memory_store=memory_store,
        context_id="ctx-genre-guard",
        history_window=20,
    )
    genre_calibration = payload["genre_calibration"]
    assert genre_calibration["genre"] == "power_fantasy"
    assert genre_calibration["learning_mode"] == "feedback-adaptive-v1-guarded"
    assert genre_calibration["applied"] is False
    assert genre_calibration["guard_triggered"] is True
    assert genre_calibration["guard_reason"] in {
        "high-volatility",
        "recent-long-divergence",
        "signal-reversal",
    }
    assert genre_calibration["fallback_mode"] == "no-bias-update"
    assert genre_calibration["bias_updates"] == {}
    summary = payload["memory_summary"]
    assert summary["genre_auto_learning_guard_triggered"] is True
    assert summary["genre_auto_learning_fallback_mode"] == "no-bias-update"


def test_v4_genre_auto_calibration_guard_thresholds_support_genre_override(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "v4_genre_guard_overrides_json",
        '{"power_fantasy":{"max_volatility":2.0,"max_signal_divergence":2.0,"reversal_divergence_min":2.0,"extreme_signal":1.0}}',
    )
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-genre-override",
            **sample_context(),
            "genre": "power_fantasy",
            "genre_profile": {"genre": "power_fantasy"},
            "v3_feedback_history": [
                {"accepted": True, "retention_delta": 0.42, "abandonment_delta": -0.1},
                {"accepted": False, "retention_delta": -0.31, "abandonment_delta": 0.24},
                {"accepted": True, "retention_delta": 0.33, "abandonment_delta": -0.12},
                {"accepted": True, "retention_delta": 0.21, "abandonment_delta": -0.08},
                {"accepted": False, "retention_delta": -0.2, "abandonment_delta": 0.22},
                {"accepted": True, "retention_delta": 0.28, "abandonment_delta": -0.06},
            ],
        },
        memory_store=memory_store,
        context_id="ctx-genre-override",
        history_window=20,
    )
    genre_calibration = payload["genre_calibration"]
    assert genre_calibration["genre"] == "power_fantasy"
    assert genre_calibration["learning_mode"] == "feedback-adaptive-v1"
    assert genre_calibration["guard_triggered"] is False
    assert genre_calibration["fallback_mode"] in {"bias-update-applied", "no-op-low-signal"}
    assert genre_calibration["guard_profile"]["max_volatility"] == 2.0
    assert genre_calibration["guard_profile"]["reversal_divergence_min"] == 2.0


def test_v4_memory_decay_and_denoise_strategy_handles_outliers_and_duplicates(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    noisy_relationship_history = [
        {
            "source_character": "hero",
            "target_character": "rival",
            "tension_score": 1.4 if chapter_index == 6 else (0.01 if chapter_index < 6 else 0.42),
            "dominant_gap": "emotion" if chapter_index % 2 == 0 else "status",
            "chapter_index": chapter_index,
        }
        for chapter_index in range(12)
    ]
    noisy_relationship_history.extend(
        [
            {
                "source_character": "hero",
                "target_character": "rival",
                "tension_score": 0.77,
                "dominant_gap": "emotion",
                "chapter_index": 11,
            },
            {
                "source_character": "hero",
                "target_character": "rival",
                "tension_score": 0.78,
                "dominant_gap": "emotion",
                "chapter_index": 11,
            },
        ]
    )
    noisy_feedback_history = [
        {
            "accepted": chapter_index % 3 != 0,
            "retention_delta": -1.7 if chapter_index == 4 else (0.01 if chapter_index < 5 else 0.12),
            "abandonment_delta": 1.5 if chapter_index == 4 else (0.01 if chapter_index < 5 else -0.04),
            "chapter_index": chapter_index,
        }
        for chapter_index in range(12)
    ]
    noisy_feedback_history.extend(
        [
            {"accepted": True, "retention_delta": 0.12, "abandonment_delta": -0.04, "chapter_index": 11},
            {"accepted": True, "retention_delta": 0.12, "abandonment_delta": -0.04, "chapter_index": 11},
        ]
    )
    payload = build_v4_bridge_payload_with_memory(
        {
            "id": "ctx-decay",
            **sample_context(),
            "chapter_index": 12,
            "relationship_history": noisy_relationship_history,
            "v3_feedback_history": noisy_feedback_history,
        },
        memory_store=memory_store,
        context_id="ctx-decay",
        history_window=12,
    )
    summary = payload["memory_summary"]
    assert summary["memory_strategy"] == "append-window-decay-denoise-v2"
    assert summary["relationship_history_count"] <= 12
    assert summary["feedback_history_count"] <= 12
    assert summary["relationship_clipped_count"] >= 1
    assert summary["feedback_clipped_count"] >= 1
    assert summary["relationship_collapsed_count"] >= 1
    assert (summary["feedback_collapsed_count"] + summary["feedback_merge_deduped_count"]) >= 1
    assert summary["relationship_decay_dropped_count"] >= 1
    assert summary["feedback_decay_dropped_count"] >= 1
    assert payload["candidate_timeline"]


def test_v4_observability_snapshot_reports_trend_and_alerts(tmp_path) -> None:
    memory_store = V4MemoryStore(
        relationship_path=tmp_path / "v4_relationship_memory.jsonl",
        feedback_path=tmp_path / "v4_feedback_memory.jsonl",
    )
    for chapter_index in range(15):
        accepted = chapter_index % 5 == 0
        memory_store.append_feedback_history(
            "obs-ctx-1",
            [
                {
                    "accepted": accepted,
                    "retention_delta": 0.06 if accepted else -0.2,
                    "abandonment_delta": -0.04 if accepted else 0.21,
                    "chapter_index": chapter_index,
                }
            ],
            source="test-observability",
            chapter_index=chapter_index,
            genre="power_fantasy",
        )
        memory_store.append_relationship_snapshot(
            "obs-ctx-1",
            chapter_index=chapter_index,
            payload={
                "relationship_displacements": [
                    {
                        "source_character": "hero",
                        "target_character": "rival",
                        "chapter_index": chapter_index,
                        "current_tension": 0.15 + 0.01 * (chapter_index % 3),
                        "current_dominant_gap": "status",
                    }
                ]
            },
        )

    snapshot = build_v4_observability_snapshot(memory_store, limit=200)
    assert snapshot["enabled"] is True
    assert snapshot["feedbackRows"] >= 15
    assert snapshot["relationshipRows"] >= 15
    assert isinstance(snapshot["trend"], list)
    assert snapshot["trend"]
    assert isinstance(snapshot["alerts"], list)
    assert snapshot["alertCount"] >= 1
    assert snapshot["criticalAlertCount"] >= 1
    assert any(item["code"] == "low-accept-rate" for item in snapshot["alerts"])


def test_v4_alert_channel_routes_critical_alert_and_applies_cooldown(tmp_path) -> None:
    channel = V4AlertChannel(
        sink_path=tmp_path / "v4_observability_alerts.jsonl",
        state_path=tmp_path / "v4_observability_alerts.state.json",
        cooldown_seconds=3600,
    )
    snapshot = {
        "feedbackRows": 20,
        "relationshipRows": 20,
        "acceptRate": 0.2,
        "feedbackSignal": -0.5,
        "alerts": [
            {
                "code": "low-accept-rate",
                "severity": "critical",
                "message": "Accept rate dropped below 35%.",
            }
        ],
    }
    first = route_v4_observability_alerts(snapshot, channel=channel)
    second = route_v4_observability_alerts(snapshot, channel=channel)
    assert first["routed"] is True
    assert first["reason"] == "routed-critical-alert"
    assert second["routed"] is False
    assert second["reason"] == "cooldown-active"
    assert channel.sink_path.exists()
    rows = [
        line
        for line in channel.sink_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 1


def test_apply_retention_feedback_writeback_supports_multi_window_decay_and_denoise() -> None:
    context = apply_retention_feedback_writeback(
        {
            "retention_weight": 0.72,
            "tension_weight": 0.28,
            "template_penalty": 0.08,
            "retention_feedback_history": [
                {"accepted": True, "retention_delta": 0.12, "abandonment_delta": -0.02},
                {"accepted": True, "retention_delta": 0.11, "abandonment_delta": 0.0},
                {"accepted": False, "retention_delta": -0.2, "abandonment_delta": 0.31},
                # Outlier noise: should be clipped by denoise strategy in signal processing.
                {"accepted": False, "retention_delta": -1.0, "abandonment_delta": 1.0},
                {"accepted": True, "retention_delta": 0.08, "abandonment_delta": 0.01},
            ],
        }
    )

    writeback = context["retention_writeback"]
    assert writeback["adaptation_mode"] == "feedback-driven-multi-window"
    assert writeback["aggregation_strategy"] == "multi-window-decay-denoise"
    assert isinstance(writeback["window_signals"], list)
    assert writeback["window_signals"]
    assert writeback["feedback_denoised_count"] >= 1
    assert writeback["feedback_count"] == 5
    assert context["retention_weight"] != 0.72
