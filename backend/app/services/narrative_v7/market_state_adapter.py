from __future__ import annotations

from typing import Any

from .schemas import (
    BenchmarkParameterSet,
    DecisionState,
    NarrativeMarketState,
    NovelProjectState,
    StoryStateMarketAdaptRequest,
    StoryStateMarketAdaptResponse,
    default_nqm_metrics,
)


class StoryStateMarketAdapter:
    def adapt(self, payload: StoryStateMarketAdaptRequest) -> StoryStateMarketAdaptResponse:
        defaults_applied: list[str] = []
        normalized_story_state = self._normalize_story_state(payload.story_state, defaults_applied=defaults_applied)
        project_state = self._resolve_project_state(
            payload.project_state,
            story_state=normalized_story_state,
            defaults_applied=defaults_applied,
        )
        benchmark_state = self._resolve_benchmark_state(
            payload.benchmark_state,
            project_state=project_state,
            defaults_applied=defaults_applied,
        )
        metric_state = self._resolve_metric_state(
            payload.metric_overrides,
            story_state=normalized_story_state,
            defaults_applied=defaults_applied,
        )
        decision_state = self._resolve_decision_state(
            payload.decision_state,
            metric_state=metric_state,
            defaults_applied=defaults_applied,
        )
        composite = decision_state.last_composite
        kline_state = {
            "open": composite,
            "high": composite,
            "low": composite,
            "close": composite,
            "volume": float(max(1, int(normalized_story_state.get("chapter_index", 1))) * 100),
        }

        market_state = NarrativeMarketState(
            project_state=project_state,
            story_state=normalized_story_state,
            benchmark_state=benchmark_state,
            metric_state=metric_state,
            kline_state=kline_state,
            threshold_state={},
            decision_state=decision_state,
        )
        return StoryStateMarketAdaptResponse(
            market_state=market_state,
            defaults_applied=self._dedupe(defaults_applied),
        )

    def _normalize_story_state(self, raw: dict[str, Any], *, defaults_applied: list[str]) -> dict[str, Any]:
        state = dict(raw)

        chapter_index = self._to_int(state.get("chapter_index"), 1)
        if chapter_index < 1:
            chapter_index = 1
            defaults_applied.append("story_state.chapter_index_clamped")
        if "chapter_index" not in state:
            defaults_applied.append("story_state.chapter_index_defaulted")
        state["chapter_index"] = chapter_index

        stage = str(state.get("stage", "unknown")).strip() or "unknown"
        if "stage" not in state or not str(state.get("stage", "")).strip():
            defaults_applied.append("story_state.stage_defaulted")
        state["stage"] = stage

        state["deadlock_triggered"] = bool(state.get("deadlock_triggered", False))
        state["antipattern_critical"] = bool(state.get("antipattern_critical", False))
        state["t9_delta_5chapters"] = self._to_float(state.get("t9_delta_5chapters"), 0.0)
        state["a6_sigma_delta"] = self._to_float(state.get("a6_sigma_delta"), 0.0)
        if "is_death_chapter" in state:
            state["is_death_chapter"] = bool(state.get("is_death_chapter"))
        else:
            state["is_death_chapter"] = self._contains_tag(state.get("tags"), "death")
            if state["is_death_chapter"]:
                defaults_applied.append("story_state.is_death_chapter_inferred_from_tags")
        return state

    def _resolve_project_state(
        self,
        value: NovelProjectState | None,
        *,
        story_state: dict[str, Any],
        defaults_applied: list[str],
    ) -> NovelProjectState:
        if value is not None:
            return value

        defaults_applied.append("project_state.defaulted")
        return NovelProjectState(
            project_id=str(story_state.get("project_id", "default-project")),
            platform=str(story_state.get("platform", "unknown")),
            genre_track=str(story_state.get("genre_track", "unknown")),
            reader_profile=str(story_state.get("reader_profile", "unknown")),
            ip_flavor_tag=str(story_state.get("ip_flavor_tag", story_state.get("macro_structure", "default"))),
            selling_point_contract=str(story_state.get("selling_point_contract", "")),
        )

    def _resolve_benchmark_state(
        self,
        value: BenchmarkParameterSet | None,
        *,
        project_state: NovelProjectState,
        defaults_applied: list[str],
    ) -> BenchmarkParameterSet:
        if value is not None:
            return value
        defaults_applied.append("benchmark_state.defaulted")
        return BenchmarkParameterSet(
            channel=project_state.platform,
            genre_track=project_state.genre_track,
        )

    def _resolve_metric_state(
        self,
        overrides: dict[str, float],
        *,
        story_state: dict[str, Any],
        defaults_applied: list[str],
    ) -> dict[str, float]:
        metrics = default_nqm_metrics()
        metrics["T8"] = self._clamp(self._to_float(story_state.get("foreshadowing_load"), 0.5))
        metrics["T4"] = self._clamp(self._to_float(story_state.get("payoff_pressure"), 0.5))
        metrics["T9"] = self._clamp(self._to_float(story_state.get("conflict_intensity"), 0.5))

        a6_sigma_delta = self._to_float(story_state.get("a6_sigma_delta"), 0.0)
        metrics["A6"] = self._clamp(0.5 + a6_sigma_delta * 0.1)

        if overrides:
            for key, raw in overrides.items():
                if key not in metrics:
                    continue
                metrics[key] = self._clamp(self._to_float(raw, metrics[key]))
            defaults_applied.append("metric_state.overrides_applied")
        else:
            defaults_applied.append("metric_state.defaults_from_story_state")
        return metrics

    def _resolve_decision_state(
        self,
        value: DecisionState | None,
        *,
        metric_state: dict[str, float],
        defaults_applied: list[str],
    ) -> DecisionState:
        if value is not None:
            return value

        defaults_applied.append("decision_state.defaulted")
        composite = (metric_state.get("T8", 0.5) + metric_state.get("T4", 0.5) + metric_state.get("T9", 0.5)) / 3.0
        return DecisionState(last_composite=self._clamp(composite))

    def _contains_tag(self, tags: object, needle: str) -> bool:
        if not isinstance(tags, list):
            return False
        normalized = needle.strip().lower()
        for item in tags:
            if isinstance(item, str) and item.strip().lower() == normalized:
                return True
        return False

    def _to_int(self, value: object, fallback: int) -> int:
        try:
            if value is None:
                return fallback
            return int(value)  # type: ignore[arg-type]
        except Exception:
            return fallback

    def _to_float(self, value: object, fallback: float) -> float:
        try:
            if value is None:
                return fallback
            return float(value)  # type: ignore[arg-type]
        except Exception:
            return fallback

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _dedupe(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
        return ordered
