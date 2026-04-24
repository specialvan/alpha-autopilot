from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..narrative.dashboard_service import build_dashboard
from ..narrative.history_service import HistoryService
from ..narrative.state_builder import base_state
from .imported_contexts import load_imported_workbench_contexts


@dataclass
class NarrativeV2WorkbenchService:
    history_service: HistoryService = field(default_factory=HistoryService)
    imported_context_path: Path = (
        Path(__file__).resolve().parents[4] / "artifacts" / "testing" / "plotpilot" / "workbench_contexts.json"
    )

    def list_contexts(self) -> dict[str, object]:
        imported = load_imported_workbench_contexts(self.imported_context_path)
        if imported is not None:
            return imported

        state = base_state()
        dashboard = build_dashboard()
        history = self.history_service.get_history(limit=5)
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
        }

        return {"contexts": [context]}
