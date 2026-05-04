from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_v8_acceptance_review.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_v8_acceptance_review", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_v8_acceptance_review_commands_cover_required_gates() -> None:
    module = load_module()
    commands = module._commands(Path(r"D:\workspace\alpha-autopilot"))
    joined = [" ".join(item.argv) for item in commands]
    argv_sets = [set(item.argv) for item in commands]

    assert any("tests/test_narrative_v8_schemas.py" in row for row in joined)
    assert any("tests/test_narrative_v8_controller.py" in row for row in joined)
    assert any("tests/test_narrative_v8_integration.py" in row for row in joined)
    assert any({"scripts/run_layered_tests.py", "v8"}.issubset(argv_set) for argv_set in argv_sets)


def test_v8_acceptance_review_run_writes_report(monkeypatch, tmp_path) -> None:
    module = load_module()

    def fake_run(command):  # noqa: ANN001
        return subprocess.CompletedProcess(command.argv, 0, stdout=f"ok:{command.name}", stderr="")

    monkeypatch.setattr(module, "_run_command", fake_run)

    exit_code, report_path = module.run(
        repo_root=tmp_path,
        output=tmp_path / "acceptance_report.md",
    )

    assert exit_code == 0
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "V8 Acceptance Review Report" in report_text
    assert "v8_targeted_gate" in report_text
