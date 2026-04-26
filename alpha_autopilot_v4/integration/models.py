from __future__ import annotations

from dataclasses import dataclass

from ..plot_generation.models import PlotGenerationResult


@dataclass(frozen=True)
class V4IntegrationPayload:
    chapter_context: dict[str, object]
    v3_retention_context: dict[str, object]
    plot_generation_result: PlotGenerationResult


@dataclass(frozen=True)
class V4ToV3BridgeResult:
    enabled: bool
    retention_sort_key: str
    plot_generation_result: PlotGenerationResult
    v3_context: dict[str, object]
    fallback_reason: str | None = None
    qc_summary: dict[str, object] | None = None
