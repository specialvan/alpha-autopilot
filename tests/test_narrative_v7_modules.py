from __future__ import annotations

import json

from backend.app.services.narrative_v7.antipattern_registry import AntiPatternRegistry
from backend.app.services.narrative_v7.benchmark_store import V7BenchmarkStore
from backend.app.services.narrative_v7.decision_controller import DecisionFeedbackController
from backend.app.services.narrative_v7.decision_rules import DecisionRuleSet
from backend.app.services.narrative_v7.deadlock_router import DeadlockRouter
from backend.app.services.narrative_v7.expectation_debt import ExpectationDebtManager
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
