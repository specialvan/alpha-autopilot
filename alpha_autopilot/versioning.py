from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, List


@dataclass
class MatrixSnapshot:
    version: str
    created_at: str
    weights: Dict[str, float]
    bias: float
    sample_count: int
    notes: str = ""


class VersionManager:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path(__file__).resolve().parents[1])
        self.store_dir = self.root / "artifacts"
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.store_dir / "registry.json"

    def _load_registry(self) -> List[Dict[str, Any]]:
        if not self.registry_path.exists():
            return []
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _save_registry(self, items: List[Dict[str, Any]]) -> None:
        self.registry_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_version(self, weights: Dict[str, float], bias: float, sample_count: int, notes: str = "") -> MatrixSnapshot:
        registry = self._load_registry()
        version = f"v{len(registry) + 1:03d}"
        snapshot = MatrixSnapshot(
            version=version,
            created_at=datetime.now(timezone.utc).isoformat(),
            weights=dict(sorted(weights.items())),
            bias=round(bias, 6),
            sample_count=sample_count,
            notes=notes,
        )
        registry.append(asdict(snapshot))
        self._save_registry(registry)
        self._write_snapshot(snapshot)
        return snapshot

    def latest(self) -> MatrixSnapshot | None:
        registry = self._load_registry()
        if not registry:
            return None
        item = registry[-1]
        return MatrixSnapshot(**item)

    def _write_snapshot(self, snapshot: MatrixSnapshot) -> None:
        path = self.store_dir / f"matrix_{snapshot.version}.json"
        path.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")
