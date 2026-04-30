from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

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
    create_default_v7_benchmark_store,
)
from ...services.narrative_v7.schemas import (
    AntiPatternCheckRequest,
    AntiPatternCheckResponse,
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
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


@router.post("/sample", response_model=NQMSampleResponse)
def sample_nqm(payload: NQMSampleRequest) -> NQMSampleResponse:
    return _sampler.sample(payload)


@router.post("/thresholds/preview", response_model=ThresholdPreviewResponse)
def preview_thresholds(payload: ThresholdPreviewRequest) -> ThresholdPreviewResponse:
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


@router.post("/decision", response_model=DecisionResponse)
def decide(payload: DecisionRequest) -> DecisionResponse:
    return _decision_controller.decide(payload)


@router.post("/opening-gate", response_model=OpeningGateResponse)
def opening_gate(payload: OpeningGateRequest) -> OpeningGateResponse:
    return _opening_gate.run(payload)


@router.post("/hook-guard", response_model=HookGuardResponse)
def hook_guard(payload: HookGuardRequest) -> HookGuardResponse:
    return _expectation_manager.check_hook_guard(payload)


@router.post("/deadlock/check", response_model=DeadlockCheckResponse)
def deadlock_check(payload: DeadlockCheckRequest) -> DeadlockCheckResponse:
    return _deadlock_router.check_and_route(payload)


@router.post("/antipattern/check", response_model=AntiPatternCheckResponse)
def antipattern_check(payload: AntiPatternCheckRequest) -> AntiPatternCheckResponse:
    return _antipattern_registry.evaluate(payload)


@router.post("/emotion/score", response_model=EmotionSatisfactionResponse)
def emotion_score(payload: EmotionSatisfactionRequest) -> EmotionSatisfactionResponse:
    return _emotion_scorer.score(payload)


@router.post("/loop/analyze", response_model=LoopStructureResponse)
def loop_analyze(payload: LoopStructureRequest) -> LoopStructureResponse:
    return _loop_analyzer.analyze(payload)


@router.post("/pacing/evaluate", response_model=PacingResponse)
def pacing_evaluate(payload: PacingRequest) -> PacingResponse:
    return _pacing_controller.evaluate(payload)


@router.post("/benchmark/ingest", response_model=BenchmarkIngestResponse)
def benchmark_ingest(payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
    return _benchmark_library.ingest_sample(payload)


@router.post("/benchmark/query", response_model=BenchmarkQueryResponse)
def benchmark_query(payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
    return _benchmark_library.query_benchmark(payload)


@router.delete("/benchmark/{book_id}", response_model=dict)
def benchmark_retract(book_id: str) -> dict[str, bool]:
    return {"retracted": _benchmark_library.retract_sample(book_id)}


@router.post("/contract/evaluate", response_model=dict)
def contract_evaluate(payload: DecisionRequest) -> dict[str, object]:
    return _contract_guard.evaluate(payload.market_state, payload.vector)
