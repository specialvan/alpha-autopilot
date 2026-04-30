from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from time import perf_counter
from typing import Callable, TypeVar

from ...core.config import settings
from ...services.narrative_v7 import (
    AntiPatternRegistry,
    BenchmarkLibrary,
    DecisionFeedbackController,
    DeadlockRouter,
    EmotionSatisfactionScorer,
    ExpectationDebtManager,
    LoopStructureAnalyzer,
    NQMSampler,
    OpeningGate,
    PacingInformationFlowController,
    SellingPointContractGuard,
    ThresholdBandEngine,
    build_v7_observability_snapshot,
    create_default_v7_benchmark_store,
    create_default_v7_runtime_metrics_store,
)
from ...services.narrative_v7.schemas import (
    AntiPatternCheckRequest,
    AntiPatternCheckResponse,
    BenchmarkAuditExportResponse,
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionDiffResponse,
    BenchmarkVersionListResponse,
    BenchmarkVersionPruneResponse,
    DeadlockCheckRequest,
    DeadlockCheckResponse,
    DecisionRequest,
    DecisionResponse,
    EmotionSatisfactionRequest,
    EmotionSatisfactionResponse,
    HookGuardRequest,
    HookGuardResponse,
    LoopStructureRequest,
    LoopStructureResponse,
    NQMSampleRequest,
    NQMSampleResponse,
    NQMVector,
    NarrativeMetricOHLCV,
    OpeningGateRequest,
    OpeningGateResponse,
    PacingRequest,
    PacingResponse,
)

router = APIRouter(prefix="/api/narrative/v7", tags=["narrative_v7"])

_sampler = NQMSampler()
_threshold_engine = ThresholdBandEngine()
_decision_controller = DecisionFeedbackController(threshold_engine=_threshold_engine)
_opening_gate = OpeningGate()
_expectation_manager = ExpectationDebtManager()
_deadlock_router = DeadlockRouter()
_antipattern_registry = AntiPatternRegistry()
_emotion_scorer = EmotionSatisfactionScorer()
_loop_analyzer = LoopStructureAnalyzer()
_pacing_controller = PacingInformationFlowController()
_benchmark_store = create_default_v7_benchmark_store()
_benchmark_library = BenchmarkLibrary(store=_benchmark_store)
_contract_guard = SellingPointContractGuard()
_runtime_metrics_store = create_default_v7_runtime_metrics_store()


class ThresholdPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector: NQMVector
    benchmark_parameters: BenchmarkParameterSet = Field(default_factory=BenchmarkParameterSet)
    ohlcv: NarrativeMetricOHLCV = Field(default_factory=NarrativeMetricOHLCV)


class ThresholdPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone: str
    dominant_pattern: str
    bands: dict[str, dict[str, float]] = Field(default_factory=dict)


_ReturnT = TypeVar("_ReturnT")


def _ensure_enabled(*, feature_name: str, feature_enabled: bool = True) -> None:
    if not settings.v7_enabled:
        raise HTTPException(status_code=503, detail="v7_disabled")
    if not feature_enabled:
        raise HTTPException(status_code=503, detail=f"{feature_name}_disabled")


def _record_call(
    *,
    route: str,
    started_at: float,
    status: str,
    error_type: str | None = None,
    http_status: int | None = None,
    route_id: str | None = None,
) -> None:
    _runtime_metrics_store.append_metric(
        route=route,
        status=status,
        latency_ms=(perf_counter() - started_at) * 1000.0,
        error_type=error_type,
        http_status=http_status,
        route_id=route_id,
    )


def _execute_with_metrics(
    *,
    route: str,
    operation: Callable[[], _ReturnT],
    feature_name: str,
    feature_enabled: bool = True,
    route_id_getter: Callable[[_ReturnT], str | None] | None = None,
) -> _ReturnT:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    route_id: str | None = None

    try:
        _ensure_enabled(feature_name=feature_name, feature_enabled=feature_enabled)
        result = operation()
        if route_id_getter:
            route_id = route_id_getter(result)
        return result
    except HTTPException as exc:
        status = "error"
        error_type = "HTTPException"
        http_status = exc.status_code
        raise
    except Exception as exc:
        status = "error"
        error_type = type(exc).__name__
        http_status = 500
        raise
    finally:
        _record_call(
            route=route,
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
            route_id=route_id,
        )


@router.post("/sample", response_model=NQMSampleResponse)
def sample_nqm(payload: NQMSampleRequest) -> NQMSampleResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/sample",
        feature_name="sample",
        operation=lambda: _sampler.sample(payload),
    )


@router.post("/thresholds/preview", response_model=ThresholdPreviewResponse)
def preview_thresholds(payload: ThresholdPreviewRequest) -> ThresholdPreviewResponse:
    def _op() -> ThresholdPreviewResponse:
        bands = _threshold_engine.build_metric_bands(payload.vector, payload.benchmark_parameters)
        dominant_band = bands.get("T8") or next(iter(bands.values()))
        zone = _threshold_engine.classify_zone(payload.vector.composite, payload.benchmark_parameters)
        pattern = _threshold_engine.detect_pattern(
            payload.ohlcv.open,
            payload.ohlcv.close,
            payload.ohlcv.volume,
            dominant_band,
        )
        return ThresholdPreviewResponse(
            zone=zone,
            dominant_pattern=pattern,
            bands={
                key: {
                    "support": value.support,
                    "resistance": value.resistance,
                    "stop_loss": value.stop_loss,
                    "breakout_confirm": value.breakout_confirm,
                }
                for key, value in bands.items()
            },
        )

    return _execute_with_metrics(
        route="/api/narrative/v7/thresholds/preview",
        feature_name="threshold_preview",
        operation=_op,
    )


@router.post("/decision", response_model=DecisionResponse)
def decide(payload: DecisionRequest) -> DecisionResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/decision",
        feature_name="decision",
        operation=lambda: _decision_controller.decide(payload),
        route_id_getter=lambda item: item.decision.route_id,
    )


@router.get("/decision/rules", response_model=dict)
def decision_rules() -> dict[str, object]:
    return _execute_with_metrics(
        route="/api/narrative/v7/decision/rules",
        feature_name="decision_rules",
        operation=lambda: _decision_controller.describe_rules(),
    )


@router.post("/opening-gate", response_model=OpeningGateResponse)
def opening_gate(payload: OpeningGateRequest) -> OpeningGateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/opening-gate",
        feature_name="opening_gate",
        feature_enabled=settings.v7_opening_gate_enabled,
        operation=lambda: _opening_gate.run(payload),
    )


@router.post("/hook-guard", response_model=HookGuardResponse)
def hook_guard(payload: HookGuardRequest) -> HookGuardResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/hook-guard",
        feature_name="hook_guard",
        operation=lambda: _expectation_manager.check_hook_guard(payload),
    )


@router.post("/deadlock/check", response_model=DeadlockCheckResponse)
def deadlock_check(payload: DeadlockCheckRequest) -> DeadlockCheckResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/deadlock/check",
        feature_name="deadlock_router",
        feature_enabled=settings.v7_deadlock_router_enabled,
        operation=lambda: _deadlock_router.check_and_route(payload),
    )


@router.post("/antipattern/check", response_model=AntiPatternCheckResponse)
def antipattern_check(payload: AntiPatternCheckRequest) -> AntiPatternCheckResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/antipattern/check",
        feature_name="antipattern_guard",
        feature_enabled=settings.v7_antipattern_guard_enabled,
        operation=lambda: _antipattern_registry.evaluate(payload),
    )


@router.post("/emotion/score", response_model=EmotionSatisfactionResponse)
def emotion_score(payload: EmotionSatisfactionRequest) -> EmotionSatisfactionResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/emotion/score",
        feature_name="emotion_score",
        operation=lambda: _emotion_scorer.score(payload),
    )


@router.post("/loop/analyze", response_model=LoopStructureResponse)
def loop_analyze(payload: LoopStructureRequest) -> LoopStructureResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/loop/analyze",
        feature_name="loop_analyze",
        operation=lambda: _loop_analyzer.analyze(payload),
    )


@router.post("/pacing/evaluate", response_model=PacingResponse)
def pacing_evaluate(payload: PacingRequest) -> PacingResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/pacing/evaluate",
        feature_name="pacing_evaluate",
        operation=lambda: _pacing_controller.evaluate(payload),
    )


@router.post("/benchmark/ingest", response_model=BenchmarkIngestResponse)
def benchmark_ingest(payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
    def _op() -> BenchmarkIngestResponse:
        result = _benchmark_library.ingest_sample(payload)
        if not result.accepted:
            status_code = 422 if result.message == "empty_sample_payload" else 409
            raise HTTPException(status_code=status_code, detail=result.message or "benchmark_ingest_conflict")
        return result

    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/ingest",
        feature_name="benchmark_ingest",
        operation=_op,
    )


@router.post("/benchmark/query", response_model=BenchmarkQueryResponse)
def benchmark_query(payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/query",
        feature_name="benchmark_query",
        operation=lambda: _benchmark_library.query_benchmark(payload),
    )


@router.delete("/benchmark/{book_id}", response_model=dict)
def benchmark_retract(book_id: str) -> dict[str, bool]:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/{book_id}",
        feature_name="benchmark_retract",
        operation=lambda: {"retracted": _benchmark_library.retract_sample(book_id)},
    )


@router.get("/benchmark/versions", response_model=BenchmarkVersionListResponse)
def benchmark_versions(limit: int = Query(default=20, ge=1, le=200)) -> BenchmarkVersionListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions",
        feature_name="benchmark_versions",
        operation=lambda: BenchmarkVersionListResponse(versions=_benchmark_library.list_versions(limit=limit)),
    )


@router.post("/benchmark/restore/{version}", response_model=BenchmarkRestoreResponse)
def benchmark_restore(version: str) -> BenchmarkRestoreResponse:
    def _op() -> BenchmarkRestoreResponse:
        result = _benchmark_library.restore_version(version)
        if not result.restored:
            raise HTTPException(status_code=404, detail=result.message or "benchmark_version_not_found")
        return result

    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/restore/{version}",
        feature_name="benchmark_restore",
        operation=_op,
    )


@router.get("/benchmark/versions/diff", response_model=BenchmarkVersionDiffResponse)
def benchmark_versions_diff(
    base_version: str = Query(min_length=1),
    target_version: str = Query(min_length=1),
) -> BenchmarkVersionDiffResponse:
    def _op() -> BenchmarkVersionDiffResponse:
        result = _benchmark_library.compare_versions(base_version=base_version, target_version=target_version)
        if not result.comparable:
            if result.message in {"base_version_not_found", "target_version_not_found"}:
                raise HTTPException(status_code=404, detail=result.message)
            raise HTTPException(status_code=422, detail=result.message or "benchmark_versions_not_comparable")
        return result

    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions/diff",
        feature_name="benchmark_versions_diff",
        operation=_op,
    )


@router.get("/benchmark/audit/export", response_model=BenchmarkAuditExportResponse)
def benchmark_audit_export(limit: int = Query(default=50, ge=1, le=200)) -> BenchmarkAuditExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/audit/export",
        feature_name="benchmark_audit_export",
        operation=lambda: _benchmark_library.export_audit(limit=limit),
    )


@router.post("/benchmark/versions/prune", response_model=BenchmarkVersionPruneResponse)
def benchmark_versions_prune(
    keep_last: int = Query(default=50, ge=0, le=10000),
    dry_run: bool = Query(default=True),
) -> BenchmarkVersionPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions/prune",
        feature_name="benchmark_versions_prune",
        operation=lambda: _benchmark_library.prune_versions(keep_last=keep_last, dry_run=dry_run),
    )


@router.post("/contract/evaluate", response_model=dict)
def contract_evaluate(payload: DecisionRequest) -> dict[str, object]:
    return _execute_with_metrics(
        route="/api/narrative/v7/contract/evaluate",
        feature_name="contract_evaluate",
        operation=lambda: _contract_guard.evaluate(payload.market_state, payload.vector),
    )


@router.get("/observability", response_model=dict)
def observability(limit: int = Query(default=500, ge=10, le=5000)) -> dict[str, object]:
    return _execute_with_metrics(
        route="/api/narrative/v7/observability",
        feature_name="observability",
        operation=lambda: build_v7_observability_snapshot(_runtime_metrics_store, limit=limit),
    )
