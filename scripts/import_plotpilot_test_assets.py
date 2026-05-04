from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
import json


DEFAULT_PLOTPILOT_ROOT = Path(r"D:\workspace\PlotPilot")
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(DEFAULT_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_REPO_ROOT))

from backend.app.services.narrative_v2.imported_contexts import (  # noqa: E402
    build_workbench_contexts_from_plotpilot_report,
)


def copy_file_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def copy_tree_if_exists(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return True


def import_plotpilot_assets(repo_root: Path, plotpilot_root: Path) -> dict[str, object]:
    target_root = repo_root / "artifacts" / "testing" / "plotpilot"
    raw_root = target_root / "raw"

    env_source = plotpilot_root / ".env.local"
    env_target = repo_root / ".env.local"

    run_dir = (
        plotpilot_root
        / "data"
        / "data"
        / "logs"
        / "model_switch_tests"
        / "gpt54_xuanhuan_light_20260421_155711"
    )
    decomposition_dir = (
        plotpilot_root
        / "data"
        / "decomposition"
        / "v3"
        / "runs"
        / "v3_20260421_220604"
    )

    report_path = run_dir / "report.json"
    report_payload = json.loads(report_path.read_text(encoding="utf-8-sig"))
    contexts = build_workbench_contexts_from_plotpilot_report(report_payload)

    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "workbench_contexts.json").write_text(
        json.dumps({"contexts": contexts}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    copy_tree_if_exists(run_dir, raw_root / "model_switch_tests" / run_dir.name)
    copy_tree_if_exists(decomposition_dir, raw_root / "decomposition" / decomposition_dir.name)
    copied_env = copy_file_if_exists(env_source, env_target)

    return {
        "copied_env": copied_env,
        "env_target": str(env_target),
        "workbench_contexts": str(target_root / "workbench_contexts.json"),
        "raw_run_dir": str(raw_root / "model_switch_tests" / run_dir.name),
        "raw_decomposition_dir": str(raw_root / "decomposition" / decomposition_dir.name),
        "context_count": len(contexts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plotpilot-root", type=Path, default=DEFAULT_PLOTPILOT_ROOT)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    args = parser.parse_args()

    result = import_plotpilot_assets(
        repo_root=args.repo_root.resolve(),
        plotpilot_root=args.plotpilot_root.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
