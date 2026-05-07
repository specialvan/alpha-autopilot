from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_layered_tests.py"


def load_run_layered_tests_module():
    spec = importlib.util.spec_from_file_location("run_layered_tests", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_resolve_layers_returns_path_based_commands_in_order() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_layered_tests = load_run_layered_tests_module()

    commands = run_layered_tests.resolve_layers(["core", "frontend"], repo_root=repo_root)

    assert [command.name for command in commands] == ["core", "frontend"]
    assert commands[0].cwd == repo_root
    assert commands[0].argv[:3] == (sys.executable, "-m", "pytest")
    assert "tests/test_alpha_autopilot_v2_domain.py" in commands[0].argv
    assert commands[1].cwd == repo_root / "ui-react"
    assert commands[1].argv[:3] == ("npm", "test", "--")
    assert "src/pages/V2WorkbenchPage.test.tsx" in commands[1].argv
    assert "src/features/v2Workbench/characterInterviewPanel.test.tsx" in commands[1].argv


def test_run_layers_prints_and_executes_selected_commands(monkeypatch, capsys) -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    calls: list[tuple[tuple[str, ...], Path]] = []
    run_layered_tests = load_run_layered_tests_module()

    def fake_run(argv, cwd=None, check=False):  # noqa: ANN001
        calls.append((tuple(argv), Path(cwd)))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(run_layered_tests.subprocess, "run", fake_run)

    exit_code = run_layered_tests.run_layers(["quality"], repo_root=repo_root)

    assert exit_code == 0
    assert calls == [
        (
            (
                sys.executable,
                "-m",
                "pytest",
                "tests/test_alpha_autopilot_v2_golden_cases.py",
                "tests/test_alpha_autopilot_v2_rule_fixtures_runtime.py",
                "tests/test_alpha_autopilot_v2_validation_assets.py",
                "tests/test_alpha_autopilot_v2_validation_ledger.py",
                "tests/test_alpha_autopilot_v3_build_script.py",
                "tests/test_alpha_autopilot_v3_retention_metrics.py",
                "tests/test_alpha_autopilot_v3_qc_report.py",
                "tests/test_narrative_training_service_projection.py",
            ),
            repo_root,
        )
    ]

    output = capsys.readouterr().out
    assert "quality:" in output
    assert "-m pytest tests/test_alpha_autopilot_v2_golden_cases.py" in output


def test_run_layers_uses_windows_npm_cmd_when_needed(monkeypatch) -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    calls: list[tuple[tuple[str, ...], Path]] = []
    run_layered_tests = load_run_layered_tests_module()

    def fake_run(argv, cwd=None, check=False):  # noqa: ANN001
        calls.append((tuple(argv), Path(cwd)))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(run_layered_tests.subprocess, "run", fake_run)

    exit_code = run_layered_tests.run_layers(["frontend"], repo_root=repo_root)

    assert exit_code == 0
    assert calls
    expected_exec = "npm.cmd" if run_layered_tests.os.name == "nt" else "npm"
    assert calls[0][0][0] == expected_exec
    assert calls[0][0][1:3] == ("test", "--")
    assert calls[0][1] == repo_root / "ui-react"


def test_resolve_layers_supports_v7_gate() -> None:
    repo_root = Path(r"D:\workspace\alpha-autopilot")
    run_layered_tests = load_run_layered_tests_module()

    commands = run_layered_tests.resolve_layers(["v7"], repo_root=repo_root)

    assert [command.name for command in commands] == ["v7"]
    assert commands[0].cwd == repo_root
    assert commands[0].argv[:3] == (sys.executable, "-m", "pytest")
    assert "tests/test_narrative_v7_modules.py" in commands[0].argv
    assert "tests/test_narrative_v7_api.py" in commands[0].argv


def test_resolve_layers_rejects_unknown_layer_name() -> None:
    run_layered_tests = load_run_layered_tests_module()
    with pytest.raises(SystemExit, match="Unknown layer: missing"):
        run_layered_tests.resolve_layers(["missing"], repo_root=Path(r"D:\workspace\alpha-autopilot"))


def test_layer_definitions_include_required_v3_gate_tests() -> None:
    run_layered_tests = load_run_layered_tests_module()
    layer_tests = {
        test_path
        for layer in run_layered_tests.LAYER_DEFINITIONS.values()
        for test_path in layer.argv
        if test_path.startswith("tests/") or test_path.startswith("backend/tests/")
    }

    assert "tests/test_alpha_autopilot_v3_build_script.py" in layer_tests
    assert "tests/test_alpha_autopilot_v3_retention_metrics.py" in layer_tests
    assert "tests/test_alpha_autopilot_v3_qc_report.py" in layer_tests
    assert "tests/test_narrative_v2_decision_contract.py" in layer_tests
    assert "tests/test_narrative_v2_workbench_context_api.py" in layer_tests
    assert "tests/test_narrative_v2_workbench_quality_enrichment.py" in layer_tests
    assert "tests/test_alpha_autopilot_v4_modules.py" in layer_tests
    assert "backend/tests/test_narrative_v4_api.py" in layer_tests
    assert "tests/test_narrative_seed_extractor.py" in layer_tests
    assert "tests/test_character_parameterizer.py" in layer_tests
    assert "tests/test_parallel_plot_simulation.py" in layer_tests
    assert "tests/test_emergent_conflict_probe.py" in layer_tests
    assert "tests/test_event_injection_checkpoint.py" in layer_tests
    assert "tests/test_character_interview.py" in layer_tests
    assert "tests/test_group_memory_layer.py" in layer_tests
    assert "tests/test_graph_rag_retrieval.py" in layer_tests
    assert "tests/test_v6_graph_memory_store.py" in layer_tests
    assert "tests/test_v6_state_store.py" in layer_tests
    assert "tests/test_narrative_v6_observability.py" in layer_tests
    assert "tests/test_narrative_v6_api.py" in layer_tests
    assert "tests/test_run_v6_acceptance_review.py" in layer_tests
    assert "tests/test_narrative_v7_modules.py" in layer_tests
    assert "tests/test_narrative_v7_api.py" in layer_tests
    assert "tests/test_narrative_v8_schemas.py" in layer_tests
    assert "tests/test_narrative_v8_fallbacks.py" in layer_tests
    assert "tests/test_narrative_v8_transition_policy.py" in layer_tests
    assert "tests/test_narrative_v8_transitions.py" in layer_tests
    assert "tests/test_narrative_v8_benchmark_matrix.py" in layer_tests
    assert "tests/test_narrative_v8_workbench_preview.py" in layer_tests
    assert "tests/test_narrative_v8_knife_library.py" in layer_tests
    assert "tests/test_narrative_v8_selection.py" in layer_tests
    assert "tests/test_narrative_v8_flavor.py" in layer_tests
    assert "tests/test_narrative_v8_ledger.py" in layer_tests
    assert "tests/test_narrative_v8_controller.py" in layer_tests
    assert "tests/test_narrative_v8_integration.py" in layer_tests
