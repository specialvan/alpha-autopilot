from __future__ import annotations

from typing import Any, Dict

from alpha_autopilot import HistoryRepository, create_history_repository


class HistoryService:
    def __init__(self, repository: HistoryRepository | None = None) -> None:
        self.repository = repository or create_history_repository()

    def _version_key(self, entry: Dict[str, Any]) -> str:
        if entry.get("version"):
            return str(entry["version"])
        stage = entry.get("stage") or "unknown"
        return f"{stage}/unversioned"

    def get_history(self, stage: str | None = None, action: str | None = None, limit: int = 20) -> Dict[str, Any]:
        training_logs = self.repository.read_training_logs()
        if stage:
            training_logs = [item for item in training_logs if item.get("stage") == stage]
        if action:
            training_logs = [item for item in training_logs if item.get("action") == action]
        training_logs = training_logs[-limit:]

        metrics = self.repository.read_value_metrics()
        summary = metrics.summary()
        top_actions = metrics.top_actions()

        grouped: Dict[str, Dict[str, Any]] = {}
        stage_groups: Dict[str, Dict[str, Any]] = {}
        for entry in training_logs:
            key = self._version_key(entry)
            bucket = grouped.setdefault(
                key,
                {
                    "version": key,
                    "count": 0,
                    "latest_time": "",
                    "average_feedback": 0.0,
                    "average_chapter_quality": 0.0,
                    "average_followup_writeability": 0.0,
                    "average_continuity_delta": 0.0,
                    "accept_rate": 0.0,
                    "actions": [],
                    "stage": entry.get("stage", ""),
                },
            )
            bucket["count"] += 1
            bucket["latest_time"] = entry.get("timestamp", bucket["latest_time"])
            bucket["actions"].append(entry.get("action", ""))
            bucket["average_feedback"] += float(entry.get("feedback", 0.0))
            bucket["average_chapter_quality"] += float(entry.get("feedback", 0.0))
            bucket["average_followup_writeability"] += max(0.0, min(1.0, float(entry.get("feedback", 0.0)) * 0.9 + 0.05))
            bucket["average_continuity_delta"] += float(entry.get("target", 0.0)) - float(entry.get("predicted", 0.0))
            bucket["accept_rate"] += 1.0 if float(entry.get("feedback", 0.0)) >= 0.8 else 0.0

            stage_key = entry.get("stage", "unknown")
            stage_bucket = stage_groups.setdefault(
                stage_key,
                {
                    "stage": stage_key,
                    "count": 0,
                    "latest_time": "",
                    "versions": [],
                    "average_feedback": 0.0,
                },
            )
            stage_bucket["count"] += 1
            stage_bucket["latest_time"] = entry.get("timestamp", stage_bucket["latest_time"])
            stage_bucket["versions"].append(key)
            stage_bucket["average_feedback"] += float(entry.get("feedback", 0.0))

        version_timeline = []
        for bucket in grouped.values():
            count = max(bucket["count"], 1)
            version_timeline.append(
                {
                    "version": bucket["version"],
                    "count": bucket["count"],
                    "latest_time": bucket["latest_time"],
                    "average_feedback": bucket["average_feedback"] / count,
                    "average_chapter_quality": bucket["average_chapter_quality"] / count,
                    "average_followup_writeability": bucket["average_followup_writeability"] / count,
                    "average_continuity_delta": bucket["average_continuity_delta"] / count,
                    "accept_rate": bucket["accept_rate"] / count,
                    "actions": sorted(set(action for action in bucket["actions"] if action)),
                    "stage": bucket["stage"],
                }
            )

        version_timeline.sort(key=lambda item: item["latest_time"], reverse=True)

        stage_timeline = []
        for bucket in stage_groups.values():
            count = max(bucket["count"], 1)
            stage_timeline.append(
                {
                    "stage": bucket["stage"],
                    "count": bucket["count"],
                    "latest_time": bucket["latest_time"],
                    "average_feedback": bucket["average_feedback"] / count,
                    "versions": sorted(set(bucket["versions"]), reverse=True),
                }
            )
        stage_timeline.sort(key=lambda item: item["latest_time"], reverse=True)

        latest_training = training_logs[-5:]
        return {
            "historyLogs": [
                {
                    "time": item.get("timestamp", ""),
                    "text": f"[{item.get('stage', '')}] {item.get('action', '')} pred={item.get('predicted', 0):.3f} target={item.get('target', 0):.3f} feedback={item.get('feedback', 0):.3f}",
                }
                for item in latest_training
            ],
            "historySnapshots": latest_training,
            "valueSummary": summary,
            "topActions": top_actions,
            "versionTimeline": version_timeline[:10],
            "stageTimeline": stage_timeline[:10],
            "filters": {"stage": stage, "action": action, "limit": limit},
        }
