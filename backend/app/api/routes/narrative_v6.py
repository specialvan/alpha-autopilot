from __future__ import annotations

from fastapi import APIRouter, HTTPException
from time import perf_counter

from ...core.config import settings
from ...services.narrative_v6.character_interview import CharacterInterviewService
from ...services.narrative_v6.character_parameterizer import CharacterParameterizer
from ...services.narrative_v6.conflict_probe import EmergentConflictProbeService
from ...services.narrative_v6.event_injection import EventInjectionService
from ...services.narrative_v6.graph_memory_store import create_default_v6_graph_memory_store
from ...services.narrative_v6.graph_rag import GraphRAGRetriever
from ...services.narrative_v6.group_memory import GroupMemoryService
from ...services.narrative_v6.observability import (
    build_v6_observability_snapshot,
    create_default_v6_runtime_metrics_store,
)
from ...services.narrative_v6.parallel_simulation import ParallelPlotSimulationService
from ...services.narrative_v6.schemas import (
    CharacterInterviewRequest,
    CharacterInterviewResponse,
    CharacterParameterizeRequest,
    CharacterParameterizeResponse,
    EmergentConflictProbeRequest,
    EmergentConflictProbeResult,
    EventInjectionRequest,
    EventInjectionResult,
    GraphRAGRetrieveRequest,
    GraphRAGRetrieveResponse,
    GroupMemoryApplyRequest,
    GroupMemoryGraph,
    NarrativeSeedExtractionRequest,
    NarrativeSeedExtractionResponse,
    ParallelPlotSimulationResult,
    ParallelSimulationRequest,
)
from ...services.narrative_v6.seed_extractor import NarrativeSeedExtractor
from ...services.narrative_v6.state_store import create_default_v6_simulation_store

router = APIRouter(prefix="/api/narrative/v6", tags=["narrative_v6"])

seed_extractor = NarrativeSeedExtractor()
character_parameterizer = CharacterParameterizer()
parallel_simulation_service = ParallelPlotSimulationService()
conflict_probe_service = EmergentConflictProbeService()
event_injection_service = EventInjectionService()
character_interview_service = CharacterInterviewService()
group_memory_service = GroupMemoryService()
simulation_store = create_default_v6_simulation_store()
runtime_metrics_store = create_default_v6_runtime_metrics_store()
graph_rag_retriever = GraphRAGRetriever()
graph_memory_store = create_default_v6_graph_memory_store()


def _ensure_enabled() -> None:
    if not settings.v6_enabled:
        raise HTTPException(status_code=503, detail="v6_disabled")


def _append_runtime_metric(
    *,
    route: str,
    started_at: float,
    status: str,
    simulation_id: str | None = None,
    path_count: int | None = None,
    failed_path_count: int | None = None,
    winner_path_id: str | None = None,
    fallback_reason: str | None = None,
    error_type: str | None = None,
    risk_flags: list[str] | None = None,
    http_status: int | None = None,
) -> None:
    runtime_metrics_store.append_metric(
        route=route,
        status=status,
        latency_ms=(perf_counter() - started_at) * 1000.0,
        simulation_id=simulation_id,
        path_count=path_count,
        failed_path_count=failed_path_count,
        winner_path_id=winner_path_id,
        fallback_reason=fallback_reason,
        error_type=error_type,
        risk_flags=risk_flags,
        http_status=http_status,
    )


def _build_default_simulation_graph_query(payload: ParallelSimulationRequest) -> str:
    if payload.graph_rag_query and payload.graph_rag_query.strip():
        return payload.graph_rag_query.strip()
    if payload.narrative_seed.open_threads:
        return payload.narrative_seed.open_threads[0].thread
    if payload.narrative_seed.plot_events:
        return payload.narrative_seed.plot_events[0].event
    return "main conflict direction"


def _build_default_interview_graph_query(payload: CharacterInterviewRequest) -> str:
    if payload.graph_rag_query and payload.graph_rag_query.strip():
        return payload.graph_rag_query.strip()
    return payload.user_message.strip()


def _safe_int(value: object) -> int | None:
    try:
        if value is None:
            return None
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None


def _stitch_hits(
    primary_hits: list,
    history_hits: list,
    *,
    top_k: int,
) -> list:
    merged = []
    seen: set[str] = set()

    for hit in primary_hits:
        key = str(getattr(hit, "summary", "")).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(hit)

    for hit in history_hits:
        key = str(getattr(hit, "summary", "")).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(hit)

    ranked = sorted(
        merged,
        key=lambda item: (
            float(getattr(item, "score", 0.0)),
            float(getattr(item, "confidence", 0.0)),
            str(getattr(item, "node_id", "")),
        ),
        reverse=True,
    )
    return ranked[: max(1, top_k)]


def _retrieve_graph_with_stitching(
    payload: GraphRAGRetrieveRequest,
    *,
    source_route: str,
    simulation_id: str | None = None,
) -> GraphRAGRetrieveResponse:
    base_result = graph_rag_retriever.retrieve(payload)
    history_hits = graph_memory_store.search_hits(
        query=payload.query,
        top_k=payload.top_k,
        include_hidden=payload.include_hidden,
        chapter_index=payload.chapter_index,
    )
    stitched_hits = _stitch_hits(base_result.hits, history_hits, top_k=payload.top_k)

    result = base_result.model_copy(deep=True)
    result.hits = stitched_hits
    result.stitched_from_history_count = len([item for item in stitched_hits if item.node_type == "history_memory"])
    result.history_recall_used = result.stitched_from_history_count > 0
    if result.history_recall_used:
        result.retrieval_mode = "deterministic_stitched"
    if result.fallback_used and result.history_recall_used:
        result.fallback_used = False
        result.fallback_reason = None

    graph_memory_store.append_hits(
        query=payload.query,
        hits=result.hits,
        source_route=source_route,
        chapter_index=payload.chapter_index,
        simulation_id=simulation_id,
    )
    return result


@router.post("/seed/extract", response_model=NarrativeSeedExtractionResponse)
def extract_narrative_seed(payload: NarrativeSeedExtractionRequest) -> NarrativeSeedExtractionResponse:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return seed_extractor.extract(payload)
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
        _append_runtime_metric(
            route="/api/narrative/v6/seed/extract",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/characters/parameterize", response_model=CharacterParameterizeResponse)
def parameterize_characters(payload: CharacterParameterizeRequest) -> CharacterParameterizeResponse:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return character_parameterizer.parameterize(payload)
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
        _append_runtime_metric(
            route="/api/narrative/v6/characters/parameterize",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/simulations/parallel", response_model=ParallelPlotSimulationResult)
def run_parallel_simulation(payload: ParallelSimulationRequest) -> ParallelPlotSimulationResult:
    started_at = perf_counter()
    status = "ok"
    simulation_id: str | None = None
    path_count: int | None = None
    failed_path_count: int | None = None
    winner_path_id: str | None = None
    fallback_reason: str | None = None
    error_type: str | None = None
    risk_flags: list[str] | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        graph_query = _build_default_simulation_graph_query(payload)
        retrieval = _retrieve_graph_with_stitching(
            GraphRAGRetrieveRequest(
                query=graph_query,
                narrative_seed=payload.narrative_seed,
                relationship_graph_input=payload.relationship_graph_input,
                group_memory_graph=payload.group_memory_graph,
                top_k=payload.graph_rag_top_k,
                include_hidden=payload.graph_rag_include_hidden,
                chapter_index=_safe_int(payload.story_state.get("chapter_index")),
            ),
            source_route="/api/narrative/v6/simulations/parallel",
            simulation_id=payload.simulation_id,
        )
        graph_rag_hints = [hit.summary for hit in retrieval.hits]
        result = parallel_simulation_service.run(payload, graph_rag_hints=graph_rag_hints)
        simulation_store.save(result)
        simulation_id = result.simulation_id
        path_count = len(result.paths)
        failed_path_count = len([path for path in result.paths if path.status == "failed"])
        winner_path_id = result.winner_path_id
        risk_flags = list(result.risk_flags)
        if retrieval.fallback_used and fallback_reason is None:
            status = "fallback"
            fallback_reason = retrieval.fallback_reason or "graph-rag-fallback"
        if result.winner_path_id is None:
            status = "fallback"
            fallback_reason = "no-valid-winner-path"
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
        _append_runtime_metric(
            route="/api/narrative/v6/simulations/parallel",
            started_at=started_at,
            status=status,
            simulation_id=simulation_id,
            path_count=path_count,
            failed_path_count=failed_path_count,
            winner_path_id=winner_path_id,
            fallback_reason=fallback_reason,
            error_type=error_type,
            risk_flags=risk_flags,
            http_status=http_status,
        )


@router.get("/simulations/{simulation_id}", response_model=ParallelPlotSimulationResult)
def get_parallel_simulation(simulation_id: str) -> ParallelPlotSimulationResult:
    started_at = perf_counter()
    status = "ok"
    path_count: int | None = None
    failed_path_count: int | None = None
    winner_path_id: str | None = None
    fallback_reason: str | None = None
    error_type: str | None = None
    risk_flags: list[str] | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        result = simulation_store.get(simulation_id)
        if result is None:
            status = "error"
            fallback_reason = "simulation-not-found"
            http_status = 404
            raise HTTPException(status_code=404, detail=f"simulation not found: {simulation_id}")

        path_count = len(result.paths)
        failed_path_count = len([path for path in result.paths if path.status == "failed"])
        winner_path_id = result.winner_path_id
        risk_flags = list(result.risk_flags)
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
        _append_runtime_metric(
            route="/api/narrative/v6/simulations/{simulation_id}",
            started_at=started_at,
            status=status,
            simulation_id=simulation_id,
            path_count=path_count,
            failed_path_count=failed_path_count,
            winner_path_id=winner_path_id,
            fallback_reason=fallback_reason,
            error_type=error_type,
            risk_flags=risk_flags,
            http_status=http_status,
        )


@router.post("/conflicts/probe", response_model=EmergentConflictProbeResult)
def probe_emergent_conflicts(payload: EmergentConflictProbeRequest) -> EmergentConflictProbeResult:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return conflict_probe_service.probe(payload)
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
        _append_runtime_metric(
            route="/api/narrative/v6/conflicts/probe",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/simulations/{simulation_id}/inject-event", response_model=EventInjectionResult)
def inject_event(simulation_id: str, payload: EventInjectionRequest) -> EventInjectionResult:
    started_at = perf_counter()
    status = "ok"
    path_count: int | None = None
    failed_path_count: int | None = None
    winner_path_id: str | None = None
    fallback_reason: str | None = None
    error_type: str | None = None
    risk_flags: list[str] | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        simulation = simulation_store.get(simulation_id)
        if simulation is None:
            status = "error"
            fallback_reason = "simulation-not-found"
            http_status = 404
            raise HTTPException(status_code=404, detail=f"simulation not found: {simulation_id}")

        result = event_injection_service.inject(simulation, payload)
        simulation_store.save(result.updated_simulation)
        path_count = len(result.updated_simulation.paths)
        failed_path_count = len([path for path in result.updated_simulation.paths if path.status == "failed"])
        winner_path_id = result.updated_simulation.winner_path_id
        risk_flags = list(result.updated_simulation.risk_flags)
        if result.updated_simulation.winner_path_id is None:
            status = "fallback"
            fallback_reason = "inject-event-no-valid-winner"
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
        _append_runtime_metric(
            route="/api/narrative/v6/simulations/{simulation_id}/inject-event",
            started_at=started_at,
            status=status,
            simulation_id=simulation_id,
            path_count=path_count,
            failed_path_count=failed_path_count,
            winner_path_id=winner_path_id,
            fallback_reason=fallback_reason,
            error_type=error_type,
            risk_flags=risk_flags,
            http_status=http_status,
        )


@router.post("/characters/{character_id}/interview", response_model=CharacterInterviewResponse)
def interview_character(character_id: str, payload: CharacterInterviewRequest) -> CharacterInterviewResponse:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        graph_rag_hints: list[str] = []
        if payload.relationship_graph_input is not None or payload.group_memory_graph is not None:
            retrieval = _retrieve_graph_with_stitching(
                GraphRAGRetrieveRequest(
                    query=_build_default_interview_graph_query(payload),
                    narrative_seed=None,
                    relationship_graph_input=payload.relationship_graph_input,
                    group_memory_graph=payload.group_memory_graph,
                    top_k=payload.graph_rag_top_k,
                    include_hidden=payload.graph_rag_include_hidden,
                    chapter_index=payload.chapter_index,
                ),
                source_route="/api/narrative/v6/characters/{character_id}/interview",
            )
            graph_rag_hints = [hit.summary for hit in retrieval.hits]
        return character_interview_service.interview(character_id, payload, graph_rag_hints=graph_rag_hints)
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
        _append_runtime_metric(
            route="/api/narrative/v6/characters/{character_id}/interview",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/group-memory/apply", response_model=GroupMemoryGraph)
def apply_group_memory(payload: GroupMemoryApplyRequest) -> GroupMemoryGraph:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return group_memory_service.apply(payload)
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
        _append_runtime_metric(
            route="/api/narrative/v6/group-memory/apply",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/graph/retrieve", response_model=GraphRAGRetrieveResponse)
def retrieve_graph_context(payload: GraphRAGRetrieveRequest) -> GraphRAGRetrieveResponse:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    fallback_reason: str | None = None
    http_status: int | None = 200
    risk_flags: list[str] | None = None
    try:
        _ensure_enabled()
        result = _retrieve_graph_with_stitching(
            payload,
            source_route="/api/narrative/v6/graph/retrieve",
        )
        if result.fallback_used:
            status = "fallback"
            fallback_reason = result.fallback_reason or "graph-rag-fallback"
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/retrieve",
            started_at=started_at,
            status=status,
            fallback_reason=fallback_reason,
            error_type=error_type,
            risk_flags=risk_flags,
            http_status=http_status,
        )


@router.post("/graph/memory/compact", response_model=dict[str, int])
def compact_graph_memory() -> dict[str, int]:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return graph_memory_store.compact()
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/memory/compact",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.get("/graph/memory/audit", response_model=dict[str, object])
def audit_graph_memory(limit: int = 20) -> dict[str, object]:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return graph_memory_store.audit_snapshot(limit=max(1, min(100, int(limit))))
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/memory/audit",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.post("/graph/memory/audit/snapshot", response_model=dict[str, object])
def persist_graph_memory_audit_snapshot(limit: int = 20) -> dict[str, object]:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return graph_memory_store.persist_audit_snapshot(limit=max(1, min(100, int(limit))))
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/memory/audit/snapshot",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.get("/graph/memory/audit/history", response_model=list[dict[str, object]])
def get_graph_memory_audit_history(limit: int = 20) -> list[dict[str, object]]:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return graph_memory_store.audit_history(limit=max(1, min(100, int(limit))))
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/memory/audit/history",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.get("/graph/memory/audit/alerts", response_model=dict[str, object])
def get_graph_memory_audit_alerts(limit: int = 20) -> dict[str, object]:
    started_at = perf_counter()
    status = "ok"
    error_type: str | None = None
    http_status: int | None = 200
    try:
        _ensure_enabled()
        return graph_memory_store.audit_trend_alerts(limit=max(1, min(100, int(limit))))
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
        _append_runtime_metric(
            route="/api/narrative/v6/graph/memory/audit/alerts",
            started_at=started_at,
            status=status,
            error_type=error_type,
            http_status=http_status,
        )


@router.get("/observability", response_model=dict[str, object])
def get_v6_observability(limit: int = 500) -> dict[str, object]:
    _ensure_enabled()
    return build_v6_observability_snapshot(runtime_store=runtime_metrics_store, limit=limit)
