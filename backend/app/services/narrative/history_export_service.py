from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json

from alpha_autopilot import ArtifactStore, HistoryRepository, create_history_repository


class HistoryExportService:
    def __init__(self, repository: HistoryRepository | None = None, store: ArtifactStore | None = None) -> None:
        self.store = store or ArtifactStore.default()
        self.repository = repository or create_history_repository(self.store)

    def export_json(self, target_path: str | Path | None = None) -> Dict[str, Any]:
        if target_path is None:
            export_name = f"history-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            path = self.store.artifacts_dir / "exports" / export_name
        else:
            path = Path(target_path)
        payload = {
            "training_logs": self.repository.read_training_logs(),
            "value_metrics": [record.__dict__ for record in self.repository.read_value_metrics().records],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(path), "counts": {"training_logs": len(payload["training_logs"]), "value_metrics": len(payload["value_metrics"])}}
