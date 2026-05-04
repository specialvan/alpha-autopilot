from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from .imported_contexts import build_workbench_contexts_from_plotpilot_report


def load_online_plotpilot_report_contexts(
    *,
    api_url: str | None,
    api_key: str | None = None,
    preferred_model: str | None = None,
    quality_records: list[dict[str, object]] | None = None,
    timeout_seconds: float = 8.0,
    max_attempts: int = 3,
    backoff_seconds: float = 0.2,
) -> dict[str, object] | None:
    result = probe_online_plotpilot_report_contexts(
        api_url=api_url,
        api_key=api_key,
        preferred_model=preferred_model,
        quality_records=quality_records,
        timeout_seconds=timeout_seconds,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
    )
    payload = result.get("payload")
    if isinstance(payload, dict):
        diagnostics = result.get("diagnostics")
        if isinstance(diagnostics, dict):
            payload["source_diagnostics"] = {
                "online_report": diagnostics,
            }
        return payload
    return None


def probe_online_plotpilot_report_contexts(
    *,
    api_url: str | None,
    api_key: str | None = None,
    preferred_model: str | None = None,
    quality_records: list[dict[str, object]] | None = None,
    timeout_seconds: float = 8.0,
    max_attempts: int = 3,
    backoff_seconds: float = 0.2,
    sleep_fn=time.sleep,
) -> dict[str, object]:
    resolved_max_attempts = max(1, int(max_attempts))
    resolved_backoff_seconds = max(0.0, float(backoff_seconds))
    diagnostics: dict[str, object] = {
        "enabled": bool(api_url and api_url.strip()),
        "attempted": False,
        "status": "disabled",
        "preferred_model": preferred_model,
        "timeout_seconds": timeout_seconds,
        "max_attempts": resolved_max_attempts,
        "backoff_seconds": resolved_backoff_seconds,
        "attempts_count": 0,
        "retried": False,
        "retry_exhausted": False,
        "attempt_history": [],
    }
    if not api_url or not api_url.strip():
        return {"payload": None, "diagnostics": diagnostics}

    request_url = _build_request_url(api_url.strip(), preferred_model=preferred_model)
    diagnostics["attempted"] = True
    diagnostics["request_url"] = request_url

    payload: dict[str, object] | None = None
    fetch_meta: dict[str, object] = {"status": "fetch-failed"}
    attempt_history: list[dict[str, object]] = []
    for attempt in range(1, resolved_max_attempts + 1):
        payload, fetch_meta = _fetch_json_payload_with_meta(
            request_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        attempt_meta = dict(fetch_meta)
        attempt_meta["attempt"] = attempt
        attempt_history.append(attempt_meta)
        if isinstance(payload, dict):
            break

        if attempt >= resolved_max_attempts or not _should_retry(fetch_meta):
            break
        delay_seconds = round(
            resolved_backoff_seconds * (2 ** (attempt - 1)),
            4,
        )
        if delay_seconds > 0:
            sleep_fn(delay_seconds)

    diagnostics["attempt_history"] = attempt_history
    diagnostics["attempts_count"] = len(attempt_history)
    diagnostics["retried"] = len(attempt_history) > 1
    diagnostics.update(fetch_meta)
    diagnostics["retry_exhausted"] = (
        not isinstance(payload, dict)
        and len(attempt_history) >= resolved_max_attempts
        and _should_retry(fetch_meta)
    )
    if not isinstance(payload, dict):
        return {"payload": None, "diagnostics": diagnostics}

    report_payload = payload.get("report")
    if not isinstance(report_payload, dict):
        report_payload = payload
    if not isinstance(report_payload.get("results"), list):
        diagnostics["status"] = "invalid-report-payload"
        return {"payload": None, "diagnostics": diagnostics}

    contexts = build_workbench_contexts_from_plotpilot_report(
        report_payload,
        quality_records=quality_records,
    )
    if not contexts:
        diagnostics["status"] = "empty-contexts"
        return {"payload": None, "diagnostics": diagnostics}

    success, total = _extract_success_total(report_payload)
    success_rate = round(success / total, 6) if total > 0 else 0.0
    run_id = _extract_run_id(payload, report_payload)
    manifest_path = _extract_manifest_path(payload, report_payload)
    resolved_model = str(
        report_payload.get("model", payload.get("model", "unknown-model"))
    )
    report_timestamp = report_payload.get("timestamp")
    diagnostics["status"] = "ok"
    response_payload = {
        "contexts": contexts,
        "source": "plotpilot_api",
        "context_contract": "real_chapter_context_v2",
        "report_url": request_url,
        "run_id": run_id,
        "manifest_path": manifest_path,
        "preferred_model": preferred_model,
        "resolved_model": resolved_model,
        "report_success_rate": success_rate,
        "report_timestamp": report_timestamp if isinstance(report_timestamp, str) else None,
        "arbitration_strategy": "online-report-v1",
    }
    return {
        "payload": response_payload,
        "diagnostics": diagnostics,
    }


def _fetch_json_payload(
    url: str,
    *,
    api_key: str | None,
    timeout_seconds: float,
) -> dict[str, object] | None:
    payload, _meta = _fetch_json_payload_with_meta(
        url,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )
    return payload


def _fetch_json_payload_with_meta(
    url: str,
    *,
    api_key: str | None,
    timeout_seconds: float,
) -> tuple[dict[str, object] | None, dict[str, object]]:
    meta: dict[str, object] = {"status": "fetch-failed"}
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read()
    except TimeoutError as error:
        meta["status"] = "timeout"
        meta["error_type"] = type(error).__name__
        meta["error_message"] = str(error)
        return None, meta
    except HTTPError as error:
        meta["status"] = "http-error"
        meta["http_status"] = error.code
        meta["error_type"] = type(error).__name__
        meta["error_message"] = str(error)
        return None, meta
    except URLError as error:
        meta["status"] = "network-error"
        meta["error_type"] = type(error).__name__
        meta["error_message"] = str(error)
        return None, meta

    try:
        payload: Any = json.loads(raw.decode("utf-8-sig"))
    except Exception:
        meta["status"] = "invalid-json"
        return None, meta
    if isinstance(payload, dict):
        meta["status"] = "ok"
        return payload, meta
    meta["status"] = "invalid-payload"
    return None, meta


def _build_request_url(url: str, *, preferred_model: str | None) -> str:
    if not preferred_model:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["model"] = preferred_model
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query),
        parts.fragment,
    ))


def _should_retry(fetch_meta: dict[str, object]) -> bool:
    status = str(fetch_meta.get("status", "")).strip()
    if status in {"timeout", "network-error"}:
        return True
    if status == "http-error":
        status_code = _safe_int(fetch_meta.get("http_status"))
        return status_code == 429 or status_code >= 500
    return False


def _extract_success_total(report_payload: dict[str, object]) -> tuple[int, int]:
    success = _safe_int(report_payload.get("success"))
    total = _safe_int(report_payload.get("total"))
    if total > 0:
        return success, total
    results = report_payload.get("results")
    if not isinstance(results, list):
        return 0, 0
    total = len([item for item in results if isinstance(item, dict)])
    success = len(
        [
            item
            for item in results
            if isinstance(item, dict) and item.get("success") is not False
        ]
    )
    return success, total


def _extract_run_id(
    payload: dict[str, object],
    report_payload: dict[str, object],
) -> str | None:
    for source in (
        payload.get("run_id"),
        report_payload.get("run_id"),
    ):
        if isinstance(source, str) and source.strip():
            return source.strip()
    manifest = payload.get("manifest")
    if isinstance(manifest, dict):
        source = manifest.get("run_id")
        if isinstance(source, str) and source.strip():
            return source.strip()
    return None


def _extract_manifest_path(
    payload: dict[str, object],
    report_payload: dict[str, object],
) -> str | None:
    for source in (
        payload.get("manifest_path"),
        payload.get("manifest_url"),
        report_payload.get("manifest_path"),
    ):
        if isinstance(source, str) and source.strip():
            return source.strip()
    manifest = payload.get("manifest")
    if isinstance(manifest, dict):
        for key in ("path", "url"):
            source = manifest.get(key)
            if isinstance(source, str) and source.strip():
                return source.strip()
    return None


def _safe_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return 0
