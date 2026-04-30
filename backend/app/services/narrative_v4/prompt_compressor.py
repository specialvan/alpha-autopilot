from __future__ import annotations

import re
from typing import Callable, Literal


PromptCompressionMode = Literal["bullet", "headline"]
CoverageJudge = Callable[[str, str], float]


class PromptCompressor:
    def __init__(
        self,
        *,
        threshold_tokens: int = 2000,
        target_ratio: float = 0.3,
        enabled: bool = True,
        coverage_judge: CoverageJudge | None = None,
    ) -> None:
        self.threshold_tokens = max(1, int(threshold_tokens))
        self.target_ratio = max(0.05, min(1.0, float(target_ratio)))
        self.enabled = bool(enabled)
        self.coverage_judge = coverage_judge

    def compress(
        self,
        doc: str,
        mode: PromptCompressionMode = "bullet",
        *,
        compress: bool = True,
    ) -> dict[str, object]:
        text = str(doc or "")
        original_tokens = self.estimate_tokens(text)
        if not self.enabled or not compress:
            return {
                "text": text,
                "triggered": False,
                "fallback_used": False,
                "mode": mode,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "compression_ratio": 1.0 if original_tokens > 0 else 0.0,
                "coverage_score": 1.0,
                "coverage_source": "passthrough",
            }
        if original_tokens <= self.threshold_tokens:
            return {
                "text": text,
                "triggered": False,
                "fallback_used": False,
                "mode": mode,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "compression_ratio": 1.0 if original_tokens > 0 else 0.0,
                "coverage_score": 1.0,
                "coverage_source": "passthrough",
            }

        try:
            compressed = self._compress_text(text, mode=mode)
            compressed = self._enforce_ratio(compressed, original_tokens=original_tokens)
            compressed_tokens = self.estimate_tokens(compressed)
            if compressed_tokens == 0:
                raise ValueError("empty-compression-output")
            coverage_score, coverage_source = self.constraint_coverage(
                text,
                compressed,
            )
            return {
                "text": compressed,
                "triggered": True,
                "fallback_used": False,
                "mode": mode,
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_ratio": round(compressed_tokens / max(1, original_tokens), 4),
                "coverage_score": coverage_score,
                "coverage_source": coverage_source,
            }
        except Exception:
            return {
                "text": text,
                "triggered": True,
                "fallback_used": True,
                "mode": mode,
                "original_tokens": original_tokens,
                "compressed_tokens": original_tokens,
                "compression_ratio": 1.0 if original_tokens > 0 else 0.0,
                "coverage_score": 1.0,
                "coverage_source": "fallback_passthrough",
            }

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        chunks = re.findall(r"\S+", text)
        # Lightweight approximation that stays stable in tests.
        return max(1, int(round(sum(max(1, len(chunk) // 4) for chunk in chunks))))

    def constraint_coverage_score(self, original: str, compressed: str) -> float:
        score, _source = self.constraint_coverage(original, compressed)
        return score

    def constraint_coverage(self, original: str, compressed: str) -> tuple[float, str]:
        if self.coverage_judge is not None:
            try:
                judged = float(self.coverage_judge(original, compressed))
                return round(_clip01(judged), 4), "llm_judge"
            except Exception:
                # If judge integration fails, we continue with deterministic fallback.
                pass

        original_constraints = _extract_constraint_lines(original)
        if not original_constraints:
            return 1.0, "heuristic"
        compressed_text = compressed.lower()
        kept = sum(
            1
            for line in original_constraints
            if _constraint_line_preserved(line, compressed_text)
        )
        source = "heuristic_fallback" if self.coverage_judge is not None else "heuristic"
        return round(kept / max(1, len(original_constraints)), 4), source

    def _compress_text(self, text: str, *, mode: PromptCompressionMode) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if mode == "headline":
            headlines = [
                line for line in lines
                if line.startswith("#") or line.endswith(":")
            ]
            if headlines:
                return "\n".join(headlines)
            return "\n".join(lines[:12])

        bullets: list[str] = []
        for line in lines:
            sentence = line.split(".")[0].strip()
            if sentence:
                bullets.append(f"- {sentence}")
        return "\n".join(bullets[:32])

    def _enforce_ratio(self, compressed: str, *, original_tokens: int) -> str:
        max_tokens = max(1, int(original_tokens * self.target_ratio))
        current = compressed
        while self.estimate_tokens(current) > max_tokens:
            lines = [line for line in current.splitlines() if line.strip()]
            if len(lines) <= 1:
                break
            current = "\n".join(lines[:-1])
        return current


def _extract_constraint_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [
        line
        for line in lines
        if any(token in line.lower() for token in ("must", "should", "require", "rule"))
    ]


def _constraint_line_preserved(line: str, compressed_text: str) -> bool:
    words = re.findall(r"[a-zA-Z]{4,}", line.lower())
    if not words:
        return True
    keywords = [word for word in words if word not in {"rule", "must", "should"}]
    sample = keywords[:4] if keywords else words[:4]
    hits = sum(1 for word in sample if word in compressed_text)
    required_hits = 1 if len(sample) <= 2 else 2
    return hits >= required_hits


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))
