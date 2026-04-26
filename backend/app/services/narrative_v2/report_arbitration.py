from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class PlotPilotReportCandidate:
    report_path: Path
    model: str
    timestamp: str | None
    success: int
    total: int
    success_rate: float
    run_id: str | None = None
    manifest_path: Path | None = None


def resolve_plotpilot_report_candidate(
    report_root: Path,
    *,
    manifest_root: Path | None = None,
    preferred_model: str | None = None,
) -> PlotPilotReportCandidate | None:
    report_paths = _discover_report_paths(report_root)
    if not report_paths:
        return None

    manifest_links = _resolve_manifest_links(report_root, manifest_root)
    candidates = [
        _build_candidate(path, manifest_links.get(path))
        for path in report_paths
    ]
    candidates = [item for item in candidates if item is not None]
    if not candidates:
        return None

    return max(
        candidates,
        key=lambda item: (
            1 if preferred_model and item.model == preferred_model else 0,
            1 if item.run_id else 0,
            item.success_rate,
            item.success,
            _safe_timestamp_score(item.timestamp),
            item.report_path.stat().st_mtime,
        ),
    )


def _discover_report_paths(report_root: Path) -> list[Path]:
    if report_root.is_file():
        if report_root.name == "report.json":
            return [report_root]
        return []
    if not report_root.exists():
        return []
    return sorted(path for path in report_root.rglob("report.json") if path.is_file())


def _resolve_manifest_links(
    report_root: Path,
    manifest_root: Path | None,
) -> dict[Path, tuple[str, Path]]:
    if manifest_root is None:
        parent = report_root.parent if report_root.is_file() else report_root.parent
        manifest_root = parent / "decomposition"
    if not manifest_root.exists():
        return {}

    links: dict[Path, tuple[str, Path, float]] = {}
    manifest_paths = sorted(path for path in manifest_root.rglob("manifest.json") if path.is_file())
    for manifest_path in manifest_paths:
        payload = _load_json_dict(manifest_path)
        if payload is None:
            continue
        run_id = str(payload.get("run_id", "")).strip() or None
        generated_at = _safe_timestamp_score(payload.get("generated_at"))
        run_dirs = payload.get("input", {})
        if isinstance(run_dirs, dict):
            run_dirs = run_dirs.get("run_dirs", [])
        if not isinstance(run_dirs, list):
            continue
        for run_dir in run_dirs:
            resolved = _resolve_report_path_from_run_dir(report_root, run_dir)
            if resolved is None:
                continue
            existing = links.get(resolved)
            if existing is None or generated_at >= existing[2]:
                links[resolved] = (run_id or "", manifest_path, generated_at)
    return {
        path: (
            (run_id if run_id else None),
            manifest_path,
        )
        for path, (run_id, manifest_path, _generated_at) in links.items()
    }


def _resolve_report_path_from_run_dir(report_root: Path, run_dir: object) -> Path | None:
    if not isinstance(run_dir, str) or not run_dir.strip():
        return None
    normalized = run_dir.replace("\\", "/").strip("/")
    segments = [part for part in normalized.split("/") if part and not part.endswith(":")]
    if not segments:
        return None

    suffix_candidates: list[Path] = []
    if "model_switch_tests" in segments:
        index = segments.index("model_switch_tests")
        tail = segments[index + 1 :]
        if tail:
            suffix_candidates.append(Path(*tail))
    max_suffix = min(4, len(segments))
    for size in range(max_suffix, 0, -1):
        suffix_candidates.append(Path(*segments[-size:]))

    seen: set[Path] = set()
    for suffix in suffix_candidates:
        if suffix in seen:
            continue
        seen.add(suffix)
        candidate = report_root / suffix / "report.json"
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _build_candidate(
    report_path: Path,
    manifest_ref: tuple[str | None, Path] | None,
) -> PlotPilotReportCandidate | None:
    payload = _load_json_dict(report_path)
    if payload is None:
        return None
    model = str(payload.get("model", "unknown-model"))
    success = _safe_int(payload.get("success"))
    total = _safe_int(payload.get("total"))
    if total <= 0:
        results = payload.get("results", [])
        if isinstance(results, list):
            total = len([item for item in results if isinstance(item, dict)])
            success = len(
                [
                    item
                    for item in results
                    if isinstance(item, dict) and item.get("success") is not False
                ]
            )
    if total <= 0:
        return None
    success_rate = round(success / total, 6)
    run_id: str | None = None
    manifest_path: Path | None = None
    if manifest_ref is not None:
        run_id = manifest_ref[0]
        manifest_path = manifest_ref[1]
    timestamp = payload.get("timestamp")
    return PlotPilotReportCandidate(
        report_path=report_path,
        model=model,
        timestamp=str(timestamp) if isinstance(timestamp, str) else None,
        success=success,
        total=total,
        success_rate=success_rate,
        run_id=run_id,
        manifest_path=manifest_path,
    )


def _load_json_dict(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _safe_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return 0


def _safe_timestamp_score(value: object) -> float:
    if not isinstance(value, str) or not value.strip():
        return 0.0
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except Exception:
        return 0.0
