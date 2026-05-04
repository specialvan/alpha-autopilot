from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from ...core.config import settings
from ..narrative.dashboard_service import build_dashboard
from ..narrative.history_service import HistoryService
from ..narrative_v4 import build_v4_workbench_preview
from ..narrative_v4.memory_store import V4MemoryStore, create_default_v4_memory_store
from ..narrative_v8 import build_v8_workbench_preview
from ..narrative.state_builder import base_state
from .imported_contexts import (
    load_imported_workbench_contexts,
    load_latest_plotpilot_report_contexts,
    load_quality_records_for_plotpilot_bundle,
)
from .online_report_contexts import probe_online_plotpilot_report_contexts


@dataclass
class NarrativeV2WorkbenchService:
    history_service: HistoryService = field(default_factory=HistoryService)
    memory_store: V4MemoryStore = field(default_factory=create_default_v4_memory_store)
    imported_context_path: Path = (
        Path(__file__).resolve().parents[4] / "artifacts" / "testing" / "plotpilot" / "workbench_contexts.json"
    )
    real_chapter_report_root: Path | None = None
    real_chapter_manifest_root: Path | None = None
    preferred_model: str | None = field(
        default_factory=lambda: settings.benchmark_model or "gpt-5.4",
    )
    online_report_api_url: str | None = field(
        default_factory=lambda: settings.plotpilot_report_api_url,
    )
    online_report_api_key: str | None = field(
        default_factory=lambda: (
            settings.plotpilot_report_api_key
            or settings.benchmark_api_key
        ),
    )
    online_report_timeout_seconds: float = field(
        default_factory=lambda: settings.plotpilot_report_api_timeout_seconds,
    )
    online_report_max_attempts: int = field(
        default_factory=lambda: settings.plotpilot_report_api_max_attempts,
    )
    online_report_backoff_seconds: float = field(
        default_factory=lambda: settings.plotpilot_report_api_backoff_seconds,
    )
    v8_preview_enabled: bool = field(
        default_factory=lambda: settings.v8_workbench_enabled,
    )

    def list_contexts(
        self,
        *,
        include_source_diagnostics: bool = True,
        online_only: bool = False,
    ) -> dict[str, object]:
        report_root = self.real_chapter_report_root or (
            self.imported_context_path.parent / "raw" / "model_switch_tests"
        )
        manifest_root = self.real_chapter_manifest_root or (
            self.imported_context_path.parent / "raw" / "decomposition"
        )
        source_diagnostics: dict[str, object] = {}
        quality_records = load_quality_records_for_plotpilot_bundle(
            self.imported_context_path.parent
        )
        online_probe = probe_online_plotpilot_report_contexts(
            api_url=self.online_report_api_url,
            api_key=self.online_report_api_key,
            preferred_model=self.preferred_model,
            quality_records=quality_records,
            timeout_seconds=self.online_report_timeout_seconds,
            max_attempts=self.online_report_max_attempts,
            backoff_seconds=self.online_report_backoff_seconds,
        )
        online_contexts = online_probe.get("payload")
        online_diagnostics = online_probe.get("diagnostics")
        if include_source_diagnostics and isinstance(online_diagnostics, dict):
            source_diagnostics["online_report"] = online_diagnostics

        if online_contexts is not None:
            contexts = online_contexts.get("contexts", [])
            if isinstance(contexts, list):
                payload = dict(online_contexts)
                payload["contexts"] = [
                    _context_with_previews(
                        item,
                        memory_store=self.memory_store,
                        v8_preview_enabled=self.v8_preview_enabled,
                    )
                    for item in contexts
                    if isinstance(item, dict)
                ]
                if include_source_diagnostics:
                    payload["source_diagnostics"] = _merge_source_diagnostics(
                        payload.get("source_diagnostics"),
                        source_diagnostics,
                    )
                return payload

        if online_only:
            payload: dict[str, object] = {
                "contexts": [],
                "source": "plotpilot_api",
                "context_contract": "real_chapter_context_v2",
                "fallback_reason": "online-report-unavailable",
            }
            if include_source_diagnostics:
                payload["source_diagnostics"] = source_diagnostics
            return payload

        report_contexts = load_latest_plotpilot_report_contexts(
            report_root,
            quality_records=quality_records,
            manifest_root=manifest_root,
            preferred_model=self.preferred_model,
        )
        if report_contexts is not None:
            contexts = report_contexts.get("contexts", [])
            if isinstance(contexts, list):
                payload = dict(report_contexts)
                payload["contexts"] = [
                    _context_with_previews(
                        item,
                        memory_store=self.memory_store,
                        v8_preview_enabled=self.v8_preview_enabled,
                    )
                    for item in contexts
                    if isinstance(item, dict)
                ]
                if include_source_diagnostics:
                    payload["source_diagnostics"] = _merge_source_diagnostics(
                        payload.get("source_diagnostics"),
                        source_diagnostics,
                    )
                return payload
        if include_source_diagnostics and "local_report" not in source_diagnostics:
            source_diagnostics["local_report"] = {
                "status": "not-found",
                "report_root": str(report_root),
                "manifest_root": str(manifest_root),
            }

        imported = load_imported_workbench_contexts(self.imported_context_path)
        if imported is not None:
            contexts = imported.get("contexts", [])
            if isinstance(contexts, list):
                payload = dict(imported)
                payload["contexts"] = [
                    _context_with_previews(
                        item,
                        memory_store=self.memory_store,
                        v8_preview_enabled=self.v8_preview_enabled,
                    )
                    for item in contexts
                    if isinstance(item, dict)
                ]
                if include_source_diagnostics:
                    payload["source_diagnostics"] = _merge_source_diagnostics(
                        payload.get("source_diagnostics"),
                        {
                            **source_diagnostics,
                            "imported_context": {"status": "ok"},
                        },
                    )
                return payload
            if include_source_diagnostics:
                imported = dict(imported)
                imported["source_diagnostics"] = _merge_source_diagnostics(
                    imported.get("source_diagnostics"),
                    {
                        **source_diagnostics,
                        "imported_context": {"status": "ok"},
                    },
                )
            return imported

        state = base_state()
        dashboard = build_dashboard()
        history = self.history_service.get_history(limit=50)
        latest_snapshot = history["historySnapshots"][-1] if history["historySnapshots"] else None

        summary_parts = ["History-backed live context"]
        if latest_snapshot:
            summary_parts.append(
                f"latest {latest_snapshot.get('stage', 'unknown')} / {latest_snapshot.get('action', 'unknown')}"
            )

        context = {
            "id": f"live-chapter-{state.chapter_index}",
            "chapterNumber": state.chapter_index,
            "title": dashboard.chapterSummary["title"],
            "stage": state.stage,
            "summary": " | ".join(summary_parts),
            "state": asdict(state),
            "v3_feedback_history": _feedback_history_from_snapshots(history["historySnapshots"]),
        }

        payload = {
            "contexts": [
                _context_with_previews(
                    context,
                    memory_store=self.memory_store,
                    v8_preview_enabled=self.v8_preview_enabled,
                )
            ]
        }
        if include_source_diagnostics:
            payload["source_diagnostics"] = _merge_source_diagnostics(
                None,
                {
                    **source_diagnostics,
                    "live_context": {"status": "ok"},
                },
            )
        return payload


def _context_with_previews(
    context: dict[str, object],
    *,
    memory_store: V4MemoryStore,
    v8_preview_enabled: bool,
) -> dict[str, object]:
    enriched = dict(context)
    try:
        enriched["v4_preview"] = build_v4_workbench_preview(
            enriched,
            memory_store=memory_store,
            history_window=50,
        )
    except Exception:
        enriched["v4_preview"] = {
            "enabled": False,
            "fallback_reason": "v4-preview-error",
            "candidate_count": 0,
            "selected_candidate": None,
            "top_candidates": [],
            "qc_summary": {"warnings": ["v4-preview-error"]},
            "memory_summary": {
                "relationship_history_count": 0,
                "feedback_history_count": 0,
            },
            "v4_input_profile": {},
        }
    try:
        enriched["v8_preview"] = build_v8_workbench_preview(
            enriched,
            preview_enabled=v8_preview_enabled,
        )
    except Exception:
        enriched["v8_preview"] = {
            "enabled": False,
            "fallback_reason": "v8-preview-error",
            "decision_mode": None,
            "primary_knife_id": None,
            "secondary_knife_id": None,
            "fallback_action": None,
            "next_control_state": None,
            "transition": None,
            "explanation": {},
            "future_hooks": [],
            "risk_if_exposed": [],
            "v8_input_profile": {},
        }
    return enriched


def _feedback_history_from_snapshots(snapshots: list[dict[str, object]]) -> list[dict[str, object]]:
    feedback_history: list[dict[str, object]] = []
    for snapshot in snapshots[-5:]:
        if not isinstance(snapshot, dict):
            continue
        predicted = _safe_float(snapshot.get("predicted"), default=0.0)
        target = _safe_float(snapshot.get("target"), default=0.0)
        feedback = _safe_float(snapshot.get("feedback"), default=0.0)
        feedback_history.append(
            {
                "accepted": feedback >= 0.55,
                "retention_delta": round(feedback - target, 4),
                "abandonment_delta": round(max(0.0, predicted - feedback), 4),
            }
        )
    return feedback_history


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default


def _merge_source_diagnostics(
    primary: object,
    secondary: object,
) -> dict[str, object]:
    merged: dict[str, object] = {}
    if isinstance(primary, dict):
        merged.update(primary)
    if isinstance(secondary, dict):
        merged.update(secondary)
    return merged
