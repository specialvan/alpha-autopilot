from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import tempfile
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.core.config import settings
from backend.app.services.narrative_v4.bridge import build_v4_bridge_payload_with_memory
from backend.app.services.narrative_v4.character_validation import CharacterValidationIssueList
from backend.app.services.narrative_v4.memory_store import V4MemoryStore


@dataclass(frozen=True)
class LLMCallRecord:
    purpose: str
    endpoint: str
    status: str
    latency_ms: float
    http_status: int | None = None
    error: str | None = None


class RemoteLLMClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 25.0,
        max_attempts_per_endpoint: int = 2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.max_attempts_per_endpoint = max(1, int(max_attempts_per_endpoint))
        self.call_records: list[LLMCallRecord] = []

    def generate_json(
        self,
        *,
        purpose: str,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int = 220,
    ) -> dict[str, Any]:
        attempts: list[tuple[str, dict[str, Any]]] = [
            (
                "/chat/completions",
                {
                    "model": self.model,
                    "temperature": 0,
                    "max_tokens": max_output_tokens,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            ),
            (
                "/responses",
                {
                    "model": self.model,
                    "temperature": 0,
                    "max_output_tokens": max_output_tokens,
                    "input": [
                        {
                            "role": "system",
                            "content": [{"type": "input_text", "text": system_prompt}],
                        },
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": user_prompt}],
                        },
                    ],
                },
            ),
        ]
        last_error: Exception | None = None
        for endpoint, payload in attempts:
            for _attempt_index in range(self.max_attempts_per_endpoint):
                try:
                    raw_response = self._post_json(endpoint=endpoint, payload=payload, purpose=purpose)
                    text = _extract_text_from_model_response(raw_response)
                    parsed = _extract_json_object(text)
                    if isinstance(parsed, dict):
                        return parsed
                    raise ValueError("model-output-is-not-json-object")
                except Exception as error:
                    last_error = error
                    if not _is_retryable_error(error):
                        break
                    continue
        raise RuntimeError(f"remote-llm-json-generation-failed: {last_error}") from last_error

    def _post_json(self, *, endpoint: str, payload: dict[str, Any], purpose: str) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        encoded = json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=encoded,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        started = perf_counter()
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
                latency_ms = (perf_counter() - started) * 1000.0
                parsed = json.loads(raw.decode("utf-8-sig"))
                self.call_records.append(
                    LLMCallRecord(
                        purpose=purpose,
                        endpoint=endpoint,
                        status="ok",
                        latency_ms=round(latency_ms, 2),
                        http_status=getattr(response, "status", None),
                    )
                )
                if isinstance(parsed, dict):
                    return parsed
                raise ValueError("remote-response-not-json-object")
        except HTTPError as error:
            latency_ms = (perf_counter() - started) * 1000.0
            self.call_records.append(
                LLMCallRecord(
                    purpose=purpose,
                    endpoint=endpoint,
                    status="http-error",
                    latency_ms=round(latency_ms, 2),
                    http_status=error.code,
                    error=str(error),
                )
            )
            raise
        except URLError as error:
            latency_ms = (perf_counter() - started) * 1000.0
            self.call_records.append(
                LLMCallRecord(
                    purpose=purpose,
                    endpoint=endpoint,
                    status="network-error",
                    latency_ms=round(latency_ms, 2),
                    error=str(error),
                )
            )
            raise
        except Exception as error:
            latency_ms = (perf_counter() - started) * 1000.0
            self.call_records.append(
                LLMCallRecord(
                    purpose=purpose,
                    endpoint=endpoint,
                    status="decode-error",
                    latency_ms=round(latency_ms, 2),
                    error=str(error),
                )
            )
            raise


@dataclass(frozen=True)
class CanaryResult:
    passed: bool
    reason: str
    report_path: Path


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_report_path(started_at: datetime) -> Path:
    timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    return (
        REPO_ROOT
        / "artifacts"
        / "production_cycles"
        / "v5_live_canary"
        / f"v5-live-llm-canary-{timestamp}.md"
    )


def _build_long_rule_document(rule_count: int = 900) -> str:
    return "\n".join(
        f"Rule {index}: must preserve continuity and should maintain strict causal logic with explicit payoff anchors."
        for index in range(rule_count)
    )


def _build_canary_characters() -> list[dict[str, object]]:
    return [
        {
            "id": "hero",
            "status": 0.22,
            "knowledge": 0.41,
            "emotion": 0.74,
            "interest_conflict": 0.62,
            "control": 0.51,
            "dependency": 0.33,
            "trust": 0.37,
            "impulsiveness": 0.8,
            "calmness": 0.88,
            "resilience": 0.7,
            "directness": 0.9,
            "pragmatism": 0.7,
            "idealism": 0.2,
            "assertiveness": 0.8,
            "avoidance": 0.1,
            "self_protection": 0.4,
            "sacrifice_tendency": 0.3,
            "risk_appetite": 0.8,
            "function_type": "disguise",
            "emotion_slider_map": {
                "baseline": {"stress_baseline": 8.1},
                "scene_overrides": {},
            },
        }
    ]


def _coverage_judge_with_remote_llm(
    client: RemoteLLMClient,
):
    def _judge(original: str, compressed: str) -> float:
        original_trimmed = original[:2200]
        compressed_trimmed = compressed[:2200]
        payload = client.generate_json(
            purpose="coverage_judge",
            system_prompt=(
                "You are a strict compression coverage evaluator. "
                "Return JSON only: {\"score\": float}. Score must be between 0 and 1."
            ),
            user_prompt=(
                "Evaluate whether compressed text preserves key MUST/SHOULD constraints.\n"
                f"Original:\n{original_trimmed}\n\n"
                f"Compressed:\n{compressed_trimmed}\n\n"
                "Return JSON only."
            ),
            max_output_tokens=120,
        )
        score = float(payload.get("score", 0.0))
        return max(0.0, min(1.0, score))

    return _judge


def _external_character_inspector_with_remote_llm(
    client: RemoteLLMClient,
):
    def _inspector(generated: list[dict[str, object]]) -> CharacterValidationIssueList:
        serialized = json.dumps(generated, ensure_ascii=False)[:2200]
        payload = client.generate_json(
            purpose="character_inspector",
            system_prompt=(
                "You are a character QA inspector. "
                "Return JSON only with schema: "
                "{\"issues\":[{\"field_path\":str,\"description\":str,\"suggested_value\":any}]}"
            ),
            user_prompt=(
                "Inspect character payload for consistency issues.\n"
                f"payload={serialized}\n"
                "Rules:\n"
                "1) Disguise role should include surface_relation and actual_relation.\n"
                "2) If stress_baseline>5 and calmness>0.8, suggest lowering calmness to <=0.7.\n"
                "Return JSON only."
            ),
            max_output_tokens=220,
        )
        issues = payload.get("issues", [])
        if not isinstance(issues, list):
            issues = []
        return CharacterValidationIssueList.model_validate({"issues": issues})

    return _inspector


def _run_live_canary() -> tuple[dict[str, object], list[LLMCallRecord]]:
    base_url = (settings.benchmark_base_url or "").strip()
    api_key = (settings.benchmark_api_key or "").strip()
    model = (settings.benchmark_model or "").strip()
    if not base_url or not api_key or not model:
        raise RuntimeError(
            "missing benchmark config: require BENCHMARK_BASE_URL, BENCHMARK_API_KEY, BENCHMARK_MODEL"
        )

    client = RemoteLLMClient(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )
    coverage_judge = _coverage_judge_with_remote_llm(client)
    external_inspector = _external_character_inspector_with_remote_llm(client)

    with tempfile.TemporaryDirectory(prefix="v5-live-canary-") as temp_dir:
        tmp = Path(temp_dir)
        memory_store = V4MemoryStore(
            relationship_path=tmp / "v4_relationship_memory.jsonl",
            feedback_path=tmp / "v4_feedback_memory.jsonl",
        )
        payload = build_v4_bridge_payload_with_memory(
            {
                "id": "v5-live-llm-canary",
                "chapter_index": 18,
                "v4_enabled": True,
                "character_validation_mode": "external",
                "_character_validation_inspector": external_inspector,
                "prompt_compress_coverage_mode": "llm_judge",
                "_prompt_compression_coverage_judge": coverage_judge,
                "characters": _build_canary_characters(),
                "pressure_items": [{"type": "survival", "intensity": 0.81}],
                "prompt_documents": {
                    "style_document": _build_long_rule_document(),
                    "core_instruction_document": "Must preserve causality and style consistency.",
                },
            },
            memory_store=memory_store,
            context_id="v5-live-llm-canary",
            history_window=20,
        )
    return payload, client.call_records


def _evaluate_pass_fail(payload: dict[str, object], call_records: list[LLMCallRecord]) -> tuple[bool, str]:
    logs = payload.get("prompt_compression_logs", [])
    validation = payload.get("character_validation", {})
    if not isinstance(logs, list) or not logs:
        return False, "missing prompt_compression_logs"
    if not isinstance(validation, dict):
        return False, "missing character_validation log payload"
    style_log = next(
        (item for item in logs if isinstance(item, dict) and item.get("document_key") == "style_document"),
        None,
    )
    if not isinstance(style_log, dict):
        return False, "missing style_document compression log"
    if style_log.get("coverage_source") != "llm_judge":
        return False, f"coverage_source not llm_judge: {style_log.get('coverage_source')}"
    if validation.get("mode_effective") != "external":
        return False, f"validation mode_effective not external: {validation.get('mode_effective')}"
    if validation.get("inspector_mode") != "external_judge":
        return False, f"inspector_mode not external_judge: {validation.get('inspector_mode')}"
    successful_remote_calls = [record for record in call_records if record.status == "ok"]
    if not successful_remote_calls:
        return False, "no successful remote llm calls recorded"
    return True, "live canary checks passed"


def _write_report(
    report_path: Path,
    *,
    started_at: datetime,
    ended_at: datetime,
    passed: bool,
    reason: str,
    payload: dict[str, object] | None,
    call_records: list[LLMCallRecord],
    error: Exception | None,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    duration_seconds = (ended_at - started_at).total_seconds()
    lines: list[str] = []
    lines.append("# V5 Live LLM Canary Report")
    lines.append("")
    lines.append(f"- started_at_utc: {_iso_utc(started_at)}")
    lines.append(f"- ended_at_utc: {_iso_utc(ended_at)}")
    lines.append(f"- duration_seconds: {duration_seconds:.2f}")
    lines.append(f"- verdict: {'PASS' if passed else 'FAIL'}")
    lines.append(f"- reason: {reason}")
    lines.append("")
    lines.append("## Runtime Config")
    lines.append("")
    lines.append(f"- benchmark_base_url_set: {bool((settings.benchmark_base_url or '').strip())}")
    lines.append(f"- benchmark_model: `{(settings.benchmark_model or '').strip() or 'missing'}`")
    lines.append(f"- benchmark_api_key_set: {bool((settings.benchmark_api_key or '').strip())}")
    lines.append("")
    lines.append("## Remote Call Records")
    lines.append("")
    lines.append("| purpose | endpoint | status | latency_ms | http_status | error |")
    lines.append("| --- | --- | --- | ---: | ---: | --- |")
    for row in call_records:
        lines.append(
            f"| {row.purpose} | `{row.endpoint}` | {row.status} | {row.latency_ms:.2f} | "
            f"{'' if row.http_status is None else row.http_status} | {'' if row.error is None else row.error} |"
        )
    if not call_records:
        lines.append("| n/a | n/a | n/a | 0.00 |  | no calls |")
    lines.append("")

    if payload is not None:
        lines.append("## Payload Highlights")
        lines.append("")
        prompt_logs = payload.get("prompt_compression_logs", [])
        validation_log = payload.get("character_validation", {})
        summary = payload.get("memory_summary", {})
        lines.append("### prompt_compression_logs")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(prompt_logs, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("### character_validation")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(validation_log, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
        lines.append("### memory_summary")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(summary, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    if error is not None:
        lines.append("## Error")
        lines.append("")
        lines.append("```text")
        lines.append(str(error))
        lines.append("```")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def _extract_text_from_model_response(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                chunks: list[str] = []
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        chunks.append(item["text"])
                if chunks:
                    return "\n".join(chunks)

    output_text = response.get("output_text")
    if isinstance(output_text, str):
        return output_text
    output = response.get("output")
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
        if chunks:
            return "\n".join(chunks)
    raise ValueError("unable-to-extract-model-text")


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("json-object-not-found-in-model-output")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("model-json-output-not-object")
    return parsed


def _is_retryable_error(error: Exception) -> bool:
    if isinstance(error, URLError):
        return True
    if isinstance(error, HTTPError):
        return error.code == 429 or error.code >= 500
    message = str(error).lower()
    return any(
        token in message
        for token in (
            "timed out",
            "timeout",
            "unexpected eof",
            "temporarily unavailable",
            "connection reset",
            "connection aborted",
        )
    )


def run(report_path: Path) -> CanaryResult:
    started_at = datetime.now(timezone.utc)
    payload: dict[str, object] | None = None
    call_records: list[LLMCallRecord] = []
    error: Exception | None = None
    passed = False
    reason = "not-run"
    try:
        payload, call_records = _run_live_canary()
        passed, reason = _evaluate_pass_fail(payload, call_records)
    except Exception as run_error:
        error = run_error
        reason = f"execution-error: {run_error}"
        passed = False
    ended_at = datetime.now(timezone.utc)
    _write_report(
        report_path,
        started_at=started_at,
        ended_at=ended_at,
        passed=passed,
        reason=reason,
        payload=payload,
        call_records=call_records,
        error=error,
    )
    return CanaryResult(
        passed=passed,
        reason=reason,
        report_path=report_path,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run V5 live LLM canary for external compression/validation hooks."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional markdown report path. Defaults to artifacts/production_cycles/v5_live_canary/...",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    started_at = datetime.now(timezone.utc)
    if args.output is None:
        report_path = _default_report_path(started_at)
    elif args.output.is_absolute():
        report_path = args.output
    else:
        report_path = (REPO_ROOT / args.output).resolve()
    result = run(report_path)
    print(f"[v5-live-canary] report: {result.report_path}")
    print(f"[v5-live-canary] verdict: {'PASS' if result.passed else 'FAIL'}")
    print(f"[v5-live-canary] reason: {result.reason}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
