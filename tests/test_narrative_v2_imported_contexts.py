from __future__ import annotations

import json
from pathlib import Path

from backend.app.services.narrative.history_service import HistoryService
from backend.app.services.narrative_v2.imported_contexts import (
    build_workbench_contexts_from_plotpilot_report,
    load_latest_plotpilot_report_contexts,
    load_imported_workbench_contexts,
)
from backend.app.services.narrative_v2.online_report_contexts import (
    load_online_plotpilot_report_contexts,
    probe_online_plotpilot_report_contexts,
)
from backend.app.services.narrative_v2.workbench_service import NarrativeV2WorkbenchService


def test_build_workbench_contexts_from_plotpilot_report_creates_stageful_contexts() -> None:
    payload = {
        "model": "gpt-5.4",
        "results": [
            {
                "chapter": 1,
                "title": "black_jade_awakens",
                "success": True,
                "chars": 3354,
                "preview": "A young cultivator escapes into a sword valley.",
            },
            {
                "chapter": 6,
                "title": "secret_realm_opening",
                "success": True,
                "chars": 3167,
                "preview": "The prince blocks the road to the black market.",
            },
            {
                "chapter": 10,
                "title": "battle_of_broken_road",
                "success": True,
                "chars": 3265,
                "preview": "The tide tower archive opens under siege.",
            },
        ],
    }

    contexts = build_workbench_contexts_from_plotpilot_report(payload)

    assert [item["chapterNumber"] for item in contexts] == [1, 6, 10]
    assert contexts[0]["stage"] == "opening"
    assert contexts[1]["stage"] == "mid_late"
    assert contexts[2]["stage"] == "late"
    assert "gpt-5.4" in contexts[0]["summary"]


def test_build_workbench_contexts_from_plotpilot_report_includes_v3_quality_metadata() -> None:
    payload = {
        "model": "gpt-5.4",
        "results": [
            {
                "chapter": 2,
                "title": "guest_from_medicine_valley",
                "success": True,
                "chars": 3167,
                "preview": "The prince blocks the road to the black market.",
            }
        ],
    }

    quality_records = [
        {
            "chapter_number": 2,
            "title": "guest from medicine valley",
            "admission": "provisional",
            "primary_function": "information-reveal",
            "style_dna": {
                "pace": "brisk",
                "dialogue_reliance": "medium",
                "emotional_directness": "balanced",
            },
            "checkpoints": [
                {
                    "name": "chapter-function-fit",
                    "status": "pass",
                    "evidence": "Primary function resolved cleanly.",
                    "implication": "Suitable for downstream use.",
                }
            ],
            "workbench_context": {
                "notes": "Derived from 1 paragraphs with information-reveal."
            },
        }
    ]

    contexts = build_workbench_contexts_from_plotpilot_report(payload, quality_records=quality_records)

    assert contexts[0]["admission"] == "provisional"
    assert contexts[0]["primary_function"] == "information-reveal"
    assert contexts[0]["style_dna"]["pace"] == "brisk"
    assert contexts[0]["checkpoints"][0]["name"] == "chapter-function-fit"
    assert "information-reveal" in contexts[0]["quality_notes"]


def test_workbench_service_prefers_imported_context_file(tmp_path) -> None:
    imported_path = tmp_path / "workbench_contexts.json"
    imported_path.write_text(
        json.dumps(
            {
                "contexts": [
                    {
                        "id": "plotpilot-chapter-01",
                        "chapterNumber": 1,
                        "title": "black_jade_awakens",
                        "stage": "opening",
                        "summary": "Imported PlotPilot fixture",
                        "state": {
                            "chapter_index": 1,
                            "stage": "opening",
                            "mainline_progress": 0.12,
                            "sideplot_progress": 0.04,
                            "conflict_intensity": 0.62,
                            "emotional_temperature": 0.48,
                            "pacing_speed": 0.58,
                            "foreshadowing_load": 0.22,
                            "payoff_pressure": 0.14,
                            "characters": {},
                            "tags": ["plotpilot"],
                        },
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=imported_path,
    )

    result = service.list_contexts()

    assert result["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert result["contexts"][0]["summary"] == "Imported PlotPilot fixture"


def test_load_imported_workbench_contexts_returns_none_for_invalid_root_json(tmp_path) -> None:
    imported_path = tmp_path / "workbench_contexts.json"
    imported_path.write_text("{bad-json", encoding="utf-8")

    loaded = load_imported_workbench_contexts(imported_path)

    assert loaded is None


def test_load_imported_workbench_contexts_returns_none_when_contexts_payload_has_no_dict_items(
    tmp_path,
) -> None:
    imported_path = tmp_path / "workbench_contexts.json"
    imported_path.write_text(
        json.dumps({"contexts": ["not-a-dict", 3, None]}, ensure_ascii=False),
        encoding="utf-8",
    )

    loaded = load_imported_workbench_contexts(imported_path)

    assert loaded is None


def test_load_latest_plotpilot_report_contexts_builds_real_chapter_contract(tmp_path) -> None:
    report_path = tmp_path / "raw" / "model_switch_tests" / "run-01" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "model": "gpt-5.4",
                "results": [
                    {
                        "chapter": 1,
                        "title": "black_jade_awakens",
                        "success": True,
                        "chars": 3100,
                        "preview": "A wounded cultivator escapes into the sword valley.",
                    },
                    {
                        "chapter": 2,
                        "title": "guest_from_medicine_valley",
                        "success": True,
                        "chars": 3200,
                        "preview": "A healer arrives and forces a fragile alliance.",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    loaded = load_latest_plotpilot_report_contexts(
        tmp_path / "raw" / "model_switch_tests",
        preferred_model="gpt-5.4",
    )

    assert loaded is not None
    assert loaded["source"] == "plotpilot_report"
    assert loaded["context_contract"] == "real_chapter_context_v2"
    assert loaded["preferred_model"] == "gpt-5.4"
    assert loaded["resolved_model"] == "gpt-5.4"
    assert len(loaded["contexts"]) == 2
    assert loaded["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert loaded["contexts"][1]["compare_baseline"]["baseline_chapter_number"] == 1
    assert "mainline_progress" in loaded["contexts"][1]["compare_baseline"]["delta"]
    assert loaded["source_diagnostics"]["local_report"]["status"] == "ok"


def test_workbench_service_prefers_real_chapter_report_when_available(tmp_path) -> None:
    plotpilot_root = tmp_path / "plotpilot"
    report_path = plotpilot_root / "raw" / "model_switch_tests" / "run-01" / "report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "model": "gpt-5.4",
                "results": [
                    {
                        "chapter": 1,
                        "title": "black_jade_awakens",
                        "success": True,
                        "chars": 3100,
                        "preview": "A wounded cultivator escapes into the sword valley.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=plotpilot_root / "workbench_contexts.json",
    )

    result = service.list_contexts()

    assert result["source"] == "plotpilot_report"
    assert result["context_contract"] == "real_chapter_context_v2"
    assert result["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert result["contexts"][0]["v4_preview"]["enabled"] is True


def test_load_latest_plotpilot_report_contexts_prefers_manifest_arbitrated_run(tmp_path) -> None:
    report_root = tmp_path / "raw" / "model_switch_tests"
    run_a = report_root / "run-a"
    run_b = report_root / "run-b" / "round_01"
    run_a.mkdir(parents=True, exist_ok=True)
    run_b.mkdir(parents=True, exist_ok=True)

    (run_a / "report.json").write_text(
        json.dumps(
            {
                "timestamp": "2026-04-21T16:13:33.767178",
                "model": "gpt-4.1",
                "success": 10,
                "total": 10,
                "results": [
                    {
                        "chapter": 1,
                        "title": "run_a_chapter",
                        "success": True,
                        "chars": 3000,
                        "preview": "run-a chapter preview",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_b / "report.json").write_text(
        json.dumps(
            {
                "timestamp": "2026-04-21T15:59:00.123456",
                "model": "gpt-5.4",
                "success": 7,
                "total": 10,
                "results": [
                    {
                        "chapter": 1,
                        "title": "run_b_chapter",
                        "success": True,
                        "chars": 3100,
                        "preview": "run-b chapter preview",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    manifest_root = tmp_path / "raw" / "decomposition" / "v3_20260421_220604"
    manifest_root.mkdir(parents=True, exist_ok=True)
    (manifest_root / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "v3_20260421_220604",
                "generated_at": "2026-04-21T22:06:04.523082",
                "input": {
                    "run_dirs": [
                        str(run_b.resolve()),
                    ]
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    loaded = load_latest_plotpilot_report_contexts(
        report_root,
        manifest_root=tmp_path / "raw" / "decomposition",
        preferred_model="gpt-5.4",
    )

    assert loaded is not None
    assert loaded["source"] == "plotpilot_report"
    assert loaded["context_contract"] == "real_chapter_context_v2"
    assert loaded["report_path"].endswith("run-b\\round_01\\report.json")
    assert loaded["resolved_model"] == "gpt-5.4"
    assert loaded["run_id"] == "v3_20260421_220604"
    assert loaded["manifest_path"].endswith("manifest.json")
    assert loaded["contexts"][0]["title"] == "run b chapter"
    assert loaded["source_diagnostics"]["local_report"]["status"] == "ok"


def test_load_online_plotpilot_report_contexts_builds_real_chapter_contract(monkeypatch) -> None:
    def fake_fetch_with_meta(url: str, *, api_key: str | None, timeout_seconds: float):
        assert "model=gpt-5.4" in url
        assert api_key == "api-key-01"
        return (
            {
                "run_id": "online-run-01",
                "manifest": {
                    "path": "https://plotpilot.example/api/runs/online-run-01/manifest.json",
                },
                "report": {
                    "timestamp": "2026-04-25T05:00:00Z",
                    "model": "gpt-5.4",
                    "success": 1,
                    "total": 1,
                    "results": [
                        {
                            "chapter": 1,
                            "title": "api_chapter_opening",
                            "success": True,
                            "chars": 3200,
                            "preview": "Online API chapter preview for workbench context.",
                        }
                    ],
                },
            },
            {
                "status": "ok",
            },
        )

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.online_report_contexts._fetch_json_payload_with_meta",
        fake_fetch_with_meta,
    )
    loaded = load_online_plotpilot_report_contexts(
        api_url="https://plotpilot.example/api/latest-report",
        api_key="api-key-01",
        preferred_model="gpt-5.4",
    )

    assert loaded is not None
    assert loaded["source"] == "plotpilot_api"
    assert loaded["context_contract"] == "real_chapter_context_v2"
    assert loaded["run_id"] == "online-run-01"
    assert loaded["manifest_path"].endswith("/manifest.json")
    assert loaded["report_url"].startswith("https://plotpilot.example")
    assert loaded["preferred_model"] == "gpt-5.4"
    assert loaded["resolved_model"] == "gpt-5.4"
    assert loaded["report_success_rate"] == 1.0
    assert loaded["contexts"][0]["id"] == "plotpilot-chapter-01"
    assert loaded["contexts"][0]["title"] == "api chapter opening"
    assert loaded["source_diagnostics"]["online_report"]["status"] == "ok"


def test_workbench_service_prefers_online_report_api_when_configured(tmp_path, monkeypatch) -> None:
    def fake_probe_online(**kwargs):
        return {
            "payload": {
                "source": "plotpilot_api",
                "context_contract": "real_chapter_context_v2",
                "report_url": "https://plotpilot.example/api/latest-report?model=gpt-5.4",
                "run_id": "online-run-02",
                "contexts": [
                    {
                        "id": "plotpilot-chapter-03",
                        "chapterNumber": 3,
                        "title": "online chapter three",
                        "stage": "middle",
                        "summary": "Online report context",
                        "state": {
                            "chapter_index": 3,
                            "stage": "middle",
                            "mainline_progress": 0.31,
                            "sideplot_progress": 0.24,
                            "conflict_intensity": 0.66,
                            "emotional_temperature": 0.52,
                            "pacing_speed": 0.49,
                            "foreshadowing_load": 0.29,
                            "payoff_pressure": 0.25,
                            "characters": {},
                            "tags": ["plotpilot_import", "middle"],
                        },
                    }
                ],
            },
            "diagnostics": {"status": "ok", "attempted": True},
        }

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.workbench_service.probe_online_plotpilot_report_contexts",
        fake_probe_online,
    )

    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=tmp_path / "plotpilot" / "workbench_contexts.json",
        online_report_api_url="https://plotpilot.example/api/latest-report",
        online_report_api_key="api-key-02",
    )

    result = service.list_contexts()

    assert result["source"] == "plotpilot_api"
    assert result["context_contract"] == "real_chapter_context_v2"
    assert result["run_id"] == "online-run-02"
    assert result["source_diagnostics"]["online_report"]["status"] == "ok"
    assert result["contexts"][0]["id"] == "plotpilot-chapter-03"
    assert result["contexts"][0]["v4_preview"]["enabled"] is True


def test_probe_online_plotpilot_report_contexts_emits_diagnostics_when_disabled() -> None:
    result = probe_online_plotpilot_report_contexts(
        api_url=None,
        preferred_model="gpt-5.4",
    )
    assert result["payload"] is None
    diagnostics = result["diagnostics"]
    assert diagnostics["enabled"] is False
    assert diagnostics["status"] == "disabled"


def test_probe_online_plotpilot_report_contexts_emits_invalid_payload_status(monkeypatch) -> None:
    def fake_fetch_with_meta(url: str, *, api_key: str | None, timeout_seconds: float):
        return (
            {
                "report": {
                    "model": "gpt-5.4",
                    "results": "not-a-list",
                }
            },
            {"status": "ok"},
        )

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.online_report_contexts._fetch_json_payload_with_meta",
        fake_fetch_with_meta,
    )
    result = probe_online_plotpilot_report_contexts(
        api_url="https://plotpilot.example/api/latest-report",
        api_key="api-key-03",
        preferred_model="gpt-5.4",
    )
    assert result["payload"] is None
    diagnostics = result["diagnostics"]
    assert diagnostics["attempted"] is True
    assert diagnostics["status"] == "invalid-report-payload"


def test_probe_online_plotpilot_report_contexts_retries_transient_http_error(monkeypatch) -> None:
    call_count = {"value": 0}

    def fake_fetch_with_meta(url: str, *, api_key: str | None, timeout_seconds: float):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return (
                None,
                {
                    "status": "http-error",
                    "http_status": 503,
                    "error_type": "HTTPError",
                    "error_message": "HTTP Error 503: Service Unavailable",
                },
            )
        return (
            {
                "run_id": "online-run-retry-01",
                "report": {
                    "timestamp": "2026-04-25T05:00:00Z",
                    "model": "gpt-5.4",
                    "success": 1,
                    "total": 1,
                    "results": [
                        {
                            "chapter": 1,
                            "title": "retry_success_chapter",
                            "success": True,
                            "chars": 3100,
                            "preview": "Recovered after retry.",
                        }
                    ],
                },
            },
            {"status": "ok"},
        )

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.online_report_contexts._fetch_json_payload_with_meta",
        fake_fetch_with_meta,
    )
    sleeps: list[float] = []
    result = probe_online_plotpilot_report_contexts(
        api_url="https://plotpilot.example/api/latest-report",
        api_key="api-key-retry",
        preferred_model="gpt-5.4",
        max_attempts=3,
        backoff_seconds=0.1,
        sleep_fn=lambda seconds: sleeps.append(seconds),
    )

    payload = result["payload"]
    diagnostics = result["diagnostics"]
    assert isinstance(payload, dict)
    assert payload["source"] == "plotpilot_api"
    assert call_count["value"] == 2
    assert diagnostics["status"] == "ok"
    assert diagnostics["attempts_count"] == 2
    assert diagnostics["retried"] is True
    assert diagnostics["retry_exhausted"] is False
    assert diagnostics["attempt_history"][0]["status"] == "http-error"
    assert diagnostics["attempt_history"][1]["status"] == "ok"
    assert sleeps == [0.1]


def test_probe_online_plotpilot_report_contexts_does_not_retry_invalid_json(monkeypatch) -> None:
    call_count = {"value": 0}

    def fake_fetch_with_meta(url: str, *, api_key: str | None, timeout_seconds: float):
        call_count["value"] += 1
        return (
            None,
            {
                "status": "invalid-json",
                "error_type": "JSONDecodeError",
                "error_message": "Invalid JSON payload",
            },
        )

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.online_report_contexts._fetch_json_payload_with_meta",
        fake_fetch_with_meta,
    )
    sleeps: list[float] = []
    result = probe_online_plotpilot_report_contexts(
        api_url="https://plotpilot.example/api/latest-report",
        api_key="api-key-invalid-json",
        preferred_model="gpt-5.4",
        max_attempts=4,
        backoff_seconds=0.2,
        sleep_fn=lambda seconds: sleeps.append(seconds),
    )

    assert result["payload"] is None
    diagnostics = result["diagnostics"]
    assert diagnostics["status"] == "invalid-json"
    assert diagnostics["attempts_count"] == 1
    assert diagnostics["retried"] is False
    assert diagnostics["retry_exhausted"] is False
    assert call_count["value"] == 1
    assert sleeps == []


def test_workbench_service_passes_online_retry_config_to_probe(tmp_path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_probe_online(**kwargs):
        captured.update(kwargs)
        return {
            "payload": None,
            "diagnostics": {
                "status": "network-error",
                "attempted": True,
            },
        }

    monkeypatch.setattr(
        "backend.app.services.narrative_v2.workbench_service.probe_online_plotpilot_report_contexts",
        fake_probe_online,
    )
    service = NarrativeV2WorkbenchService(
        history_service=HistoryService(),
        imported_context_path=tmp_path / "plotpilot" / "workbench_contexts.json",
        online_report_api_url="https://plotpilot.example/api/latest-report",
        online_report_api_key="api-key-probe",
        online_report_timeout_seconds=9.5,
        online_report_max_attempts=5,
        online_report_backoff_seconds=0.35,
        preferred_model="gpt-5.4",
    )

    result = service.list_contexts(online_only=True)

    assert result["fallback_reason"] == "online-report-unavailable"
    assert captured["timeout_seconds"] == 9.5
    assert captured["max_attempts"] == 5
    assert captured["backoff_seconds"] == 0.35
    assert captured["preferred_model"] == "gpt-5.4"
