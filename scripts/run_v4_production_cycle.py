from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXE = sys.executable
PYTEST_CMD = (PYTHON_EXE, "-m", "pytest")


@dataclass(frozen=True)
class TaskCommand:
    name: str
    cwd: Path
    argv: tuple[str, ...]

    def subprocess_argv(self) -> tuple[str, ...]:
        if os.name == "nt" and self.argv and self.argv[0] == "npm":
            return ("npm.cmd", *self.argv[1:])
        return self.argv

    def display(self) -> str:
        return " ".join(self.argv)


@dataclass(frozen=True)
class ProductionTask:
    task_id: str
    title: str
    goal: str
    commands: tuple[TaskCommand, ...]


def _task_definitions(repo_root: Path) -> dict[str, ProductionTask]:
    return {
        "T01": ProductionTask(
            task_id="T01",
            title="Production Cycle Baseline Gate",
            goal="固化 V4 单任务生产周期的基础门禁与验收报告出口",
            commands=(
                TaskCommand(
                    name="layer_definition_guard",
                    cwd=repo_root,
                    argv=(*PYTEST_CMD, "tests/test_run_layered_tests.py", "-q"),
                ),
                TaskCommand(
                    name="v4_module_and_api",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "tests/test_alpha_autopilot_v4_modules.py",
                        "backend/tests/test_narrative_v4_api.py",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="layered_v4_gate",
                    cwd=repo_root,
                    argv=(PYTHON_EXE, "scripts/run_layered_tests.py", "v4"),
                ),
            ),
        ),
        "T02": ProductionTask(
            task_id="T02",
            title="Dual-Path Mandatory Gate",
            goal="将 v4_enabled=true/false 双路径显式纳入生产周期门禁并固定验收出口",
            commands=(
                TaskCommand(
                    name="dual_path_module_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_bridge_result_contains_v3_context_and_qc_summary",
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_bridge_can_be_disabled_for_safe_fallback",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="dual_path_api_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "backend/tests/test_narrative_v4_api.py::test_v4_plot_preview_endpoint_returns_payload_with_candidates_and_qc",
                        "backend/tests/test_narrative_v4_api.py::test_v4_plot_preview_endpoint_can_disable_v4_for_rollback",
                        "backend/tests/test_narrative_v4_api.py::test_v4_workbench_preview_endpoint_returns_structured_preview",
                        "backend/tests/test_narrative_v4_api.py::test_v4_workbench_preview_endpoint_returns_fallback_when_state_missing",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="layered_v4_regression_gate",
                    cwd=repo_root,
                    argv=(PYTHON_EXE, "scripts/run_layered_tests.py", "v4"),
                ),
            ),
        ),
        "T03": ProductionTask(
            task_id="T03",
            title="Runtime Metrics And Threshold Gate",
            goal="定义并落地 P95 延迟/错误率/fallback 比例结构化指标与阈值告警门禁",
            commands=(
                TaskCommand(
                    name="runtime_metrics_module_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_observability_snapshot_reports_trend_and_alerts",
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_observability_snapshot_reports_runtime_threshold_alerts",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="runtime_metrics_api_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "backend/tests/test_narrative_v4_api.py::test_v4_observability_snapshot_endpoint_returns_snapshot_and_routing",
                        "backend/tests/test_narrative_v4_api.py::test_v4_observability_snapshot_endpoint_emits_runtime_threshold_alerts",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="layered_v4_regression_gate",
                    cwd=repo_root,
                    argv=(PYTHON_EXE, "scripts/run_layered_tests.py", "v4"),
                ),
            ),
        ),
        "T04": ProductionTask(
            task_id="T04",
            title="Remote Alert Channel Gate",
            goal="将本地告警通道扩展为 IM/Webhook 远端路由并补齐值班校验门禁",
            commands=(
                TaskCommand(
                    name="remote_alert_module_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_alert_channel_routes_remote_targets_with_oncall_validation",
                        "tests/test_alpha_autopilot_v4_modules.py::test_v4_alert_channel_remote_failure_falls_back_to_local_sink",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="remote_alert_api_guard",
                    cwd=repo_root,
                    argv=(
                        *PYTEST_CMD,
                        "backend/tests/test_narrative_v4_api.py::test_v4_observability_alert_route_endpoint_routes_remote_targets",
                        "backend/tests/test_narrative_v4_api.py::test_v4_observability_alert_route_endpoint_applies_cooldown",
                        "-q",
                    ),
                ),
                TaskCommand(
                    name="layered_v4_regression_gate",
                    cwd=repo_root,
                    argv=(PYTHON_EXE, "scripts/run_layered_tests.py", "v4"),
                ),
            ),
        ),
    }


def resolve_task(task_id: str, repo_root: Path | None = None) -> ProductionTask:
    root = (repo_root or REPO_ROOT).resolve()
    task = _task_definitions(root).get(task_id)
    if task is None:
        raise SystemExit(f"Unknown task: {task_id}")
    return task


def _run_command(command: TaskCommand) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command.subprocess_argv(),
        cwd=command.cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_report_path(repo_root: Path, task_id: str, started_at: datetime) -> Path:
    timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    return (
        repo_root
        / "artifacts"
        / "production_cycles"
        / task_id.lower()
        / f"v4-{task_id.lower()}-{timestamp}.md"
    )


def _write_report(
    report_path: Path,
    task: ProductionTask,
    results: list[subprocess.CompletedProcess[str]],
    *,
    started_at: datetime,
    ended_at: datetime,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    duration_seconds = (ended_at - started_at).total_seconds()

    lines: list[str] = []
    lines.append("# V4 Production Cycle Report")
    lines.append("")
    lines.append(f"- task_id: `{task.task_id}`")
    lines.append(f"- task_title: `{task.title}`")
    lines.append(f"- goal: {task.goal}")
    lines.append(f"- started_at_utc: {_iso_utc(started_at)}")
    lines.append(f"- ended_at_utc: {_iso_utc(ended_at)}")
    lines.append(f"- duration_seconds: {duration_seconds:.2f}")
    lines.append("")
    lines.append("## Command Results")
    lines.append("")

    for command, result in zip(task.commands, results, strict=True):
        status = "PASS" if result.returncode == 0 else "FAIL"
        lines.append(f"### {command.name} ({status})")
        lines.append("")
        lines.append(f"- cwd: `{command.cwd}`")
        lines.append(f"- command: `{command.display()}`")
        lines.append(f"- exit_code: `{result.returncode}`")
        lines.append("")
        lines.append("```text")
        combined_output = (result.stdout or "") + (result.stderr or "")
        lines.append(combined_output.rstrip())
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_task(
    task_id: str,
    *,
    repo_root: Path | None = None,
    output: Path | None = None,
    stream=None,
) -> tuple[int, Path]:
    root = (repo_root or REPO_ROOT).resolve()
    task = resolve_task(task_id, repo_root=root)
    started_at = datetime.now(timezone.utc)

    if output is None:
        report_path = _default_report_path(root, task.task_id, started_at)
    elif output.is_absolute():
        report_path = output
    else:
        report_path = (root / output).resolve()

    out = stream if stream is not None else sys.stdout
    results: list[subprocess.CompletedProcess[str]] = []
    exit_code = 0

    for command in task.commands:
        print(f"[cycle:{task.task_id}] {command.name}: {command.display()} (cwd={command.cwd})", file=out)
        result = _run_command(command)
        results.append(result)
        if result.returncode != 0 and exit_code == 0:
            exit_code = result.returncode

    ended_at = datetime.now(timezone.utc)
    _write_report(report_path, task, results, started_at=started_at, ended_at=ended_at)
    print(f"[cycle:{task.task_id}] report: {report_path}", file=out)
    return exit_code, report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a single V4 production-cycle task and write an acceptance report.")
    parser.add_argument("task", choices=tuple(sorted(_task_definitions(REPO_ROOT))), help="Task ID to execute.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root path. Defaults to script parent repository.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional report output path. Defaults to artifacts/production_cycles/<task>/v4-<task>-<timestamp>.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code, _report = run_task(
        args.task,
        repo_root=args.repo_root,
        output=args.output,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
