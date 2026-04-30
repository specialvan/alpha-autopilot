from __future__ import annotations

from backend.app.services.narrative_v6.observability import (
    V6RuntimeMetricsStore,
    build_v6_observability_snapshot,
)


def test_v6_observability_snapshot_reports_empty_runtime_window(tmp_path) -> None:
    store = V6RuntimeMetricsStore(path=tmp_path / "runtime.jsonl")

    snapshot = build_v6_observability_snapshot(runtime_store=store, limit=200)

    assert snapshot["enabled"] is False
    assert snapshot["runtimeRows"] == 0
    assert snapshot["latencyP95Ms"] == 0.0
    assert snapshot["errorRate"] == 0.0
    assert snapshot["fallbackRate"] == 0.0
    assert snapshot["unifiedEnvelope"]["schemaVersion"] == "obs-envelope.v1"
    assert snapshot["unifiedEnvelope"]["layer"] == "v6"
    assert snapshot["unifiedEnvelope"]["keyMetrics"]["runtimeRows"] == 0
    alert_codes = {item["code"] for item in snapshot["alerts"]}
    assert "no-runtime-data" in alert_codes


def test_v6_observability_snapshot_aggregates_route_metrics_and_alerts(tmp_path, monkeypatch) -> None:
    store = V6RuntimeMetricsStore(path=tmp_path / "runtime.jsonl")

    monkeypatch.setattr("backend.app.services.narrative_v6.observability.settings.v6_observability_latency_p95_ms_threshold", 10.0)
    monkeypatch.setattr("backend.app.services.narrative_v6.observability.settings.v6_observability_error_rate_threshold", 0.1)
    monkeypatch.setattr("backend.app.services.narrative_v6.observability.settings.v6_observability_fallback_rate_threshold", 0.2)

    for index in range(10):
        if index in {2, 6, 9}:
            status = "error"
            fallback_reason = ""
        elif index in {4, 8}:
            status = "fallback"
            fallback_reason = "no-valid-winner-path"
        else:
            status = "ok"
            fallback_reason = ""
        store.append_metric(
            route="/api/narrative/v6/simulations/parallel",
            status=status,
            latency_ms=20 + index,
            simulation_id=f"sim-{index}",
            path_count=3,
            failed_path_count=1 if status != "ok" else 0,
            winner_path_id="" if status == "fallback" else f"sim-{index}-path-1",
            fallback_reason=fallback_reason,
            error_type="RuntimeError" if status == "error" else "",
            risk_flags=["path_generation_failed"] if status != "ok" else [],
            http_status=500 if status == "error" else 200,
        )

    snapshot = build_v6_observability_snapshot(runtime_store=store, limit=50)

    assert snapshot["enabled"] is True
    assert snapshot["runtimeRows"] == 10
    assert snapshot["latencyP95Ms"] >= 20.0
    assert snapshot["errorRate"] == 0.3
    assert snapshot["fallbackRate"] == 0.2
    assert snapshot["routes"]
    route_row = snapshot["routes"][0]
    assert route_row["route"] == "/api/narrative/v6/simulations/parallel"
    assert route_row["sampleCount"] == 10
    assert route_row["errorRate"] == 0.3
    assert route_row["fallbackRate"] == 0.2
    envelope = snapshot["unifiedEnvelope"]
    assert envelope["schemaVersion"] == "obs-envelope.v1"
    assert envelope["layer"] == "v6"
    assert envelope["keyMetrics"]["runtimeRows"] == 10
    assert envelope["keyMetrics"]["errorRate"] == 0.3

    alert_codes = {item["code"] for item in snapshot["alerts"]}
    assert "runtime-latency-p95-high" in alert_codes
    assert "runtime-error-rate-high" in alert_codes
    assert "runtime-fallback-rate-high" in alert_codes
