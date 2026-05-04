from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_EXE = sys.executable
PYTEST_CMD = (PYTHON_EXE, "-m", "pytest")


@dataclass(frozen=True)
class LayerCommand:
    name: str
    cwd: Path
    argv: tuple[str, ...]

    def display(self) -> str:
        return " ".join(self.argv)

    def subprocess_argv(self) -> tuple[str, ...]:
        if not self.argv:
            return self.argv
        if os.name == "nt" and self.argv[0] == "npm":
            return ("npm.cmd", *self.argv[1:])
        return self.argv


LAYER_DEFINITIONS: dict[str, LayerCommand] = {
    "core": LayerCommand(
        name="core",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_alpha_autopilot_v2_domain.py",
            "tests/test_alpha_autopilot_v3_pipeline.py",
            "tests/test_alpha_autopilot_v3_taxonomy_and_models.py",
            "tests/test_narrative_v3_projection_bridge.py",
        ),
    ),
    "quality": LayerCommand(
        name="quality",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_alpha_autopilot_v2_golden_cases.py",
            "tests/test_alpha_autopilot_v2_rule_fixtures_runtime.py",
            "tests/test_alpha_autopilot_v2_validation_assets.py",
            "tests/test_alpha_autopilot_v2_validation_ledger.py",
            "tests/test_alpha_autopilot_v3_build_script.py",
            "tests/test_alpha_autopilot_v3_retention_metrics.py",
            "tests/test_alpha_autopilot_v3_qc_report.py",
            "tests/test_narrative_training_service_projection.py",
        ),
    ),
    "api": LayerCommand(
        name="api",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_narrative_v2_api.py",
            "tests/test_narrative_v2_app_wiring.py",
            "tests/test_narrative_v2_backend_app_route.py",
            "tests/test_narrative_v2_decision_contract.py",
            "tests/test_narrative_v2_preview_service.py",
            "tests/test_narrative_v2_services.py",
            "tests/test_narrative_v2_workbench_context_api.py",
        ),
    ),
    "frontend": LayerCommand(
        name="frontend",
        cwd=REPO_ROOT / "ui-react",
        argv=(
            "npm",
            "test",
            "--",
            "src/features/v2Workbench/backendContexts.test.ts",
            "src/features/v2Workbench/characterInterviewPanel.test.tsx",
            "src/features/v2Workbench/contextMapping.test.ts",
            "src/features/v2Workbench/session.test.ts",
            "src/pages/V2WorkbenchPage.test.tsx",
            "src/router/AppRouter.test.tsx",
        ),
    ),
    "import": LayerCommand(
        name="import",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_alpha_autopilot_v3_plotpilot_import.py",
            "tests/test_narrative_v2_imported_contexts.py",
            "tests/test_narrative_v2_workbench_quality_enrichment.py",
        ),
    ),
    "v4": LayerCommand(
        name="v4",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_alpha_autopilot_v4_modules.py",
            "backend/tests/test_narrative_v4_api.py",
        ),
    ),
    "v6": LayerCommand(
        name="v6",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_narrative_seed_extractor.py",
            "tests/test_character_parameterizer.py",
            "tests/test_parallel_plot_simulation.py",
            "tests/test_emergent_conflict_probe.py",
            "tests/test_event_injection_checkpoint.py",
            "tests/test_character_interview.py",
            "tests/test_group_memory_layer.py",
            "tests/test_graph_rag_retrieval.py",
            "tests/test_v6_graph_memory_store.py",
            "tests/test_v6_state_store.py",
            "tests/test_narrative_v6_observability.py",
            "tests/test_narrative_v6_api.py",
            "tests/test_run_v6_acceptance_review.py",
        ),
    ),
    "v8": LayerCommand(
        name="v8",
        cwd=REPO_ROOT,
        argv=(
            *PYTEST_CMD,
            "tests/test_narrative_v8_schemas.py",
            "tests/test_narrative_v8_knife_library.py",
            "tests/test_narrative_v8_selection.py",
            "tests/test_narrative_v8_flavor.py",
            "tests/test_narrative_v8_ledger.py",
            "tests/test_narrative_v8_controller.py",
            "tests/test_narrative_v8_integration.py",
            "tests/test_run_v8_acceptance_review.py",
        ),
    ),
}


def resolve_layers(layer_names: Sequence[str] | None = None, repo_root: Path | None = None) -> list[LayerCommand]:
    selected_names = list(layer_names) if layer_names else list(LAYER_DEFINITIONS)
    commands: list[LayerCommand] = []

    for name in selected_names:
        layer = LAYER_DEFINITIONS.get(name)
        if layer is None:
            raise SystemExit(f"Unknown layer: {name}")

        if repo_root is None:
            commands.append(layer)
            continue

        commands.append(
            LayerCommand(
                name=layer.name,
                cwd=repo_root / layer.cwd.relative_to(REPO_ROOT),
                argv=layer.argv,
            )
        )

    return commands


def run_layers(
    layer_names: Sequence[str] | None = None,
    repo_root: Path | None = None,
    stream=None,
) -> int:
    output = stream if stream is not None else sys.stdout
    exit_code = 0

    for command in resolve_layers(layer_names, repo_root=repo_root):
        print(f"{command.name}: {command.display()} (cwd={command.cwd})", file=output)
        result = subprocess.run(command.subprocess_argv(), cwd=command.cwd, check=False)
        if result.returncode != 0:
            exit_code = result.returncode
            break

    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run repository tests by governance layer.")
    parser.add_argument(
        "layers",
        nargs="*",
        metavar="LAYER",
        help=f"Layers to run: {', '.join(LAYER_DEFINITIONS)}. Defaults to all layers.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_layers(args.layers or None)


if __name__ == "__main__":
    raise SystemExit(main())
