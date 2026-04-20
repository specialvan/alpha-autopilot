from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json

from alpha_autopilot import create_history_repository


class HistoryExportService:
    def __init__(self) -> None:
        self.repository = create_history_repository()

    def export_json(self, target_path: str | Path) -> Dict[str, Any]:
        path = Path(target_path)
        payload = {
            "training_logs": self.repository.read_training_logs(),
            "value_metrics": [record.__dict__ for record in self.repository.read_value_metrics().records],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(path), "counts": {"training_logs": len(payload["training_logs"]), "value_metrics": len(payload["value_metrics"])}}
