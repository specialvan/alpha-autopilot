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
class AcceptanceCommand:
    name: str
    cwd: Path
    argv: tuple[str, ...]

    def subprocess_argv(self) -> tuple[str, ...]:
        if os.name == "nt" and self.argv and self.argv[0] == "npm":
            return ("npm.cmd", *self.argv[1:])
        return self.argv

    def display(self) -> str:
        return " ".join(self.argv)


def _commands(repo_root: Path) -> tuple[AcceptanceCommand, ...]:
    return (
        AcceptanceCommand(
            name="v8_targeted_gate",
            cwd=repo_root,
            argv=(
                *PYTEST_CMD,
                "tests/test_narrative_v8_schemas.py",
                "tests/test_narrative_v8_knife_library.py",
                "tests/test_narrative_v8_selection.py",
                "tests/test_narrative_v8_flavor.py",
                "tests/test_narrative_v8_ledger.py",
                "tests/test_narrative_v8_controller.py",
                "tests/test_narrative_v8_integration.py",
                "tests/test_run_layered_tests.py",
                "tests/test_run_v8_acceptance_review.py",
                "-q",
            ),
        ),
        AcceptanceCommand(
            name="layered_v8_gate",
            cwd=repo_root,
            argv=(PYTHON_EXE, "scripts/run_layered_tests.py", "v8"),
        ),
    )


def _run_command(command: AcceptanceCommand) -> subprocess.CompletedProcess[str]:
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


def _default_report_path(repo_root: Path, started_at: datetime) -> Path:
    timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    return repo_root / "artifacts" / "acceptance" / f"v8-acceptance-{timestamp}.md"


def _write_report(
    report_path: Path,
    commands: tuple[AcceptanceCommand, ...],
    results: list[subprocess.CompletedProcess[str]],
    *,
    started_at: datetime,
    ended_at: datetime,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    duration_seconds = (ended_at - started_at).total_seconds()
    lines: list[str] = []
    lines.append("# V8 Acceptance Review Report")
    lines.append("")
    lines.append(f"- started_at_utc: {_iso_utc(started_at)}")
    lines.append(f"- ended_at_utc: {_iso_utc(ended_at)}")
    lines.append(f"- duration_seconds: {duration_seconds:.2f}")
    lines.append("")
    lines.append("## Command Results")
    lines.append("")

    for command, result in zip(commands, results, strict=True):
        status = "PASS" if result.returncode == 0 else "FAIL"
        lines.append(f"### {command.name} ({status})")
        lines.append("")
        lines.append(f"- cwd: `{command.cwd}`")
        lines.append(f"- command: `{command.display()}`")
        lines.append(f"- exit_code: `{result.returncode}`")
        lines.append("")
        lines.append("```text")
        lines.append(((result.stdout or "") + (result.stderr or "")).rstrip())
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def run(
    *,
    repo_root: Path | None = None,
    output: Path | None = None,
    stream=None,
) -> tuple[int, Path]:
    root = (repo_root or REPO_ROOT).resolve()
    started_at = datetime.now(timezone.utc)
    commands = _commands(root)
    report_path = (
        _default_report_path(root, started_at)
        if output is None
        else (output if output.is_absolute() else (root / output).resolve())
    )

    out = stream if stream is not None else sys.stdout
    results: list[subprocess.CompletedProcess[str]] = []
    exit_code = 0
    for command in commands:
        print(f"[v8-acceptance] {command.name}: {command.display()} (cwd={command.cwd})", file=out)
        result = _run_command(command)
        results.append(result)
        if result.returncode != 0 and exit_code == 0:
            exit_code = result.returncode

    ended_at = datetime.now(timezone.utc)
    _write_report(report_path, commands, results, started_at=started_at, ended_at=ended_at)
    print(f"[v8-acceptance] report: {report_path}", file=out)
    return exit_code, report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run V8 acceptance gates and write a markdown report.")
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
        help="Optional markdown report output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code, _report_path = run(repo_root=args.repo_root, output=args.output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
