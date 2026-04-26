from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _resolve_commands(repo_root: Path) -> list[AcceptanceCommand]:
    return [
        AcceptanceCommand(
            name="layered_all",
            cwd=repo_root,
            argv=("python", "scripts/run_layered_tests.py"),
        ),
        AcceptanceCommand(
            name="workbench_contract",
            cwd=repo_root,
            argv=(
                "pytest",
                "tests/test_narrative_v2_workbench_context_api.py",
                "tests/test_narrative_v2_imported_contexts.py",
                "tests/test_narrative_v2_workbench_quality_enrichment.py",
                "-q",
            ),
        ),
        AcceptanceCommand(
            name="frontend_build",
            cwd=repo_root / "ui-react",
            argv=("npm", "run", "build"),
        ),
    ]


def _write_report(
    report_path: Path,
    commands: list[AcceptanceCommand],
    results: list[subprocess.CompletedProcess[str]],
    *,
    started_at: datetime,
    ended_at: datetime,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    total_seconds = (ended_at - started_at).total_seconds()
    lines: list[str] = []
    lines.append("# Claude Acceptance Run Report")
    lines.append("")
    lines.append(f"- started_at_utc: {_iso_utc(started_at)}")
    lines.append(f"- ended_at_utc: {_iso_utc(ended_at)}")
    lines.append(f"- duration_seconds: {total_seconds:.2f}")
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
        combined_output = (result.stdout or "") + (result.stderr or "")
        lines.append(combined_output.rstrip())
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Claude acceptance commands and write a report.")
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
        help="Optional report output path. Defaults to artifacts/acceptance/claude-acceptance-<timestamp>.md",
    )
    return parser


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    started_at = datetime.now(timezone.utc)
    timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    output = args.output
    if output is None:
        output = repo_root / "artifacts" / "acceptance" / f"claude-acceptance-{timestamp}.md"
    elif not output.is_absolute():
        output = (repo_root / output).resolve()

    commands = _resolve_commands(repo_root)
    results: list[subprocess.CompletedProcess[str]] = []

    exit_code = 0
    for command in commands:
        print(f"[acceptance] {command.name}: {command.display()} (cwd={command.cwd})")
        result = _run_command(command)
        results.append(result)
        if result.returncode != 0 and exit_code == 0:
            exit_code = result.returncode

    ended_at = datetime.now(timezone.utc)
    _write_report(output, commands, results, started_at=started_at, ended_at=ended_at)
    print(f"[acceptance] report: {output}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
