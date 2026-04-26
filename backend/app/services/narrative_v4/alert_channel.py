from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from alpha_autopilot import ArtifactStore


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now_utc().isoformat().replace("+00:00", "Z")


@dataclass
class V4AlertChannel:
    sink_path: Path
    state_path: Path
    cooldown_seconds: int = 600

    def route(self, snapshot: dict[str, object]) -> dict[str, object]:
        alerts = snapshot.get("alerts")
        if not isinstance(alerts, list):
            return {
                "enabled": True,
                "routed": False,
                "reason": "invalid-alerts",
                "criticalCount": 0,
            }
        critical_alerts = [
            item
            for item in alerts
            if isinstance(item, dict) and str(item.get("severity", "")).lower() == "critical"
        ]
        if not critical_alerts:
            return {
                "enabled": True,
                "routed": False,
                "reason": "no-critical-alert",
                "criticalCount": 0,
            }

        signature = self._build_signature(critical_alerts)
        state = self._read_state()
        now = _now_utc()
        if state and state.get("last_signature") == signature:
            last_routed_at = _parse_dt(str(state.get("last_routed_at", "")))
            if last_routed_at is not None:
                if now - last_routed_at < timedelta(seconds=max(0, self.cooldown_seconds)):
                    return {
                        "enabled": True,
                        "routed": False,
                        "reason": "cooldown-active",
                        "criticalCount": len(critical_alerts),
                        "signature": signature,
                        "cooldownSeconds": self.cooldown_seconds,
                    }

        row = {
            "timestamp": _now_iso(),
            "signature": signature,
            "critical_alerts": critical_alerts,
            "snapshot_meta": {
                "feedbackRows": _safe_int(snapshot.get("feedbackRows")),
                "relationshipRows": _safe_int(snapshot.get("relationshipRows")),
                "acceptRate": _safe_float(snapshot.get("acceptRate")),
                "feedbackSignal": _safe_float(snapshot.get("feedbackSignal")),
                "lastUpdated": snapshot.get("lastUpdated"),
            },
        }
        self._append_jsonl(self.sink_path, row)
        self._write_state({"last_signature": signature, "last_routed_at": _now_iso()})
        return {
            "enabled": True,
            "routed": True,
            "reason": "routed-critical-alert",
            "criticalCount": len(critical_alerts),
            "signature": signature,
        }

    def _build_signature(self, alerts: list[dict[str, object]]) -> str:
        normalized = sorted(
            [
                {
                    "code": str(item.get("code", "")),
                    "severity": str(item.get("severity", "")),
                    "message": str(item.get("message", "")),
                }
                for item in alerts
            ],
            key=lambda item: (item["severity"], item["code"], item["message"]),
        )
        return json.dumps(normalized, ensure_ascii=False, sort_keys=True)

    def _read_state(self) -> dict[str, object] | None:
        if not self.state_path.exists():
            return None
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def _write_state(self, payload: dict[str, object]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _append_jsonl(self, path: Path, row: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def create_default_v4_alert_channel(root: Path | None = None) -> V4AlertChannel:
    store = ArtifactStore.default()
    base = root or store.artifacts_dir / "history"
    return V4AlertChannel(
        sink_path=base / "v4_observability_alerts.jsonl",
        state_path=base / "v4_observability_alerts.state.json",
        cooldown_seconds=600,
    )


def route_v4_observability_alerts(
    snapshot: dict[str, object],
    *,
    channel: V4AlertChannel | None = None,
) -> dict[str, object]:
    active_channel = channel or create_default_v4_alert_channel()
    return active_channel.route(snapshot)


def _safe_float(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return 0.0


def _safe_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return 0


def _parse_dt(value: str) -> datetime | None:
    content = value.strip()
    if not content:
        return None
    normalized = content.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except Exception:
        return None
