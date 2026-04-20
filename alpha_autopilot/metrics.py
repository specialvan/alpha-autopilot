from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
import json
from typing import Dict, List


@dataclass
class RecommendationMetricRecord:
    action: str
    score: float
    accepted: bool
    chapter_quality: float
    followup_writeability: float
    continuity_delta: float
    notes: str = ""


@dataclass
class RecommendationValueMetrics:
    records: List[RecommendationMetricRecord] = field(default_factory=list)

    def add_record(self, record: RecommendationMetricRecord) -> None:
        self.records.append(record)

    def summary(self) -> Dict[str, float]:
        if not self.records:
            return {
                "sample_count": 0.0,
                "accept_rate": 0.0,
                "average_chapter_quality": 0.0,
                "average_followup_writeability": 0.0,
                "average_continuity_delta": 0.0,
            }
        sample_count = float(len(self.records))
        return {
            "sample_count": sample_count,
            "accept_rate": mean(1.0 if item.accepted else 0.0 for item in self.records),
            "average_chapter_quality": mean(item.chapter_quality for item in self.records),
            "average_followup_writeability": mean(item.followup_writeability for item in self.records),
            "average_continuity_delta": mean(item.continuity_delta for item in self.records),
        }

    def top_actions(self, limit: int = 5) -> List[Dict[str, float]]:
        aggregates: Dict[str, List[float]] = {}
        for record in self.records:
            aggregates.setdefault(record.action, []).append(record.chapter_quality)
        ranked = sorted(
            ((action, mean(values)) for action, values in aggregates.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        return [{"action": action, "average_quality": score} for action, score in ranked[:limit]]

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = [record.__dict__ for record in self.records]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "RecommendationValueMetrics":
        target = Path(path)
        if not target.exists():
            return cls()
        raw = json.loads(target.read_text(encoding="utf-8"))
        metrics = cls()
        for item in raw:
            metrics.add_record(RecommendationMetricRecord(**item))
        return metrics
