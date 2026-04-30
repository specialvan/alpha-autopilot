from __future__ import annotations

import json
import pytest

from backend.app.services.narrative_v7.antipattern_registry import AntiPatternRegistry
from backend.app.services.narrative_v7.benchmark_store import V7BenchmarkStore
from backend.app.services.narrative_v7.decision_controller import DecisionFeedbackController
from backend.app.services.narrative_v7.decision_rules import DecisionRuleSet
from backend.app.services.narrative_v7.deadlock_router import DeadlockRouter
from backend.app.services.narrative_v7.expectation_debt import ExpectationDebtManager
from backend.app.services.narrative_v7.market_state_adapter import StoryStateMarketAdapter
from backend.app.services.narrative_v7.nqm_sampler import NQMSampler
from backend.app.services.narrative_v7.opening_gate import OpeningGate
from backend.app.services.narrative_v7.schemas import (
    AntiPatternCheckRequest,
    BenchmarkIngestRequest,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    DeadlockCheckRequest,
    DeadlockUnitSnapshot,
    DecisionRequest,
    DecisionState,
    NovelProjectState,
    HookGuardRequest,
    NQMSampleRequest,
    NQMVector,
    NarrativeMarketState,
    NarrativeMetricOHLCV,
    OpeningGateRequest,
    StoryStateMarketAdaptRequest,
)
from backend.app.services.narrative_v7.threshold_band import ThresholdBandEngine


def test_v7_sampler_outputs_vector_and_ohlcv() -> None:
    sampler = NQMSampler()
    response = sampler.sample(
        NQMSampleRequest(
            text="主角今晚必须守住北门，否则全城覆灭。反派突然围剿，真相到底是什么？",
            story_state={"chapter_index": 1, "prev_nqm_close": 0.61},
            character_states=[{"id": "c1"}, {"id": "c2"}],
        )
    )

    assert 0.0 <= response.vector.composite <= 1.0
    assert len(response.vector.metrics) >= 28
    assert response.ohlcv.high >= response.ohlcv.low
    assert response.elapsed_ms >= 0.0


def test_story_state_market_adapter_builds_market_state_with_defaults() -> None:
    adapter = StoryStateMarketAdapter()
    response = adapter.adapt(
        StoryStateMarketAdaptRequest(
            story_state={
                "chapter_index": 7,
                "stage": "middle",
                "conflict_intensity": 0.68,
                "foreshadowing_load": 0.42,
                "payoff_pressure": 0.37,
                "tags": ["death"],
            }
        )
    )

    market_state = response.market_state
    assert market_state.story_state["chapter_index"] == 7
    assert market_state.story_state["stage"] == "middle"
    assert market_state.story_state["is_death_chapter"] is True
    assert market_state.metric_state["T8"] == pytest.approx(0.42)
    assert market_state.metric_state["T4"] == pytest.approx(0.37)
    assert market_state.metric_state["T9"] == pytest.approx(0.68)
    assert market_state.decision_state.last_composite > 0.0
    assert response.defaults_applied


def test_opening_gate_blocks_and_supports_override() -> None:
    gate = OpeningGate()

    blocked = gate.run(
        OpeningGateRequest(
            text="我起床洗漱吃早饭，想了很多人生道理。",
            chapter_index=1,
            allow_override=False,
        )
    )
    assert blocked.blocked is True

    override = gate.run(
        OpeningGateRequest(
            text="我起床洗漱吃早饭，想了很多人生道理。",
            chapter_index=1,
            allow_override=True,
        )
    )
    assert override.blocked is False
    assert override.override_logged is True


def test_hook_guard_produces_suggestions_when_no_hook() -> None:
    manager = ExpectationDebtManager()
    result = manager.check_hook_guard(HookGuardRequest(text="这是一个平淡的收尾，没有任何疑问句。"))
    assert result.triggered is True
    assert len(result.suggestions) == 3


def test_deadlock_router_detects_three_chapter_deadlock() -> None:
    router = DeadlockRouter()
    result = router.check_and_route(
        DeadlockCheckRequest(
            recent_units=[
                DeadlockUnitSnapshot(chapter_index=10, t2_slope=0.01, t4=0.0, p3=0.2),
                DeadlockUnitSnapshot(chapter_index=11, t2_slope=0.02, t4=0.1, p3=0.3),
                DeadlockUnitSnapshot(chapter_index=12, t2_slope=0.03, t4=0.1, p3=0.25),
            ]
        )
    )
    assert result.triggered is True
    assert result.strategy in {
        "parallel_world_variable_injection",
        "foreshadow_recycle",
        "goal_backtrace",
    }


def test_antipattern_registry_escalates_to_critical() -> None:
    registry = AntiPatternRegistry()
    vector = NQMVector(
        metrics={
            "P1": 0.5,
            "P2": 0.5,
            "P3": 0.2,
            "P4": 0.5,
            "P5": 0.5,
            "P6": 0.3,
            "P7": 0.3,
            "T1": 0.5,
            "T2": 0.2,
            "T3": 0.5,
            "T4": 0.5,
            "T5": 0.5,
            "T6": 0.5,
            "T7": 0.5,
            "T8": 0.5,
            "T9": 0.2,
            "T10": 0.5,
            "W1": 0.2,
            "W2": 0.5,
            "W3": 0.5,
            "W4": 0.5,
            "W5": 0.5,
            "W6": 0.5,
            "A1": 0.5,
            "A2": 0.5,
            "A3": 0.5,
            "A4": 0.5,
            "A5": 0.5,
            "A6": 0.2,
        },
        composite=0.3,
    )
    result = registry.evaluate(AntiPatternCheckRequest(vector=vector, continuous_trigger_count=3))
    assert result.critical is True
    assert result.alerts
    assert all(alert.severity.value == "CRITICAL" for alert in result.alerts)


def test_threshold_engine_classifies_zone() -> None:
    engine = ThresholdBandEngine()
    benchmark = BenchmarkParameterSet(high_threshold=0.78, low_threshold=0.52)
    assert engine.classify_zone(0.40, benchmark=benchmark) == "hard_intervention"
    assert engine.classify_zone(0.60, benchmark=benchmark) == "elastic_injection"
    assert engine.classify_zone(0.90, benchmark=benchmark) == "free_generation"


def test_benchmark_store_ingest_query_and_retract(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")

    accepted = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-001",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.72},
        )
    )
    assert accepted.accepted is True

    query = store.query(BenchmarkQueryRequest(channel="fantasy", genre_track="fast"))
    assert query.source_count == 1
    assert query.benchmark.nqm_mean > 0.6

    assert store.retract("book-001") is True
    query_after = store.query(BenchmarkQueryRequest(channel="fantasy", genre_track="fast"))
    assert query_after.source_count == 0


def test_benchmark_store_version_listing_and_restore(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")

    first = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-a",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.70},
        )
    )
    second = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-b",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.80},
        )
    )

    assert first.accepted is True
    assert second.accepted is True

    versions = store.list_versions(limit=10)
    assert len(versions) >= 2

    restored = store.restore(versions[0].version)
    assert restored.restored is True
    assert restored.requested_version == versions[0].version

    query = store.query(BenchmarkQueryRequest(channel="fantasy", genre_track="fast"))
    assert query.source_count == versions[0].active_rows


def test_decision_ruleset_supports_file_override(tmp_path) -> None:
    rule_file = tmp_path / "decision_rules.json"
    rule_file.write_text(
        json.dumps(
            {
                "opening_t8_gate": 0.91,
                "early_chapter_limit": 5,
                "elastic_breakout_margin": 0.03,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    rules = DecisionRuleSet(config_path=str(rule_file))
    current = rules.current()
    assert current["opening_t8_gate"] == 0.91
    assert current["early_chapter_limit"] == 5.0
    assert current["elastic_breakout_margin"] == 0.03
    assert "tail_hook_zero_threshold" in current


def test_benchmark_store_compare_versions_and_export_audit(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-a",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.70},
        )
    )
    second = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-b",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.80},
        )
    )
    assert second.accepted is True
    assert store.retract("book-b") is True

    latest_versions = store.list_versions(limit=10)
    assert latest_versions

    diff = store.compare_versions(base_version=second.version, target_version=latest_versions[0].version)
    assert diff.comparable is True
    assert "book-b" in diff.deactivated_book_ids
    assert diff.deactivated_count >= 1

    audit = store.export_audit(limit=10)
    assert audit.version_count >= 3
    assert audit.integrity_failed_count == 0


def test_benchmark_store_restore_rejects_tampered_snapshot(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    accepted = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-tamper",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.75},
        )
    )
    assert accepted.accepted is True

    snapshot_path = store.version_root / f"{accepted.version}.json"
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.21
    snapshot_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    restored = store.restore(accepted.version)
    assert restored.restored is False
    assert restored.message == "snapshot_integrity_failed"


def test_benchmark_store_prunes_old_versions(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-prune-a",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.61},
        )
    )
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-prune-b",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.71},
        )
    )
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-prune-c",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.81},
        )
    )
    before = store.list_versions(limit=20)
    assert len(before) >= 3

    dry_run = store.prune_versions(keep_last=1, dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.pruned_count == 0
    assert dry_run.candidate_count >= 2

    applied = store.prune_versions(keep_last=1, dry_run=False)
    assert applied.dry_run is False
    assert applied.pruned_count >= 2

    after = store.list_versions(limit=20)
    assert len(after) == 1


def test_benchmark_store_health_scan_detects_tamper_and_malformed(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    accepted = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-health",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.78},
        )
    )
    assert accepted.accepted is True

    tampered_path = store.version_root / f"{accepted.version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.11
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    malformed_path = store.version_root / "malformed.json"
    malformed_path.write_text("{bad-json", encoding="utf-8")

    health = store.scan_version_health()
    assert health.total_files >= 2
    assert health.failed_integrity_count >= 1
    assert health.malformed_file_count >= 1


def test_benchmark_store_repairs_failed_and_malformed_snapshots(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    accepted = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-repair",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.69},
        )
    )
    assert accepted.accepted is True

    tampered_path = store.version_root / f"{accepted.version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.09
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    malformed_path = store.version_root / "repair-malformed.json"
    malformed_path.write_text("{bad-json", encoding="utf-8")

    dry_run = store.repair_versions(dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.candidate_failed_count >= 1
    assert dry_run.candidate_malformed_count >= 1
    assert dry_run.moved_count == 0

    applied = store.repair_versions(dry_run=False)
    assert applied.dry_run is False
    assert applied.moved_count >= 2

    health_after = store.scan_version_health()
    assert health_after.failed_integrity_count == 0
    assert health_after.malformed_file_count == 0


def test_benchmark_store_builds_maintenance_report(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-maint",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.74},
        )
    )
    report = store.build_maintenance_report(limit=20)
    assert report.audit.version_count >= 1
    assert report.health.total_files >= 1
    assert report.severity in {"ok", "warn", "critical"}


def test_benchmark_store_auto_remediate_versions(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    first = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-auto-a",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.61},
        )
    )
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-auto-b",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.71},
        )
    )
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-auto-c",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.81},
        )
    )
    tampered_path = store.version_root / f"{first.version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.05
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (store.version_root / "auto-malformed.json").write_text("{bad-json", encoding="utf-8")

    dry_run = store.auto_remediate_versions(dry_run=True, keep_last=1)
    assert dry_run.dry_run is True
    assert dry_run.repair.candidate_failed_count >= 1
    assert dry_run.repair.candidate_malformed_count >= 1
    assert dry_run.prune.candidate_count >= 2
    assert dry_run.health_after.failed_integrity_count >= 1

    applied = store.auto_remediate_versions(dry_run=False, keep_last=1)
    assert applied.dry_run is False
    assert applied.repair.moved_count >= 2
    assert applied.health_after.failed_integrity_count == 0
    assert applied.health_after.malformed_file_count == 0


def test_benchmark_store_builds_maintenance_alert_with_sla(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    accepted = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-a",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.62},
        )
    )
    assert accepted.accepted is True

    tampered_path = store.version_root / f"{accepted.version}.json"
    payload = json.loads(tampered_path.read_text(encoding="utf-8"))
    payload["rows"][0]["nqm_mean"] = 0.01
    tampered_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setenv("AA_V7_BENCH_SLA_MAX_FAILED_INTEGRITY", "0")
    monkeypatch.setenv("AA_V7_BENCH_SLA_MAX_MALFORMED_FILES", "0")
    monkeypatch.setenv("AA_V7_BENCH_SLA_MAX_UNVERIFIED", "0")

    alert = store.build_maintenance_alert(limit=20)
    assert alert.level == "critical"
    assert alert.should_page is True
    assert alert.breaches


def test_benchmark_store_emits_and_lists_maintenance_alert_events(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-event",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.64},
        )
    )

    emitted = store.emit_maintenance_alert(limit=20)
    assert emitted.event.level in {"ok", "warn", "critical"}
    assert emitted.event.event_id

    listed = store.list_maintenance_alerts(limit=20)
    assert listed.alerts
    assert listed.alerts[0].event_id == emitted.event.event_id


def test_benchmark_store_prunes_maintenance_alert_events(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.68},
        )
    )

    emitted_ids: list[str] = []
    for _ in range(3):
        emitted = store.emit_maintenance_alert(limit=20)
        emitted_ids.append(emitted.event.event_id)

    alerts_path = store.version_root / "_maintenance_alerts.jsonl"
    with alerts_path.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run = store.prune_maintenance_alerts(keep_last=1, dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.total_alerts_before >= 3
    assert dry_run.candidate_count >= 2
    assert dry_run.pruned_count == 0
    assert dry_run.malformed_candidate_count >= 1

    applied = store.prune_maintenance_alerts(keep_last=1, dry_run=False)
    assert applied.dry_run is False
    assert applied.kept_count == 1
    assert applied.pruned_count >= 2
    assert applied.malformed_dropped_count >= 1

    listed_after = store.list_maintenance_alerts(limit=20)
    assert len(listed_after.alerts) == 1
    assert listed_after.alerts[0].event_id in emitted_ids


def test_benchmark_store_summarizes_maintenance_alert_events(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-summary",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.70},
        )
    )

    for _ in range(3):
        _ = store.emit_maintenance_alert(limit=20)

    alerts_path = store.version_root / "_maintenance_alerts.jsonl"
    with alerts_path.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    summary = store.summarize_maintenance_alerts(limit=2)
    assert summary.total_valid_events >= 3
    assert summary.window_event_count == 2
    assert summary.malformed_line_count >= 1
    assert summary.latest_event is not None
    assert (summary.ok_count + summary.warn_count + summary.critical_count) == summary.window_event_count


def test_benchmark_store_builds_maintenance_alert_digest(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-digest",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.66},
        )
    )
    _ = store.emit_maintenance_alert(limit=20)

    digest = store.build_maintenance_alert_digest(limit=20)
    assert digest.current_alert.level in {"ok", "warn", "critical"}
    assert digest.summary.total_valid_events >= 1
    assert digest.stale_threshold_seconds >= 0
    assert digest.recommended_action in {
        "observe",
        "emit_fresh_alert",
        "create_ticket",
        "page_oncall",
        "clean_alert_log",
    }


def test_benchmark_store_exports_maintenance_alerts(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-export",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.72},
        )
    )
    _ = store.emit_maintenance_alert(limit=20)

    exported = store.export_maintenance_alerts(limit=20)
    assert exported.limit == 20
    assert exported.digest.current_alert.level in {"ok", "warn", "critical"}
    assert exported.digest.summary.total_valid_events >= 1
    assert exported.alerts


def test_benchmark_store_supports_maintenance_alert_cursor_paging(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-cursor",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.67},
        )
    )
    for _ in range(5):
        _ = store.emit_maintenance_alert(limit=20)

    first = store.list_maintenance_alerts(limit=2, cursor="")
    assert len(first.alerts) == 2
    assert first.has_more is True
    assert first.next_cursor
    assert first.total_valid_events >= 5

    second = store.list_maintenance_alerts(limit=2, cursor=first.next_cursor)
    assert len(second.alerts) == 2
    assert second.cursor == first.next_cursor
    assert second.alerts[0].event_id != first.alerts[0].event_id

    exported = store.export_maintenance_alerts(limit=2, cursor=first.next_cursor)
    assert len(exported.alerts) == 2
    assert exported.cursor == first.next_cursor
    assert exported.total_valid_events >= 5
    assert exported.has_more in {True, False}


def test_benchmark_store_archives_maintenance_alerts_into_shards(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-archive",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.69},
        )
    )
    for _ in range(5):
        _ = store.emit_maintenance_alert(limit=20)

    alerts_path = store.version_root / "_maintenance_alerts.jsonl"
    with alerts_path.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run = store.archive_maintenance_alerts(keep_last=2, shard_size=2, dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.kept_count == 2
    assert dry_run.candidate_count >= 3
    assert dry_run.archive_shard_count == 0
    assert dry_run.malformed_candidate_count >= 1

    applied = store.archive_maintenance_alerts(keep_last=2, shard_size=2, dry_run=False)
    assert applied.dry_run is False
    assert applied.kept_count == 2
    assert applied.archived_count >= 3
    assert applied.archive_shard_count >= 2
    assert applied.malformed_dropped_count >= 1
    assert applied.archive_files

    listed_after = store.list_maintenance_alerts(limit=20)
    assert len(listed_after.alerts) == 2

    archive_dir = alerts_path.parent / "_maintenance_alerts_archive"
    for file_name in applied.archive_files:
        assert (archive_dir / file_name).exists()


def test_benchmark_store_lists_and_reads_alert_archive_files(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-archive-read",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.63},
        )
    )
    for _ in range(5):
        _ = store.emit_maintenance_alert(limit=20)
    _ = store.archive_maintenance_alerts(keep_last=2, shard_size=2, dry_run=False)

    archive_list = store.list_maintenance_alert_archive_files(limit=20)
    assert archive_list.total_files >= 2
    assert archive_list.files
    first_file = archive_list.files[0].file_name
    assert first_file.endswith(".jsonl")

    first_page = store.read_maintenance_alert_archive_file(file_name=first_file, limit=1, cursor="")
    assert first_page.message == "ok"
    assert first_page.total_valid_events >= 1
    assert len(first_page.alerts) == 1

    invalid = store.read_maintenance_alert_archive_file(file_name="../bad.jsonl", limit=1, cursor="")
    assert invalid.message == "invalid_file_name"


def test_benchmark_store_auto_archives_alerts_by_policy(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-auto-archive",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.64},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")

    dry_run = store.auto_archive_maintenance_alerts(dry_run=True)
    assert dry_run.should_archive is True
    assert dry_run.archive is not None
    assert dry_run.archive.dry_run is True
    assert dry_run.archive.candidate_count >= 3

    applied = store.auto_archive_maintenance_alerts(dry_run=False)
    assert applied.should_archive is True
    assert applied.archive is not None
    assert applied.archive.dry_run is False
    assert applied.archive.kept_count == 1
    assert applied.archive.archived_count >= 3

    listed_after = store.list_maintenance_alerts(limit=20)
    assert len(listed_after.alerts) == 1


def test_benchmark_store_cleans_up_alert_archive_by_policy(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-archive-cleanup",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.61},
        )
    )
    for _ in range(6):
        _ = store.emit_maintenance_alert(limit=20)
    _ = store.archive_maintenance_alerts(keep_last=1, shard_size=1, dry_run=False)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "2")

    dry_run = store.cleanup_maintenance_alert_archives(dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.total_files >= 5
    assert dry_run.candidate_count >= 3
    assert dry_run.max_shard_candidate_count >= 3
    assert dry_run.removed_count == 0

    applied = store.cleanup_maintenance_alert_archives(dry_run=False)
    assert applied.dry_run is False
    assert applied.removed_count >= 3
    assert applied.kept_count <= 2

    archive_list = store.list_maintenance_alert_archive_files(limit=20)
    assert archive_list.total_files <= 2


def test_benchmark_store_builds_and_runs_alert_governance(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.68},
        )
    )
    for _ in range(5):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    report = store.build_maintenance_alert_governance_report(alert_limit=20, archive_limit=20)
    assert report.policy.archive_trigger_count == 2
    assert report.projected_auto_archive.should_archive is True
    assert report.projected_auto_archive.archive is not None

    dry_run = store.run_maintenance_alert_governance(dry_run=True, alert_limit=20, archive_limit=20)
    assert dry_run.dry_run is True
    assert dry_run.auto_archive.should_archive is True
    assert dry_run.performed_steps
    assert dry_run.active_summary_after.total_valid_events == dry_run.active_summary_before.total_valid_events

    applied = store.run_maintenance_alert_governance(dry_run=False, alert_limit=20, archive_limit=20)
    assert applied.dry_run is False
    assert applied.auto_archive.should_archive is True
    assert applied.auto_archive.archive is not None
    assert applied.active_summary_after.total_valid_events <= 1


def test_benchmark_store_governance_run_supports_idempotency(tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-idempotency",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.68},
        )
    )
    for _ in range(5):
        _ = store.emit_maintenance_alert(limit=20)

    first = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="idem-governance-001",
    )
    second = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="idem-governance-001",
    )

    assert second.idempotency_reused is True
    assert second.run_id == first.run_id
    assert second.request_fingerprint == first.request_fingerprint

    history = store.list_maintenance_alert_governance_runs(limit=20)
    assert history.total_records == 1
    assert history.records[0].status == "succeeded"

    with pytest.raises(ValueError, match="idempotency_key_reused_with_different_request"):
        _ = store.run_maintenance_alert_governance(
            dry_run=False,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="idem-governance-001",
        )


def test_benchmark_store_governance_run_records_failure_and_retry(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-retry",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.71},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    original_auto_archive = store.auto_archive_maintenance_alerts
    call_counter = {"value": 0}

    def flaky_auto_archive(*, dry_run: bool = True):
        call_counter["value"] += 1
        if call_counter["value"] == 1:
            raise RuntimeError("forced_governance_auto_archive_failure")
        return original_auto_archive(dry_run=dry_run)

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", flaky_auto_archive)

    with pytest.raises(RuntimeError, match="forced_governance_auto_archive_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="governance-retry-seed",
        )

    failed_history = store.list_maintenance_alert_governance_runs(limit=20)
    assert failed_history.total_records == 1
    failed_record = failed_history.records[0]
    assert failed_record.status == "failed"
    assert failed_record.error_type == "RuntimeError"
    assert "forced_governance_auto_archive_failure" in failed_record.error_message

    retry_result = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        retry_run_id=failed_record.run_id,
        idempotency_key="governance-retry-001",
    )
    assert retry_result.retry_run_id == failed_record.run_id
    assert retry_result.attempt == 2
    assert retry_result.idempotency_reused is False

    history = store.list_maintenance_alert_governance_runs(limit=20)
    assert history.total_records == 2
    assert history.records[0].status == "succeeded"
    assert history.records[0].attempt == 2
    assert history.records[1].status == "failed"


def test_benchmark_store_prunes_governance_runs(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.72},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    for index in range(3):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key=f"governance-prune-{index}",
        )

    governance_log = store.version_root / "_maintenance_alert_governance_runs.jsonl"
    with governance_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run = store.prune_maintenance_alert_governance_runs(keep_last=1, dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.total_runs_before == 3
    assert dry_run.kept_count == 1
    assert dry_run.candidate_count == 2
    assert dry_run.pruned_count == 0
    assert dry_run.malformed_candidate_count >= 1
    assert dry_run.malformed_dropped_count == 0

    applied = store.prune_maintenance_alert_governance_runs(keep_last=1, dry_run=False)
    assert applied.dry_run is False
    assert applied.total_runs_before == 3
    assert applied.kept_count == 1
    assert applied.candidate_count == 2
    assert applied.pruned_count == 2
    assert applied.malformed_candidate_count >= 1
    assert applied.malformed_dropped_count >= 1

    history = store.list_maintenance_alert_governance_runs(limit=20)
    assert history.total_records == 1
    assert len(history.records) == 1


def test_benchmark_store_summarizes_governance_runs(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-summary",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.70},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    _ = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="governance-summary-ok-1",
    )

    original_auto_archive = store.auto_archive_maintenance_alerts
    call_counter = {"value": 0}

    def flaky_auto_archive(*, dry_run: bool = True):
        call_counter["value"] += 1
        if call_counter["value"] == 1:
            raise RuntimeError("forced_governance_summary_failure")
        return original_auto_archive(dry_run=dry_run)

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", flaky_auto_archive)

    with pytest.raises(RuntimeError, match="forced_governance_summary_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="governance-summary-failed",
        )

    _ = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="governance-summary-ok-2",
    )

    summary = store.summarize_maintenance_alert_governance_runs(limit=20)
    assert summary.total_records == 3
    assert summary.window_record_count == 3
    assert summary.succeeded_count == 2
    assert summary.failed_count == 1
    assert summary.latest_run is not None
    assert summary.latest_failed_run is not None
    assert summary.latest_failed_run.status == "failed"


def test_benchmark_store_exports_governance_runs(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-export",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.69},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", "2")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", "365")
    monkeypatch.setenv("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", "100")

    for index in range(3):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key=f"governance-export-{index}",
        )

    export_first = store.export_maintenance_alert_governance_runs(limit=2)
    assert export_first.limit == 2
    assert export_first.summary.total_records == 3
    assert len(export_first.records) == 2
    assert export_first.has_more is True
    assert export_first.next_cursor

    export_second = store.export_maintenance_alert_governance_runs(limit=2, cursor=export_first.next_cursor)
    assert export_second.limit == 2
    assert len(export_second.records) == 1
    assert export_second.has_more is False
    assert export_second.cursor == export_first.next_cursor
    assert export_second.summary.total_records == 3


def test_benchmark_store_auto_prunes_governance_runs(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-auto-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.67},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)
    for index in range(4):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key=f"governance-auto-prune-{index}",
        )

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_TRIGGER_COUNT", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_KEEP_LAST", "1")

    dry_run = store.auto_prune_maintenance_alert_governance_runs(dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.should_prune is True
    assert dry_run.prune is not None
    assert dry_run.prune.dry_run is True
    assert dry_run.prune.candidate_count >= 3

    applied = store.auto_prune_maintenance_alert_governance_runs(dry_run=False)
    assert applied.dry_run is False
    assert applied.should_prune is True
    assert applied.prune is not None
    assert applied.prune.dry_run is False
    assert applied.prune.pruned_count >= 3

    history = store.list_maintenance_alert_governance_runs(limit=20)
    assert history.total_records <= 1

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_TRIGGER_COUNT", "100")
    not_needed = store.auto_prune_maintenance_alert_governance_runs(dry_run=True)
    assert not_needed.should_prune is False
    assert not_needed.prune is None
    assert not_needed.message == "below_threshold"


def test_benchmark_store_builds_governance_runs_digest(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-runs-digest",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.64},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    _ = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="governance-runs-digest-ok",
    )

    original_auto_archive = store.auto_archive_maintenance_alerts
    call_counter = {"value": 0}

    def flaky_auto_archive(*, dry_run: bool = True):
        call_counter["value"] += 1
        if call_counter["value"] == 1:
            raise RuntimeError("forced_governance_runs_digest_failure")
        return original_auto_archive(dry_run=dry_run)

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", flaky_auto_archive)
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_STALE_SECONDS", "3600")

    with pytest.raises(RuntimeError, match="forced_governance_runs_digest_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="governance-runs-digest-failed",
        )

    digest = store.build_maintenance_alert_governance_runs_digest(limit=20)
    assert digest.summary.total_records == 2
    assert digest.summary.failed_count == 1
    assert digest.summary.latest_run is not None
    assert digest.summary.latest_run.status == "failed"
    assert digest.is_stale is False
    assert digest.recommended_action == "retry_latest_failed_run"


def test_benchmark_store_auto_remediates_governance_runs(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-runs-auto-remediate",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.62},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    _ = store.run_maintenance_alert_governance(
        dry_run=True,
        alert_limit=20,
        archive_limit=20,
        idempotency_key="governance-runs-auto-remediate-ok",
    )

    original_auto_archive = store.auto_archive_maintenance_alerts
    call_counter = {"value": 0}

    def flaky_auto_archive(*, dry_run: bool = True):
        call_counter["value"] += 1
        if call_counter["value"] == 1:
            raise RuntimeError("forced_governance_runs_auto_remediate_failure")
        return original_auto_archive(dry_run=dry_run)

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", flaky_auto_archive)

    with pytest.raises(RuntimeError, match="forced_governance_runs_auto_remediate_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="governance-runs-auto-remediate-failed",
        )

    failed_history = store.list_maintenance_alert_governance_runs(limit=20)
    failed_run_id = failed_history.records[0].run_id
    assert failed_history.records[0].status == "failed"

    remediated = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert remediated.action == "retry_latest_failed_run"
    assert remediated.executed is True
    assert remediated.governance_run is not None
    assert remediated.governance_run.retry_run_id == failed_run_id
    assert remediated.digest_after.summary.total_records >= failed_history.total_records + 1


def test_benchmark_store_governance_retry_limit_escalates(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-retry-limit",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.60},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "3")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_retry_limit_failure")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    with pytest.raises(RuntimeError, match="forced_governance_retry_limit_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            idempotency_key="governance-retry-limit-seed",
        )

    first_failed = store.list_maintenance_alert_governance_runs(limit=20).records[0]
    assert first_failed.status == "failed"
    assert first_failed.attempt == 1

    with pytest.raises(RuntimeError, match="forced_governance_retry_limit_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            retry_run_id=first_failed.run_id,
            idempotency_key="governance-retry-limit-2",
        )

    second_history = store.list_maintenance_alert_governance_runs(limit=20)
    second_failed = max(second_history.records, key=lambda item: item.attempt)
    assert second_failed.status == "failed"
    assert second_failed.attempt == 2

    with pytest.raises(RuntimeError, match="forced_governance_retry_limit_failure"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            retry_run_id=second_failed.run_id,
            idempotency_key="governance-retry-limit-3",
        )

    third_history = store.list_maintenance_alert_governance_runs(limit=20)
    third_failed = max(third_history.records, key=lambda item: item.attempt)
    assert third_failed.status == "failed"
    assert third_failed.attempt == 3

    with pytest.raises(ValueError, match="retry_attempt_limit_exceeded"):
        _ = store.run_maintenance_alert_governance(
            dry_run=True,
            alert_limit=20,
            archive_limit=20,
            retry_run_id=third_failed.run_id,
            idempotency_key="governance-retry-limit-4",
        )

    history = store.list_maintenance_alert_governance_runs(limit=20)
    assert history.total_records == 3
    assert max(item.attempt for item in history.records) == 3

    digest = store.build_maintenance_alert_governance_runs_digest(limit=20)
    assert digest.recommended_action == "escalate_failed_run"
    assert digest.retry_max_attempts == 3
    assert digest.latest_failed_attempt == 3
    assert digest.retry_exhausted is True

    remediated = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert remediated.action == "escalate_failed_run"
    assert remediated.executed is False
    assert remediated.escalation_required is True
    assert remediated.escalation_reason == "retry_exhausted_at_attempt_3"
    assert remediated.message == "escalation_required"


def test_benchmark_store_governance_failure_streak_escalates(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-failure-streak",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.58},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_failure_streak")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_failure_streak"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-failure-streak-{index}",
            )

    digest = store.build_maintenance_alert_governance_runs_digest(limit=20)
    assert digest.summary.total_records == 2
    assert digest.summary.consecutive_failed_runs == 2
    assert digest.retry_max_attempts == 5
    assert digest.latest_failed_attempt == 1
    assert digest.retry_exhausted is False
    assert digest.escalation_failure_streak_limit == 2
    assert digest.failure_streak_exhausted is True
    assert digest.recommended_action == "escalate_failed_run"
    assert digest.message == "consecutive_failure_streak_exhausted"

    remediated = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert remediated.action == "escalate_failed_run"
    assert remediated.executed is False
    assert remediated.escalation_required is True
    assert remediated.escalation_reason == "consecutive_failures_2_reached_limit_2"
    assert remediated.escalation_event is not None
    assert remediated.escalation_event.source == "auto_remediate"
    assert remediated.message == "escalation_required"

    escalation_events = store.list_maintenance_alert_governance_escalations(limit=20)
    assert escalation_events.total_events == 1
    assert escalation_events.events[0].source == "auto_remediate"
    assert escalation_events.events[0].escalation_reason == "consecutive_failures_2_reached_limit_2"


def test_benchmark_store_emits_and_lists_governance_escalation_events(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-events",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.56},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_events")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_events"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-events-{index}",
            )

    emitted = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert emitted.emitted is True
    assert emitted.event is not None
    assert emitted.event.source == "manual_emit"
    assert emitted.event.recommended_action == "escalate_failed_run"
    assert emitted.event.failure_streak_exhausted is True
    assert emitted.message == "escalation_emitted"

    listed = store.list_maintenance_alert_governance_escalations(limit=20)
    assert listed.total_events == 1
    assert listed.events[0].event_id == emitted.event.event_id
    assert listed.events[0].source == "manual_emit"

    clean_store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store_clean.jsonl")
    no_escalation = clean_store.emit_maintenance_alert_governance_escalation(limit=20)
    assert no_escalation.emitted is False
    assert no_escalation.event is None
    assert no_escalation.message == "no_escalation_needed"


def test_benchmark_store_suppresses_duplicate_escalation_emit_with_cooldown(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-cooldown",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.55},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_EMIT_COOLDOWN_SECONDS", "3600")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_cooldown")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_cooldown"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-cooldown-{index}",
            )

    first = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert first.emitted is True
    assert first.suppressed is False
    assert first.event is not None

    second = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert second.emitted is False
    assert second.suppressed is True
    assert second.suppression_reason == "cooldown_active"
    assert second.suppressed_by_event_id == first.event.event_id
    assert second.cooldown_seconds == 3600
    assert second.message == "escalation_suppressed_cooldown"

    forced = store.emit_maintenance_alert_governance_escalation(limit=20, ignore_cooldown=True)
    assert forced.emitted is True
    assert forced.suppressed is False
    assert forced.event is not None
    assert forced.event.event_id != first.event.event_id


def test_benchmark_store_summarizes_and_exports_governance_escalations(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-export",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.54},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_export")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_export"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-export-{index}",
            )

    manual_emit = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert manual_emit.emitted is True
    auto_emit = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert auto_emit.escalation_event is not None

    summary = store.summarize_maintenance_alert_governance_escalations(limit=20)
    assert summary.total_events == 2
    assert summary.window_event_count == 2
    assert summary.manual_emit_count == 1
    assert summary.auto_remediate_count == 1
    assert summary.failure_streak_exhausted_count == 2
    assert summary.retry_exhausted_count == 0
    assert summary.latest_event is not None

    export_first = store.export_maintenance_alert_governance_escalations(limit=1)
    assert export_first.limit == 1
    assert export_first.summary.total_events == 2
    assert len(export_first.events) == 1
    assert export_first.has_more is True
    assert export_first.next_cursor

    export_second = store.export_maintenance_alert_governance_escalations(limit=1, cursor=export_first.next_cursor)
    assert export_second.limit == 1
    assert len(export_second.events) == 1
    assert export_second.has_more is False
    assert export_second.cursor == export_first.next_cursor


def test_benchmark_store_prunes_governance_escalation_events(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.55},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_prune")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_prune"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-prune-{index}",
            )

    manual_emit = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert manual_emit.emitted is True

    auto_emit = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert auto_emit.escalation_event is not None

    escalation_log = store.version_root / "_maintenance_alert_governance_escalations.jsonl"
    with escalation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    dry_run = store.prune_maintenance_alert_governance_escalations(keep_last=1, dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.total_events_before == 2
    assert dry_run.kept_count == 1
    assert dry_run.candidate_count == 1
    assert dry_run.pruned_count == 0
    assert dry_run.malformed_candidate_count >= 1
    assert dry_run.malformed_dropped_count == 0

    applied = store.prune_maintenance_alert_governance_escalations(keep_last=1, dry_run=False)
    assert applied.dry_run is False
    assert applied.total_events_before == 2
    assert applied.kept_count == 1
    assert applied.candidate_count == 1
    assert applied.pruned_count == 1
    assert applied.malformed_candidate_count >= 1
    assert applied.malformed_dropped_count >= 1

    listed = store.list_maintenance_alert_governance_escalations(limit=20)
    assert listed.total_events == 1
    assert len(listed.events) == 1


def test_benchmark_store_auto_prunes_governance_escalations(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-auto-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.51},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_auto_prune")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_auto_prune"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-auto-prune-{index}",
            )

    manual_emit = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert manual_emit.emitted is True
    auto_emit = store.auto_remediate_maintenance_alert_governance_runs(
        dry_run=False,
        limit=20,
        alert_limit=20,
        archive_limit=20,
    )
    assert auto_emit.escalation_event is not None

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT", "1")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_KEEP_LAST", "1")

    dry_run = store.auto_prune_maintenance_alert_governance_escalations(dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.should_prune is True
    assert dry_run.prune is not None
    assert dry_run.prune.dry_run is True
    assert dry_run.prune.candidate_count >= 1

    applied = store.auto_prune_maintenance_alert_governance_escalations(dry_run=False)
    assert applied.dry_run is False
    assert applied.should_prune is True
    assert applied.prune is not None
    assert applied.prune.dry_run is False
    assert applied.prune.pruned_count >= 1

    listed = store.list_maintenance_alert_governance_escalations(limit=20)
    assert listed.total_events <= 1

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT", "100")
    not_needed = store.auto_prune_maintenance_alert_governance_escalations(dry_run=True)
    assert not_needed.should_prune is False
    assert not_needed.prune is None
    assert not_needed.message == "below_threshold"


def test_benchmark_store_builds_governance_escalations_digest(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-digest",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.57},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_digest")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_digest"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-digest-{index}",
            )

    digest_before = store.build_maintenance_alert_governance_escalations_digest(limit=20)
    assert digest_before.summary.total_events == 0
    assert digest_before.run_digest.recommended_action == "escalate_failed_run"
    assert digest_before.recommended_action == "emit_escalation"
    assert digest_before.message == "escalation_needed"

    emitted = store.emit_maintenance_alert_governance_escalation(limit=20)
    assert emitted.emitted is True

    digest_after = store.build_maintenance_alert_governance_escalations_digest(limit=20)
    assert digest_after.summary.total_events == 1
    assert digest_after.recommended_action == "observe"
    assert digest_after.message == "ok"

    escalation_log = store.version_root / "_maintenance_alert_governance_escalations.jsonl"
    with escalation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    digest_malformed = store.build_maintenance_alert_governance_escalations_digest(limit=20)
    assert digest_malformed.recommended_action == "auto_prune_escalations"
    assert digest_malformed.message == "malformed_detected"


def test_benchmark_store_auto_remediates_governance_escalations(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-auto-remediate",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.56},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT", "100")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_auto_remediate")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_auto_remediate"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-auto-remediate-{index}",
            )

    dry_run_emit = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=True, limit=20)
    assert dry_run_emit.action == "emit_escalation"
    assert dry_run_emit.executed is False
    assert dry_run_emit.message == "dry_run"

    applied_emit = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=False, limit=20)
    assert applied_emit.action == "emit_escalation"
    assert applied_emit.executed is True
    assert applied_emit.emitted is True
    assert applied_emit.emitted_event is not None
    assert applied_emit.message == "remediated"

    escalation_log = store.version_root / "_maintenance_alert_governance_escalations.jsonl"
    with escalation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    applied_prune = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=False, limit=20)
    assert applied_prune.action == "auto_prune_escalations"
    assert applied_prune.executed is True
    assert applied_prune.pruned is True
    assert applied_prune.auto_prune is not None
    assert applied_prune.auto_prune.prune is not None
    assert applied_prune.auto_prune.prune.malformed_dropped_count >= 1
    assert applied_prune.message == "remediated"

    history = store.list_maintenance_alert_governance_escalation_remediations(limit=20)
    assert history.total_records == 3
    assert history.records[0].action == "auto_prune_escalations"
    assert history.records[0].pruned is True
    assert history.records[1].action == "emit_escalation"
    assert history.records[1].emitted is True
    assert history.records[2].dry_run is True

    remediation_log = store.version_root / "_maintenance_alert_governance_escalation_remediations.jsonl"
    with remediation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    summary = store.summarize_maintenance_alert_governance_escalation_remediations(limit=20)
    assert summary.total_records == 3
    assert summary.window_record_count == 3
    assert summary.malformed_line_count == 1
    assert summary.dry_run_count == 1
    assert summary.apply_count == 2
    assert summary.executed_count == 2
    assert summary.emitted_count == 1
    assert summary.pruned_count == 1
    assert summary.latest_record is not None
    assert summary.latest_record.action == "auto_prune_escalations"

    export_first = store.export_maintenance_alert_governance_escalation_remediations(limit=2)
    assert export_first.summary.total_records == 3
    assert export_first.summary.malformed_line_count == 1
    assert len(export_first.records) == 2
    assert export_first.has_more is True
    assert export_first.next_cursor

    export_second = store.export_maintenance_alert_governance_escalation_remediations(
        limit=2,
        cursor=export_first.next_cursor,
    )
    assert export_second.summary.total_records == 3
    assert export_second.summary.malformed_line_count == 1
    assert len(export_second.records) == 1
    assert export_second.has_more is False
    assert export_second.cursor == export_first.next_cursor

    prune_dry_run = store.prune_maintenance_alert_governance_escalation_remediations(keep_last=1, dry_run=True)
    assert prune_dry_run.dry_run is True
    assert prune_dry_run.total_records_before == 3
    assert prune_dry_run.kept_count == 1
    assert prune_dry_run.candidate_count == 2
    assert prune_dry_run.pruned_count == 0
    assert prune_dry_run.malformed_candidate_count == 1
    assert prune_dry_run.malformed_dropped_count == 0

    prune_apply = store.prune_maintenance_alert_governance_escalation_remediations(keep_last=1, dry_run=False)
    assert prune_apply.dry_run is False
    assert prune_apply.total_records_before == 3
    assert prune_apply.kept_count == 1
    assert prune_apply.pruned_count == 2
    assert prune_apply.malformed_candidate_count == 1
    assert prune_apply.malformed_dropped_count == 1
    assert len(prune_apply.pruned_run_ids) == 2

    remaining = store.list_maintenance_alert_governance_escalation_remediations(limit=20)
    assert remaining.total_records == 1
    assert remaining.malformed_line_count == 0
    assert len(remaining.records) == 1
    assert remaining.records[0].action == "auto_prune_escalations"


def test_benchmark_store_auto_prunes_governance_escalation_remediations(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-auto-remediation-auto-prune",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.56},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT", "100")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_auto_remediation_auto_prune")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_auto_remediation_auto_prune"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-auto-remediation-auto-prune-{index}",
            )

    _ = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=True, limit=20)
    _ = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=False, limit=20)

    remediation_log = store.version_root / "_maintenance_alert_governance_escalation_remediations.jsonl"
    with remediation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST", "1")

    dry_run = store.auto_prune_maintenance_alert_governance_escalation_remediations(dry_run=True)
    assert dry_run.dry_run is True
    assert dry_run.should_prune is True
    assert dry_run.prune is not None
    assert dry_run.prune.dry_run is True
    assert dry_run.prune.total_records_before == 2
    assert dry_run.prune.malformed_candidate_count >= 1
    assert dry_run.prune.malformed_dropped_count == 0

    applied = store.auto_prune_maintenance_alert_governance_escalation_remediations(dry_run=False)
    assert applied.dry_run is False
    assert applied.should_prune is True
    assert applied.prune is not None
    assert applied.prune.dry_run is False
    assert applied.prune.total_records_before == 2
    assert applied.prune.kept_count == 1
    assert applied.prune.pruned_count == 1
    assert applied.prune.malformed_candidate_count >= 1
    assert applied.prune.malformed_dropped_count >= 1

    listed = store.list_maintenance_alert_governance_escalation_remediations(limit=20)
    assert listed.total_records == 1
    assert listed.malformed_line_count == 0

    not_needed = store.auto_prune_maintenance_alert_governance_escalation_remediations(dry_run=True)
    assert not_needed.should_prune is False
    assert not_needed.prune is None
    assert not_needed.message == "below_threshold"


def test_benchmark_store_builds_governance_escalation_remediations_digest(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    no_records = store.build_maintenance_alert_governance_escalation_remediations_digest(limit=20)
    assert no_records.summary.total_records == 0
    assert no_records.recommended_action == "run_auto_remediate_escalations"
    assert no_records.message == "no_records"
    assert no_records.is_stale is True
    assert no_records.latest_record_age_seconds == -1.0

    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-remediation-digest",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.56},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST", "1")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_remediation_digest")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_remediation_digest"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-remediation-digest-{index}",
            )

    _ = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=True, limit=20)
    _ = store.auto_remediate_maintenance_alert_governance_escalations(dry_run=False, limit=20)

    digest_ok = store.build_maintenance_alert_governance_escalation_remediations_digest(limit=20)
    assert digest_ok.summary.total_records == 2
    assert digest_ok.summary.malformed_line_count == 0
    assert digest_ok.recommended_action == "observe"
    assert digest_ok.message == "ok"
    assert digest_ok.latest_record_age_seconds >= 0.0
    assert digest_ok.is_stale is False

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "1")
    digest_above_threshold = store.build_maintenance_alert_governance_escalation_remediations_digest(limit=20)
    assert digest_above_threshold.recommended_action == "auto_prune_remediations"
    assert digest_above_threshold.message == "above_prune_threshold"

    remediation_log = store.version_root / "_maintenance_alert_governance_escalation_remediations.jsonl"
    with remediation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    digest_malformed = store.build_maintenance_alert_governance_escalation_remediations_digest(limit=20)
    assert digest_malformed.recommended_action == "auto_prune_remediations"
    assert digest_malformed.message == "malformed_detected"
    assert digest_malformed.summary.malformed_line_count >= 1


def test_benchmark_store_auto_remediates_governance_escalation_remediations(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-remediation-auto-remediate",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.56},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST", "1")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_remediation_auto_remediate")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_remediation_auto_remediate"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-remediation-auto-remediate-{index}",
            )

    applied_escalations = store.auto_remediate_maintenance_alert_governance_escalation_remediations(
        dry_run=False,
        limit=20,
    )
    assert applied_escalations.action == "run_auto_remediate_escalations"
    assert applied_escalations.executed is True
    assert applied_escalations.remediated_escalations is True
    assert applied_escalations.pruned_remediation_history is False
    assert applied_escalations.escalation_auto_remediate is not None
    assert applied_escalations.escalation_auto_remediate.executed is True
    assert applied_escalations.remediation_auto_prune is None
    assert applied_escalations.message == "remediated"

    dry_run_after_apply = store.auto_remediate_maintenance_alert_governance_escalation_remediations(
        dry_run=True,
        limit=20,
    )
    assert dry_run_after_apply.executed is False
    assert dry_run_after_apply.message == "dry_run"

    remediation_log = store.version_root / "_maintenance_alert_governance_escalation_remediations.jsonl"
    with remediation_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    applied_prune = store.auto_remediate_maintenance_alert_governance_escalation_remediations(
        dry_run=False,
        limit=20,
    )
    assert applied_prune.action == "auto_prune_remediations"
    assert applied_prune.executed is True
    assert applied_prune.remediated_escalations is False
    assert applied_prune.pruned_remediation_history is True
    assert applied_prune.escalation_auto_remediate is None
    assert applied_prune.remediation_auto_prune is not None
    assert applied_prune.remediation_auto_prune.prune is not None
    assert applied_prune.remediation_auto_prune.prune.malformed_dropped_count >= 1
    assert applied_prune.message == "remediated"

    run_history = store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=20)
    assert run_history.total_records == 3
    assert run_history.records[0].action == "auto_prune_remediations"
    assert run_history.records[0].pruned_remediation_history is True
    assert any(item.dry_run for item in run_history.records)
    assert any(item.action == "run_auto_remediate_escalations" for item in run_history.records)
    assert any(item.remediated_escalations for item in run_history.records)

    run_history_log = store.version_root / "_maintenance_alert_governance_escalation_remediation_auto_remediate_runs.jsonl"
    with run_history_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    summary = store.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=20)
    assert summary.total_records == 3
    assert summary.window_record_count == 3
    assert summary.malformed_line_count == 1
    assert summary.dry_run_count == 1
    assert summary.apply_count == 2
    assert summary.executed_count == 2
    assert summary.remediated_escalations_count == 1
    assert summary.pruned_remediation_history_count == 1
    assert summary.latest_record is not None
    assert summary.latest_record.action == "auto_prune_remediations"

    export_first = store.export_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=2)
    assert export_first.summary.total_records == 3
    assert export_first.summary.malformed_line_count == 1
    assert len(export_first.records) == 2
    assert export_first.has_more is True
    assert export_first.next_cursor

    export_second = store.export_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        limit=2,
        cursor=export_first.next_cursor,
    )
    assert export_second.summary.total_records == 3
    assert export_second.summary.malformed_line_count == 1
    assert len(export_second.records) == 1
    assert export_second.has_more is False
    assert export_second.cursor == export_first.next_cursor

    prune_dry_run = store.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        keep_last=1,
        dry_run=True,
    )
    assert prune_dry_run.dry_run is True
    assert prune_dry_run.total_records_before == 3
    assert prune_dry_run.kept_count == 1
    assert prune_dry_run.candidate_count == 2
    assert prune_dry_run.pruned_count == 0
    assert prune_dry_run.malformed_candidate_count == 1
    assert prune_dry_run.malformed_dropped_count == 0

    prune_apply = store.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        keep_last=1,
        dry_run=False,
    )
    assert prune_apply.dry_run is False
    assert prune_apply.total_records_before == 3
    assert prune_apply.kept_count == 1
    assert prune_apply.pruned_count == 2
    assert prune_apply.malformed_candidate_count == 1
    assert prune_apply.malformed_dropped_count == 1
    assert len(prune_apply.pruned_run_ids) == 2

    remaining_runs = store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=20)
    assert remaining_runs.total_records == 1
    assert remaining_runs.malformed_line_count == 0
    assert len(remaining_runs.records) == 1

    with run_history_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST", "1")

    auto_prune_dry_run = store.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        dry_run=True
    )
    assert auto_prune_dry_run.dry_run is True
    assert auto_prune_dry_run.should_prune is True
    assert auto_prune_dry_run.prune is not None
    assert auto_prune_dry_run.prune.dry_run is True
    assert auto_prune_dry_run.prune.total_records_before == 1
    assert auto_prune_dry_run.prune.malformed_candidate_count >= 1
    assert auto_prune_dry_run.prune.malformed_dropped_count == 0

    auto_prune_apply = store.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        dry_run=False
    )
    assert auto_prune_apply.dry_run is False
    assert auto_prune_apply.should_prune is True
    assert auto_prune_apply.prune is not None
    assert auto_prune_apply.prune.dry_run is False
    assert auto_prune_apply.prune.total_records_before == 1
    assert auto_prune_apply.prune.kept_count == 1
    assert auto_prune_apply.prune.pruned_count == 0
    assert auto_prune_apply.prune.malformed_candidate_count >= 1
    assert auto_prune_apply.prune.malformed_dropped_count >= 1

    post_auto_prune_runs = store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=20)
    assert post_auto_prune_runs.total_records == 1
    assert post_auto_prune_runs.malformed_line_count == 0

    auto_prune_not_needed = store.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        dry_run=True
    )
    assert auto_prune_not_needed.should_prune is False
    assert auto_prune_not_needed.prune is None
    assert auto_prune_not_needed.message == "below_threshold"


def test_benchmark_store_builds_governance_escalation_remediation_auto_remediate_runs_digest(monkeypatch, tmp_path) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    no_records = store.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(limit=20)
    assert no_records.summary.total_records == 0
    assert no_records.recommended_action == "run_auto_remediation_orchestrator"
    assert no_records.message == "no_records"
    assert no_records.is_stale is True
    assert no_records.latest_record_age_seconds == -1.0

    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-remediation-orchestrator-runs-digest",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.57},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST", "1")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_remediation_orchestrator_runs_digest")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(RuntimeError, match="forced_governance_escalation_remediation_orchestrator_runs_digest"):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-remediation-orchestrator-runs-digest-{index}",
            )

    _ = store.auto_remediate_maintenance_alert_governance_escalation_remediations(dry_run=True, limit=20)
    _ = store.auto_remediate_maintenance_alert_governance_escalation_remediations(dry_run=False, limit=20)

    digest_ok = store.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(limit=20)
    assert digest_ok.summary.total_records == 2
    assert digest_ok.summary.malformed_line_count == 0
    assert digest_ok.recommended_action == "observe"
    assert digest_ok.message == "ok"
    assert digest_ok.latest_record_age_seconds >= 0.0
    assert digest_ok.is_stale is False

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT", "1")
    digest_above_threshold = store.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(
        limit=20
    )
    assert digest_above_threshold.recommended_action == "auto_prune_runs"
    assert digest_above_threshold.message == "above_prune_threshold"

    run_history_log = store.version_root / "_maintenance_alert_governance_escalation_remediation_auto_remediate_runs.jsonl"
    with run_history_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    digest_malformed = store.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(limit=20)
    assert digest_malformed.recommended_action == "auto_prune_runs"
    assert digest_malformed.message == "malformed_detected"
    assert digest_malformed.summary.malformed_line_count >= 1


def test_benchmark_store_auto_remediates_governance_escalation_remediation_auto_remediate_runs(
    monkeypatch,
    tmp_path,
) -> None:
    store = V7BenchmarkStore(path=tmp_path / "v7_benchmark_store.jsonl")
    _ = store.ingest(
        BenchmarkIngestRequest(
            book_id="book-alert-governance-escalation-remediation-orchestrator-runs-auto-remediate",
            channel="fantasy",
            genre_track="fast",
            sample_payload={"nqm_mean": 0.58},
        )
    )
    for _ in range(4):
        _ = store.emit_maintenance_alert(limit=20)

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", "5")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK", "2")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST", "1")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_STALE_SECONDS", "3600")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT", "100")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST", "1")

    def always_fail_auto_archive(*, dry_run: bool = True):
        raise RuntimeError("forced_governance_escalation_remediation_orchestrator_runs_auto_remediate")

    monkeypatch.setattr(store, "auto_archive_maintenance_alerts", always_fail_auto_archive)

    for index in range(2):
        with pytest.raises(
            RuntimeError,
            match="forced_governance_escalation_remediation_orchestrator_runs_auto_remediate",
        ):
            _ = store.run_maintenance_alert_governance(
                dry_run=True,
                alert_limit=20,
                archive_limit=20,
                idempotency_key=f"governance-escalation-remediation-orchestrator-runs-auto-remediate-{index}",
            )

    apply_orchestrator = store.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        dry_run=False,
        limit=20,
    )
    assert apply_orchestrator.action == "run_auto_remediation_orchestrator"
    assert apply_orchestrator.executed is True
    assert apply_orchestrator.remediated_orchestrator is True
    assert apply_orchestrator.pruned_run_history is False
    assert apply_orchestrator.orchestrator_auto_remediate is not None
    assert apply_orchestrator.orchestrator_auto_remediate.executed is True
    assert apply_orchestrator.run_history_auto_prune is None
    assert apply_orchestrator.digest_before.summary.total_records == 0
    assert apply_orchestrator.digest_after.summary.total_records >= 1
    assert apply_orchestrator.message == "remediated"

    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT", "0")
    monkeypatch.setenv("AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST", "0")

    apply_prune = store.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        dry_run=False,
        limit=20,
    )
    assert apply_prune.action == "auto_prune_runs"
    assert apply_prune.executed is True
    assert apply_prune.remediated_orchestrator is False
    assert apply_prune.pruned_run_history is True
    assert apply_prune.orchestrator_auto_remediate is None
    assert apply_prune.run_history_auto_prune is not None
    assert apply_prune.run_history_auto_prune.prune is not None
    assert apply_prune.run_history_auto_prune.prune.pruned_count >= 1
    assert apply_prune.message == "remediated"

    post_prune_history = store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=20)
    assert post_prune_history.total_records == 0

    orchestrator_run_history = (
        store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(limit=20)
    )
    assert orchestrator_run_history.total_records == 2
    assert orchestrator_run_history.malformed_line_count == 0
    assert orchestrator_run_history.records[0].action == "auto_prune_runs"
    assert orchestrator_run_history.records[0].pruned_run_history is True
    assert orchestrator_run_history.records[1].action == "run_auto_remediation_orchestrator"
    assert orchestrator_run_history.records[1].remediated_orchestrator is True

    orchestrator_run_history_log = (
        store.version_root
        / "_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs.jsonl"
    )
    with orchestrator_run_history_log.open("a", encoding="utf-8") as handle:
        handle.write("{bad-json\n")

    orchestrator_run_history_after_malformed = (
        store.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(limit=20)
    )
    assert orchestrator_run_history_after_malformed.total_records == 2
    assert orchestrator_run_history_after_malformed.malformed_line_count >= 1

    orchestrator_run_history_summary = (
        store.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=20
        )
    )
    assert orchestrator_run_history_summary.total_records == 2
    assert orchestrator_run_history_summary.window_record_count == 2
    assert orchestrator_run_history_summary.malformed_line_count >= 1
    assert orchestrator_run_history_summary.dry_run_count == 0
    assert orchestrator_run_history_summary.apply_count == 2
    assert orchestrator_run_history_summary.executed_count == 2
    assert orchestrator_run_history_summary.remediated_orchestrator_count == 1
    assert orchestrator_run_history_summary.pruned_run_history_count == 1
    assert orchestrator_run_history_summary.latest_record is not None
    assert orchestrator_run_history_summary.latest_record.action == "auto_prune_runs"

    orchestrator_run_history_export_first = (
        store.export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=1
        )
    )
    assert orchestrator_run_history_export_first.summary.total_records == 2
    assert orchestrator_run_history_export_first.summary.malformed_line_count >= 1
    assert len(orchestrator_run_history_export_first.records) == 1
    assert orchestrator_run_history_export_first.has_more is True
    assert orchestrator_run_history_export_first.next_cursor

    orchestrator_run_history_export_second = (
        store.export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=1,
            cursor=orchestrator_run_history_export_first.next_cursor,
        )
    )
    assert orchestrator_run_history_export_second.summary.total_records == 2
    assert orchestrator_run_history_export_second.summary.malformed_line_count >= 1
    assert len(orchestrator_run_history_export_second.records) == 1
    assert orchestrator_run_history_export_second.has_more is False
    assert (
        orchestrator_run_history_export_second.cursor
        == orchestrator_run_history_export_first.next_cursor
    )


def test_decision_controller_returns_override_route_when_confirmed() -> None:
    controller = DecisionFeedbackController()
    vector = NQMVector(metrics={key: 0.5 for key in NQMVector().metrics}, composite=0.4)
    market_state = NarrativeMarketState(
        project_state=NovelProjectState(project_id="demo"),
        benchmark_state=BenchmarkParameterSet(high_threshold=0.78, low_threshold=0.52, opening_gate_t8=0.6),
        decision_state=DecisionState(),
        story_state={"chapter_index": 1},
    )
    result = controller.decide(
        DecisionRequest(
            market_state=market_state,
            vector=vector,
            ohlcv=NarrativeMetricOHLCV(open=0.5, high=0.5, low=0.4, close=0.4, volume=100),
            override_confirmed=True,
        )
    )
    assert result.decision.route_id == "R-OVERRIDE"
