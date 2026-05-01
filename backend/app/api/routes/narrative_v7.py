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
    StoryStateMarketAdapter,
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
    BenchmarkMaintenanceAlertResponse,
    BenchmarkMaintenanceAlertArchiveResponse,
    BenchmarkMaintenanceAlertArchiveListResponse,
    BenchmarkMaintenanceAlertArchiveReadResponse,
    BenchmarkMaintenanceAlertArchiveCleanupResponse,
    BenchmarkMaintenanceAlertAutoArchiveResponse,
    BenchmarkMaintenanceAlertGovernanceReportResponse,
    BenchmarkMaintenanceAlertGovernanceRunListResponse,
    BenchmarkMaintenanceAlertGovernanceRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunResponse,
    BenchmarkMaintenanceAlertGovernanceRunSummaryResponse,
    BenchmarkMaintenanceAlertDigestResponse,
    BenchmarkMaintenanceAlertEmitResponse,
    BenchmarkMaintenanceAlertExportResponse,
    BenchmarkMaintenanceAlertListResponse,
    BenchmarkMaintenanceAlertPruneResponse,
    BenchmarkMaintenanceAlertSummaryResponse,
    BenchmarkMaintenanceReportResponse,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionDiffResponse,
    BenchmarkVersionAutoRemediateResponse,
    BenchmarkVersionHealthResponse,
    BenchmarkVersionListResponse,
    BenchmarkVersionPruneResponse,
    BenchmarkVersionRepairResponse,
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
    StoryStateMarketAdaptRequest,
    StoryStateMarketAdaptResponse,
    UnifiedDecisionPreviewRequest,
    UnifiedDecisionPreviewResponse,
)

router = APIRouter(prefix="/api/narrative/v7", tags=["narrative_v7"])

_sampler = NQMSampler()
_market_state_adapter = StoryStateMarketAdapter()
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


@router.post("/market-state/adapt", response_model=StoryStateMarketAdaptResponse)
def adapt_market_state(payload: StoryStateMarketAdaptRequest) -> StoryStateMarketAdaptResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/market-state/adapt",
        feature_name="market_state_adapter",
        operation=lambda: _market_state_adapter.adapt(payload),
    )


@router.post("/decision/preview", response_model=UnifiedDecisionPreviewResponse)
def decision_preview(payload: UnifiedDecisionPreviewRequest) -> UnifiedDecisionPreviewResponse:
    def _op() -> UnifiedDecisionPreviewResponse:
        adapted = _market_state_adapter.adapt(
            StoryStateMarketAdaptRequest(
                story_state=payload.story_state,
                project_state=payload.project_state,
                benchmark_state=payload.benchmark_state,
                metric_overrides=payload.metric_overrides,
                decision_state=payload.decision_state,
            )
        )
        sample = _sampler.sample(
            NQMSampleRequest(
                text=payload.text,
                story_state=adapted.market_state.story_state,
                character_states=payload.character_states,
                benchmark_parameters=adapted.market_state.benchmark_state,
            )
        )
        decision = _decision_controller.decide(
            DecisionRequest(
                market_state=adapted.market_state,
                vector=sample.vector,
                ohlcv=sample.ohlcv,
                override_confirmed=payload.override_confirmed,
            )
        )
        return UnifiedDecisionPreviewResponse(
            market_state=adapted.market_state,
            vector=sample.vector,
            ohlcv=sample.ohlcv,
            decision=decision.decision,
            defaults_applied=adapted.defaults_applied,
        )

    return _execute_with_metrics(
        route="/api/narrative/v7/decision/preview",
        feature_name="decision_preview",
        operation=_op,
        route_id_getter=lambda item: item.decision.route_id,
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


@router.get("/benchmark/versions/health", response_model=BenchmarkVersionHealthResponse)
def benchmark_versions_health() -> BenchmarkVersionHealthResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions/health",
        feature_name="benchmark_versions_health",
        operation=lambda: _benchmark_library.scan_version_health(),
    )


@router.post("/benchmark/versions/repair", response_model=BenchmarkVersionRepairResponse)
def benchmark_versions_repair(dry_run: bool = Query(default=True)) -> BenchmarkVersionRepairResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions/repair",
        feature_name="benchmark_versions_repair",
        operation=lambda: _benchmark_library.repair_versions(dry_run=dry_run),
    )


@router.get("/benchmark/maintenance/report", response_model=BenchmarkMaintenanceReportResponse)
def benchmark_maintenance_report(limit: int = Query(default=50, ge=1, le=500)) -> BenchmarkMaintenanceReportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/report",
        feature_name="benchmark_maintenance_report",
        operation=lambda: _benchmark_library.build_maintenance_report(limit=limit),
    )


@router.get("/benchmark/maintenance/alert", response_model=BenchmarkMaintenanceAlertResponse)
def benchmark_maintenance_alert(limit: int = Query(default=50, ge=1, le=500)) -> BenchmarkMaintenanceAlertResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alert",
        feature_name="benchmark_maintenance_alert",
        operation=lambda: _benchmark_library.build_maintenance_alert(limit=limit),
    )


@router.post("/benchmark/maintenance/alert/emit", response_model=BenchmarkMaintenanceAlertEmitResponse)
def benchmark_maintenance_alert_emit(limit: int = Query(default=50, ge=1, le=500)) -> BenchmarkMaintenanceAlertEmitResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alert/emit",
        feature_name="benchmark_maintenance_alert_emit",
        operation=lambda: _benchmark_library.emit_maintenance_alert(limit=limit),
    )


@router.get("/benchmark/maintenance/alerts", response_model=BenchmarkMaintenanceAlertListResponse)
def benchmark_maintenance_alert_list(
    limit: int = Query(default=100, ge=1, le=2000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts",
        feature_name="benchmark_maintenance_alert_list",
        operation=lambda: _benchmark_library.list_maintenance_alerts(limit=limit, cursor=cursor),
    )


@router.post("/benchmark/maintenance/alerts/prune", response_model=BenchmarkMaintenanceAlertPruneResponse)
def benchmark_maintenance_alert_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/prune",
        feature_name="benchmark_maintenance_alert_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alerts(keep_last=keep_last, dry_run=dry_run),
    )


@router.post("/benchmark/maintenance/alerts/archive", response_model=BenchmarkMaintenanceAlertArchiveResponse)
def benchmark_maintenance_alert_archive(
    keep_last: int = Query(default=1000, ge=0, le=2000000),
    shard_size: int = Query(default=1000, ge=1, le=500000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertArchiveResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/archive",
        feature_name="benchmark_maintenance_alert_archive",
        operation=lambda: _benchmark_library.archive_maintenance_alerts(
            keep_last=keep_last,
            shard_size=shard_size,
            dry_run=dry_run,
        ),
    )


@router.get("/benchmark/maintenance/alerts/archive/files", response_model=BenchmarkMaintenanceAlertArchiveListResponse)
def benchmark_maintenance_alert_archive_files(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertArchiveListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/archive/files",
        feature_name="benchmark_maintenance_alert_archive_files",
        operation=lambda: _benchmark_library.list_maintenance_alert_archive_files(limit=limit),
    )


@router.get("/benchmark/maintenance/alerts/archive/read", response_model=BenchmarkMaintenanceAlertArchiveReadResponse)
def benchmark_maintenance_alert_archive_read(
    file_name: str = Query(min_length=1),
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertArchiveReadResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/archive/read",
        feature_name="benchmark_maintenance_alert_archive_read",
        operation=lambda: _benchmark_library.read_maintenance_alert_archive_file(
            file_name=file_name,
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post("/benchmark/maintenance/alerts/auto-archive", response_model=BenchmarkMaintenanceAlertAutoArchiveResponse)
def benchmark_maintenance_alert_auto_archive(dry_run: bool = Query(default=True)) -> BenchmarkMaintenanceAlertAutoArchiveResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/auto-archive",
        feature_name="benchmark_maintenance_alert_auto_archive",
        operation=lambda: _benchmark_library.auto_archive_maintenance_alerts(dry_run=dry_run),
    )


@router.post("/benchmark/maintenance/alerts/archive/cleanup", response_model=BenchmarkMaintenanceAlertArchiveCleanupResponse)
def benchmark_maintenance_alert_archive_cleanup(dry_run: bool = Query(default=True)) -> BenchmarkMaintenanceAlertArchiveCleanupResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/archive/cleanup",
        feature_name="benchmark_maintenance_alert_archive_cleanup",
        operation=lambda: _benchmark_library.cleanup_maintenance_alert_archives(dry_run=dry_run),
    )


@router.get("/benchmark/maintenance/alerts/governance/report", response_model=BenchmarkMaintenanceAlertGovernanceReportResponse)
def benchmark_maintenance_alert_governance_report(
    alert_limit: int = Query(default=200, ge=1, le=20000),
    archive_limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceReportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/report",
        feature_name="benchmark_maintenance_alert_governance_report",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_report(
            alert_limit=alert_limit,
            archive_limit=archive_limit,
        ),
    )


@router.post("/benchmark/maintenance/alerts/governance/run", response_model=BenchmarkMaintenanceAlertGovernanceRunResponse)
def benchmark_maintenance_alert_governance_run(
    dry_run: bool = Query(default=True),
    alert_limit: int = Query(default=200, ge=1, le=20000),
    archive_limit: int = Query(default=200, ge=1, le=20000),
    idempotency_key: str = Query(default="", max_length=200),
    retry_run_id: str = Query(default="", max_length=120),
) -> BenchmarkMaintenanceAlertGovernanceRunResponse:
    def _op() -> BenchmarkMaintenanceAlertGovernanceRunResponse:
        try:
            return _benchmark_library.run_maintenance_alert_governance(
                dry_run=dry_run,
                alert_limit=alert_limit,
                archive_limit=archive_limit,
                idempotency_key=idempotency_key,
                retry_run_id=retry_run_id,
            )
        except ValueError as exc:
            detail = str(exc)
            if detail == "idempotency_key_reused_with_different_request":
                raise HTTPException(status_code=409, detail=detail) from exc
            if detail == "retry_target_not_found":
                raise HTTPException(status_code=404, detail=detail) from exc
            if detail == "retry_target_not_failed":
                raise HTTPException(status_code=422, detail=detail) from exc
            if detail == "retry_attempt_limit_exceeded":
                raise HTTPException(status_code=422, detail=detail) from exc
            raise

    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/run",
        feature_name="benchmark_maintenance_alert_governance_run",
        operation=_op,
    )


@router.get("/benchmark/maintenance/alerts/governance/runs", response_model=BenchmarkMaintenanceAlertGovernanceRunListResponse)
def benchmark_maintenance_alert_governance_runs(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceRunListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs",
        feature_name="benchmark_maintenance_alert_governance_runs",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_runs(limit=limit, cursor=cursor),
    )


@router.post("/benchmark/maintenance/alerts/governance/runs/prune", response_model=BenchmarkMaintenanceAlertGovernanceRunPruneResponse)
def benchmark_maintenance_alert_governance_runs_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceRunPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.get("/benchmark/maintenance/alerts/governance/runs/summary", response_model=BenchmarkMaintenanceAlertGovernanceRunSummaryResponse)
def benchmark_maintenance_alert_governance_runs_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceRunSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_runs(limit=limit),
    )


@router.get("/benchmark/maintenance/alerts/governance/runs/export", response_model=BenchmarkMaintenanceAlertGovernanceRunExportResponse)
def benchmark_maintenance_alert_governance_runs_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceRunExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/export",
        feature_name="benchmark_maintenance_alert_governance_runs_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_runs(limit=limit, cursor=cursor),
    )


@router.post("/benchmark/maintenance/alerts/governance/runs/auto-prune", response_model=BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse)
def benchmark_maintenance_alert_governance_runs_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_runs(dry_run=dry_run),
    )


@router.get("/benchmark/maintenance/alerts/governance/runs/digest", response_model=BenchmarkMaintenanceAlertGovernanceRunDigestResponse)
def benchmark_maintenance_alert_governance_runs_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceRunDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_runs_digest(limit=limit),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalation/emit",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse,
)
def benchmark_maintenance_alert_governance_runs_escalation_emit(
    limit: int = Query(default=200, ge=1, le=20000),
    ignore_cooldown: bool = Query(default=False),
) -> BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit",
        feature_name="benchmark_maintenance_alert_governance_runs_escalation_emit",
        operation=lambda: _benchmark_library.emit_maintenance_alert_governance_escalation(
            limit=limit,
            ignore_cooldown=ignore_cooldown,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalations(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/summary",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_escalations(limit=limit),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/export",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationExportResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/export",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_escalations(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_escalations(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_escalations(dry_run=dry_run),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/digest",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_escalations_digest(limit=limit),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_escalations(
            dry_run=dry_run,
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalation_remediations(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/summary",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_escalation_remediations(limit=limit),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_escalation_remediations(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_escalation_remediations(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_escalation_remediations(
            dry_run=dry_run,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_escalation_remediations_digest(limit=limit),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_escalation_remediations(
            dry_run=dry_run,
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/summary",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/export",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/export",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            dry_run=dry_run,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/digest",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(
            limit=limit
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            dry_run=dry_run,
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/summary",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/export",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/export",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            dry_run=dry_run,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/digest",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_digest(
            limit=limit,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            dry_run=dry_run,
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/summary",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_summary(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/summary",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/export",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/export",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_export",
        operation=lambda: _benchmark_library.export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_prune(
    keep_last: int = Query(default=500, ge=0, le=200000),
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_prune",
        operation=lambda: _benchmark_library.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-prune",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoPruneResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_prune(
    dry_run: bool = Query(default=True),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoPruneResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-prune",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_prune",
        operation=lambda: _benchmark_library.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            dry_run=dry_run,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/digest",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunDigestResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_digest(
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/digest",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_digest(
            limit=limit,
        ),
    )


@router.post(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
            dry_run=dry_run,
            limit=limit,
        ),
    )


@router.get(
    "/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs",
    response_model=BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse,
)
def benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs(
    limit: int = Query(default=100, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs",
        feature_name="benchmark_maintenance_alert_governance_runs_escalations_auto_remediations_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs",
        operation=lambda: _benchmark_library.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_auto_remediate_runs(
            limit=limit,
            cursor=cursor,
        ),
    )


@router.post("/benchmark/maintenance/alerts/governance/runs/auto-remediate", response_model=BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse)
def benchmark_maintenance_alert_governance_runs_auto_remediate(
    dry_run: bool = Query(default=True),
    limit: int = Query(default=200, ge=1, le=20000),
    alert_limit: int = Query(default=200, ge=1, le=20000),
    archive_limit: int = Query(default=200, ge=1, le=20000),
) -> BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate",
        feature_name="benchmark_maintenance_alert_governance_runs_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_maintenance_alert_governance_runs(
            dry_run=dry_run,
            limit=limit,
            alert_limit=alert_limit,
            archive_limit=archive_limit,
        ),
    )


@router.get("/benchmark/maintenance/alerts/summary", response_model=BenchmarkMaintenanceAlertSummaryResponse)
def benchmark_maintenance_alert_summary(limit: int = Query(default=200, ge=1, le=20000)) -> BenchmarkMaintenanceAlertSummaryResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/summary",
        feature_name="benchmark_maintenance_alert_summary",
        operation=lambda: _benchmark_library.summarize_maintenance_alerts(limit=limit),
    )


@router.get("/benchmark/maintenance/alerts/digest", response_model=BenchmarkMaintenanceAlertDigestResponse)
def benchmark_maintenance_alert_digest(limit: int = Query(default=200, ge=1, le=20000)) -> BenchmarkMaintenanceAlertDigestResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/digest",
        feature_name="benchmark_maintenance_alert_digest",
        operation=lambda: _benchmark_library.build_maintenance_alert_digest(limit=limit),
    )


@router.get("/benchmark/maintenance/alerts/export", response_model=BenchmarkMaintenanceAlertExportResponse)
def benchmark_maintenance_alert_export(
    limit: int = Query(default=200, ge=1, le=20000),
    cursor: str = Query(default=""),
) -> BenchmarkMaintenanceAlertExportResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/maintenance/alerts/export",
        feature_name="benchmark_maintenance_alert_export",
        operation=lambda: _benchmark_library.export_maintenance_alerts(limit=limit, cursor=cursor),
    )


@router.post("/benchmark/versions/auto-remediate", response_model=BenchmarkVersionAutoRemediateResponse)
def benchmark_versions_auto_remediate(
    dry_run: bool = Query(default=True),
    keep_last: int = Query(default=50, ge=0, le=10000),
) -> BenchmarkVersionAutoRemediateResponse:
    return _execute_with_metrics(
        route="/api/narrative/v7/benchmark/versions/auto-remediate",
        feature_name="benchmark_versions_auto_remediate",
        operation=lambda: _benchmark_library.auto_remediate_versions(dry_run=dry_run, keep_last=keep_last),
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
