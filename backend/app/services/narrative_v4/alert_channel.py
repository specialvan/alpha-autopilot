from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import urllib.error
import urllib.request

from alpha_autopilot import ArtifactStore
from ...core.config import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now_utc().isoformat().replace("+00:00", "Z")


@dataclass
class V4AlertChannel:
    sink_path: Path
    state_path: Path
    cooldown_seconds: int = 600
    remote_targets: dict[str, str] | None = None
    remote_timeout_seconds: float = 3.0
    oncall_contacts: tuple[str, ...] = ()

    def route(self, snapshot: dict[str, object]) -> dict[str, object]:
        normalized_targets = self._normalized_remote_targets()
        oncall_validation = self._build_oncall_validation(remote_enabled=bool(normalized_targets))
        remote_routing = self._remote_routing_not_enabled()
        alerts = snapshot.get("alerts")
        if not isinstance(alerts, list):
            return {
                "enabled": True,
                "routed": False,
                "reason": "invalid-alerts",
                "criticalCount": 0,
                "remoteRouting": remote_routing,
                "oncallValidation": oncall_validation,
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
                "remoteRouting": remote_routing,
                "oncallValidation": oncall_validation,
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
                        "remoteRouting": remote_routing,
                        "oncallValidation": oncall_validation,
                    }

        remote_routing = self._route_remote_alerts(
            snapshot=snapshot,
            critical_alerts=critical_alerts,
            signature=signature,
            normalized_targets=normalized_targets,
            oncall_validation=oncall_validation,
        )
        snapshot_meta = self._snapshot_meta(snapshot)
        row = {
            "timestamp": _now_iso(),
            "signature": signature,
            "critical_alerts": critical_alerts,
            "snapshot_meta": snapshot_meta,
            "remote_routing": remote_routing,
            "oncall_validation": oncall_validation,
        }
        self._append_jsonl(self.sink_path, row)
        self._write_state({"last_signature": signature, "last_routed_at": _now_iso()})
        return {
            "enabled": True,
            "routed": True,
            "reason": "routed-critical-alert",
            "criticalCount": len(critical_alerts),
            "signature": signature,
            "remoteRouting": remote_routing,
            "oncallValidation": oncall_validation,
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

    def _normalized_remote_targets(self) -> dict[str, str]:
        if not self.remote_targets:
            return {}
        normalized: dict[str, str] = {}
        for raw_name, raw_url in self.remote_targets.items():
            name = str(raw_name).strip().lower()
            url = str(raw_url).strip()
            if not name or not url:
                continue
            normalized[name] = url
        return normalized

    def _build_oncall_validation(self, *, remote_enabled: bool) -> dict[str, object]:
        contacts = [item for item in self.oncall_contacts if str(item).strip()]
        if not remote_enabled:
            return {
                "enabled": False,
                "valid": True,
                "reason": "remote-disabled",
                "contacts": contacts,
            }
        if contacts:
            return {
                "enabled": True,
                "valid": True,
                "reason": "oncall-ready",
                "contacts": contacts,
            }
        return {
            "enabled": True,
            "valid": False,
            "reason": "missing-oncall-contact",
            "contacts": [],
        }

    def _remote_routing_not_enabled(self) -> dict[str, object]:
        return {
            "enabled": False,
            "status": "disabled",
            "deliveredCount": 0,
            "failedCount": 0,
            "targets": [],
        }

    def _snapshot_meta(self, snapshot: dict[str, object]) -> dict[str, object]:
        return {
            "feedbackRows": _safe_int(snapshot.get("feedbackRows")),
            "relationshipRows": _safe_int(snapshot.get("relationshipRows")),
            "acceptRate": _safe_float(snapshot.get("acceptRate")),
            "feedbackSignal": _safe_float(snapshot.get("feedbackSignal")),
            "lastUpdated": snapshot.get("lastUpdated"),
        }

    def _route_remote_alerts(
        self,
        *,
        snapshot: dict[str, object],
        critical_alerts: list[dict[str, object]],
        signature: str,
        normalized_targets: dict[str, str],
        oncall_validation: dict[str, object],
    ) -> dict[str, object]:
        if not normalized_targets:
            return self._remote_routing_not_enabled()

        if not bool(oncall_validation.get("valid", False)):
            return {
                "enabled": True,
                "status": "blocked-oncall-validation",
                "deliveredCount": 0,
                "failedCount": 0,
                "targets": [
                    {
                        "channel": name,
                        "target": target_url,
                        "ok": False,
                        "httpStatus": None,
                        "error": "missing-oncall-contact",
                    }
                    for name, target_url in normalized_targets.items()
                ],
            }

        payload = {
            "timestamp": _now_iso(),
            "signature": signature,
            "critical_alerts": critical_alerts,
            "snapshot_meta": self._snapshot_meta(snapshot),
            "oncall": {
                "contacts": list(self.oncall_contacts),
            },
        }
        targets: list[dict[str, object]] = []
        delivered_count = 0
        failed_count = 0
        for channel_name, target_url in normalized_targets.items():
            result = self._post_json(target_url, payload)
            target_result = {
                "channel": channel_name,
                "target": target_url,
                "ok": bool(result["ok"]),
                "httpStatus": result["httpStatus"],
                "error": result["error"],
            }
            targets.append(target_result)
            if target_result["ok"]:
                delivered_count += 1
            else:
                failed_count += 1
        status = "ok" if failed_count == 0 else "degraded-local-only"
        return {
            "enabled": True,
            "status": status,
            "deliveredCount": delivered_count,
            "failedCount": failed_count,
            "targets": targets,
        }

    def _post_json(self, target_url: str, payload: dict[str, object]) -> dict[str, object]:
        timeout_seconds = max(0.1, _safe_float(self.remote_timeout_seconds))
        request = urllib.request.Request(
            target_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
                status = int(getattr(response, "status", 0) or 0)
        except urllib.error.HTTPError as exc:
            status = int(getattr(exc, "code", 0) or 0)
            return {
                "ok": False,
                "httpStatus": status if status > 0 else None,
                "error": f"HTTPError:{type(exc).__name__}",
            }
        except Exception as exc:
            return {
                "ok": False,
                "httpStatus": None,
                "error": f"{type(exc).__name__}:{exc}",
            }
        if status >= 400:
            return {
                "ok": False,
                "httpStatus": status,
                "error": "http-status-not-ok",
            }
        return {
            "ok": True,
            "httpStatus": status if status > 0 else 200,
            "error": "",
        }


def create_default_v4_alert_channel(root: Path | None = None) -> V4AlertChannel:
    store = ArtifactStore.default()
    base = root or store.artifacts_dir / "history"
    remote_targets: dict[str, str] = {}
    if bool(getattr(settings, "v4_alert_remote_enabled", False)):
        im_webhook_url = str(getattr(settings, "v4_alert_im_webhook_url", "") or "").strip()
        webhook_url = str(getattr(settings, "v4_alert_webhook_url", "") or "").strip()
        if im_webhook_url:
            remote_targets["im"] = im_webhook_url
        if webhook_url:
            remote_targets["webhook"] = webhook_url
    return V4AlertChannel(
        sink_path=base / "v4_observability_alerts.jsonl",
        state_path=base / "v4_observability_alerts.state.json",
        cooldown_seconds=600,
        remote_targets=remote_targets or None,
        remote_timeout_seconds=max(
            0.1,
            _safe_float(getattr(settings, "v4_alert_webhook_timeout_seconds", 3.0)),
        ),
        oncall_contacts=_parse_oncall_contacts(getattr(settings, "v4_alert_oncall_contacts", None)),
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


def _parse_oncall_contacts(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        raw_items = [str(item).strip() for item in value if str(item).strip()]
    else:
        raw = str(value).strip()
        if not raw:
            return ()
        normalized = raw.replace("\n", ",").replace(";", ",")
        raw_items = [item.strip() for item in normalized.split(",") if item.strip()]
    deduped: list[str] = []
    for item in raw_items:
        if item not in deduped:
            deduped.append(item)
    return tuple(deduped)


def _parse_dt(value: str) -> datetime | None:
    content = value.strip()
    if not content:
        return None
    normalized = content.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except Exception:
        return None
