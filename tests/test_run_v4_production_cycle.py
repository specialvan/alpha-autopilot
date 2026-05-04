from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_v4_production_cycle.py"


def load_run_v4_production_cycle_module():
    spec = importlib.util.spec_from_file_location("run_v4_production_cycle", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_resolve_task_returns_repo_scoped_commands() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_v4_cycle = load_run_v4_production_cycle_module()

    task = run_v4_cycle.resolve_task("T01", repo_root=repo_root)

    assert task.task_id == "T01"
    assert task.title == "Production Cycle Baseline Gate"
    assert len(task.commands) == 3
    assert [command.name for command in task.commands] == [
        "layer_definition_guard",
        "v4_module_and_api",
        "layered_v4_gate",
    ]
    assert all(command.cwd == repo_root for command in task.commands)
    assert task.commands[0].argv == (sys.executable, "-m", "pytest", "tests/test_run_layered_tests.py", "-q")
    assert task.commands[2].argv == (sys.executable, "scripts/run_layered_tests.py", "v4")


def test_resolve_t02_task_contains_dual_path_guards() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_v4_cycle = load_run_v4_production_cycle_module()

    task = run_v4_cycle.resolve_task("T02", repo_root=repo_root)

    assert task.task_id == "T02"
    assert task.title == "Dual-Path Mandatory Gate"
    assert len(task.commands) == 3
    assert [command.name for command in task.commands] == [
        "dual_path_module_guard",
        "dual_path_api_guard",
        "layered_v4_regression_gate",
    ]
    assert any("test_v4_bridge_result_contains_v3_context_and_qc_summary" in arg for arg in task.commands[0].argv)
    assert any("test_v4_bridge_can_be_disabled_for_safe_fallback" in arg for arg in task.commands[0].argv)
    assert task.commands[1].argv[:3] == (sys.executable, "-m", "pytest")
    assert "test_v4_plot_preview_endpoint_returns_payload_with_candidates_and_qc" in task.commands[1].argv[3]
    assert "test_v4_plot_preview_endpoint_can_disable_v4_for_rollback" in task.commands[1].argv[4]
    assert task.commands[2].argv == (sys.executable, "scripts/run_layered_tests.py", "v4")


def test_resolve_t03_task_contains_runtime_metric_guards() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_v4_cycle = load_run_v4_production_cycle_module()

    task = run_v4_cycle.resolve_task("T03", repo_root=repo_root)

    assert task.task_id == "T03"
    assert task.title == "Runtime Metrics And Threshold Gate"
    assert len(task.commands) == 3
    assert [command.name for command in task.commands] == [
        "runtime_metrics_module_guard",
        "runtime_metrics_api_guard",
        "layered_v4_regression_gate",
    ]
    assert any("test_v4_observability_snapshot_reports_runtime_threshold_alerts" in arg for arg in task.commands[0].argv)
    assert task.commands[1].argv[:3] == (sys.executable, "-m", "pytest")
    assert "test_v4_observability_snapshot_endpoint_emits_runtime_threshold_alerts" in task.commands[1].argv[4]


def test_resolve_t04_task_contains_remote_alert_channel_guards() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_v4_cycle = load_run_v4_production_cycle_module()

    task = run_v4_cycle.resolve_task("T04", repo_root=repo_root)

    assert task.task_id == "T04"
    assert task.title == "Remote Alert Channel Gate"
    assert len(task.commands) == 3
    assert [command.name for command in task.commands] == [
        "remote_alert_module_guard",
        "remote_alert_api_guard",
        "layered_v4_regression_gate",
    ]
    assert any("test_v4_alert_channel_routes_remote_targets_with_oncall_validation" in arg for arg in task.commands[0].argv)
    assert any("test_v4_alert_channel_remote_failure_falls_back_to_local_sink" in arg for arg in task.commands[0].argv)
    assert task.commands[1].argv[:3] == (sys.executable, "-m", "pytest")
    assert "test_v4_observability_alert_route_endpoint_routes_remote_targets" in task.commands[1].argv[3]
    assert "test_v4_observability_alert_route_endpoint_applies_cooldown" in task.commands[1].argv[4]


def test_run_task_executes_commands_in_order_and_writes_report(tmp_path, monkeypatch) -> None:
    run_v4_cycle = load_run_v4_production_cycle_module()
    repo_root = tmp_path
    output = tmp_path / "report.md"
    calls: list[str] = []

    def fake_run_command(command):  # noqa: ANN001
        calls.append(command.name)
        return subprocess.CompletedProcess(command.argv, 0, stdout=f"{command.name} ok\n", stderr="")

    monkeypatch.setattr(run_v4_cycle, "_run_command", fake_run_command)

    exit_code, report_path = run_v4_cycle.run_task("T01", repo_root=repo_root, output=output)

    assert exit_code == 0
    assert report_path == output
    assert calls == ["layer_definition_guard", "v4_module_and_api", "layered_v4_gate"]
    assert report_path.exists()

    report = report_path.read_text(encoding="utf-8")
    assert "# V4 Production Cycle Report" in report
    assert "- task_id: `T01`" in report
    assert "### layer_definition_guard (PASS)" in report
    assert "### layered_v4_gate (PASS)" in report


def test_run_t02_task_executes_dual_path_commands_in_order(tmp_path, monkeypatch) -> None:
    run_v4_cycle = load_run_v4_production_cycle_module()
    repo_root = tmp_path
    output = tmp_path / "report-t02.md"
    calls: list[str] = []

    def fake_run_command(command):  # noqa: ANN001
        calls.append(command.name)
        return subprocess.CompletedProcess(command.argv, 0, stdout=f"{command.name} ok\n", stderr="")

    monkeypatch.setattr(run_v4_cycle, "_run_command", fake_run_command)

    exit_code, report_path = run_v4_cycle.run_task("T02", repo_root=repo_root, output=output)

    assert exit_code == 0
    assert report_path == output
    assert calls == [
        "dual_path_module_guard",
        "dual_path_api_guard",
        "layered_v4_regression_gate",
    ]
    report = report_path.read_text(encoding="utf-8")
    assert "- task_id: `T02`" in report
    assert "### dual_path_module_guard (PASS)" in report
    assert "### layered_v4_regression_gate (PASS)" in report


def test_run_t03_task_executes_runtime_metric_commands_in_order(tmp_path, monkeypatch) -> None:
    run_v4_cycle = load_run_v4_production_cycle_module()
    repo_root = tmp_path
    output = tmp_path / "report-t03.md"
    calls: list[str] = []

    def fake_run_command(command):  # noqa: ANN001
        calls.append(command.name)
        return subprocess.CompletedProcess(command.argv, 0, stdout=f"{command.name} ok\n", stderr="")

    monkeypatch.setattr(run_v4_cycle, "_run_command", fake_run_command)

    exit_code, report_path = run_v4_cycle.run_task("T03", repo_root=repo_root, output=output)

    assert exit_code == 0
    assert report_path == output
    assert calls == [
        "runtime_metrics_module_guard",
        "runtime_metrics_api_guard",
        "layered_v4_regression_gate",
    ]
    report = report_path.read_text(encoding="utf-8")
    assert "- task_id: `T03`" in report
    assert "### runtime_metrics_module_guard (PASS)" in report
    assert "### layered_v4_regression_gate (PASS)" in report


def test_run_t04_task_executes_remote_alert_commands_in_order(tmp_path, monkeypatch) -> None:
    run_v4_cycle = load_run_v4_production_cycle_module()
    repo_root = tmp_path
    output = tmp_path / "report-t04.md"
    calls: list[str] = []

    def fake_run_command(command):  # noqa: ANN001
        calls.append(command.name)
        return subprocess.CompletedProcess(command.argv, 0, stdout=f"{command.name} ok\n", stderr="")

    monkeypatch.setattr(run_v4_cycle, "_run_command", fake_run_command)

    exit_code, report_path = run_v4_cycle.run_task("T04", repo_root=repo_root, output=output)

    assert exit_code == 0
    assert report_path == output
    assert calls == [
        "remote_alert_module_guard",
        "remote_alert_api_guard",
        "layered_v4_regression_gate",
    ]
    report = report_path.read_text(encoding="utf-8")
    assert "- task_id: `T04`" in report
    assert "### remote_alert_module_guard (PASS)" in report
    assert "### layered_v4_regression_gate (PASS)" in report


def test_resolve_task_rejects_unknown_task() -> None:
    run_v4_cycle = load_run_v4_production_cycle_module()

    with pytest.raises(SystemExit, match="Unknown task: T99"):
        run_v4_cycle.resolve_task("T99", repo_root=Path(r"D:\workspace\alpha-autopilot"))
