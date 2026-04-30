from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


NQM_METRIC_IDS: tuple[str, ...] = (
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6",
    "P7",
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
    "T8",
    "T9",
    "T10",
    "W1",
    "W2",
    "W3",
    "W4",
    "W5",
    "W6",
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
)


def default_nqm_metrics() -> dict[str, float]:
    return {metric: 0.5 for metric in NQM_METRIC_IDS}


class DecisionType(str, Enum):
    OPEN = "open"
    ADD = "add"
    REDUCE = "reduce"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    OBSERVE = "observe"
    REVERSAL_CONFIRM = "reversal_confirm"
    BREAKOUT_FOLLOW = "breakout_follow"
    RETRACE_REPAIR = "retrace_repair"


class RiskLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class AntiPatternSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class NovelProjectState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str = "default-project"
    platform: str = "unknown"
    genre_track: str = "unknown"
    reader_profile: str = "unknown"
    ip_flavor_tag: str = "default"
    selling_point_contract: str = ""


class BenchmarkParameterSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: str = ""
    channel: str = "unknown"
    genre_track: str = "unknown"
    sample_count: int = Field(default=0, ge=0)
    nqm_mean: float = Field(default=0.62, ge=0.0, le=1.0)
    nqm_std: float = Field(default=0.08, ge=0.01, le=0.5)
    high_threshold: float = Field(default=0.78, ge=0.0, le=1.0)
    low_threshold: float = Field(default=0.52, ge=0.0, le=1.0)
    opening_gate_t8: float = Field(default=0.60, ge=0.0, le=1.0)


class ThresholdBand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    support: float = Field(default=0.52, ge=0.0, le=1.0)
    resistance: float = Field(default=0.78, ge=0.0, le=1.0)
    stop_loss: float = Field(default=0.45, ge=0.0, le=1.0)
    breakout_confirm: float = Field(default=0.82, ge=0.0, le=1.0)


class DecisionState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    last_decision_type: DecisionType = DecisionType.OBSERVE
    last_composite: float = Field(default=0.5, ge=0.0, le=1.0)
    deviation: float = 0.0
    available_position: float = Field(default=1.0, ge=0.0, le=1.0)


class NarrativeMarketState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_state: NovelProjectState = Field(default_factory=NovelProjectState)
    story_state: dict[str, Any] = Field(default_factory=dict)
    benchmark_state: BenchmarkParameterSet = Field(default_factory=BenchmarkParameterSet)
    metric_state: dict[str, float] = Field(default_factory=default_nqm_metrics)
    kline_state: dict[str, Any] = Field(default_factory=dict)
    threshold_state: dict[str, ThresholdBand] = Field(default_factory=dict)
    decision_state: DecisionState = Field(default_factory=DecisionState)


class StoryStateMarketAdaptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    story_state: dict[str, Any] = Field(default_factory=dict)
    project_state: NovelProjectState | None = None
    benchmark_state: BenchmarkParameterSet | None = None
    metric_overrides: dict[str, float] = Field(default_factory=dict)
    decision_state: DecisionState | None = None


class StoryStateMarketAdaptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_state: NarrativeMarketState
    defaults_applied: list[str] = Field(default_factory=list)


class UnifiedDecisionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    story_state: dict[str, Any] = Field(default_factory=dict)
    character_states: list[dict[str, Any]] = Field(default_factory=list)
    project_state: NovelProjectState | None = None
    benchmark_state: BenchmarkParameterSet | None = None
    metric_overrides: dict[str, float] = Field(default_factory=dict)
    decision_state: DecisionState | None = None
    override_confirmed: bool = False


class NQMVector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metrics: dict[str, float] = Field(default_factory=default_nqm_metrics)
    composite: float = Field(default=0.5, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _normalize(self) -> "NQMVector":
        normalized: dict[str, float] = {}
        for metric_id in NQM_METRIC_IDS:
            raw_value = self.metrics.get(metric_id, 0.5)
            normalized[metric_id] = max(0.0, min(1.0, float(raw_value)))
        self.metrics = normalized
        self.composite = max(0.0, min(1.0, float(self.composite)))
        return self


class NarrativeMetricOHLCV(BaseModel):
    model_config = ConfigDict(extra="forbid")

    open: float = Field(default=0.5, ge=0.0, le=1.0)
    high: float = Field(default=0.5, ge=0.0, le=1.0)
    low: float = Field(default=0.5, ge=0.0, le=1.0)
    close: float = Field(default=0.5, ge=0.0, le=1.0)
    volume: float = Field(default=0.0, ge=0.0)


class NQMSampleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    story_state: dict[str, Any] = Field(default_factory=dict)
    character_states: list[dict[str, Any]] = Field(default_factory=list)
    benchmark_parameters: BenchmarkParameterSet | None = None


class NQMSampleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector: NQMVector
    ohlcv: NarrativeMetricOHLCV
    elapsed_ms: float = Field(default=0.0, ge=0.0)


class NarrativeDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_type: DecisionType
    risk_level: RiskLevel
    route_id: str
    reasons: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    observe_next_metrics: list[str] = Field(default_factory=list)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_state: NarrativeMarketState
    vector: NQMVector
    ohlcv: NarrativeMetricOHLCV
    override_confirmed: bool = False


class DecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: NarrativeDecision


class UnifiedDecisionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    market_state: NarrativeMarketState
    vector: NQMVector
    ohlcv: NarrativeMetricOHLCV
    decision: NarrativeDecision
    defaults_applied: list[str] = Field(default_factory=list)


class OpeningGateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    chapter_index: int = Field(default=1, ge=1)
    allow_override: bool = False


class OpeningGateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocked: bool
    t8_score: float = Field(default=0.0, ge=0.0, le=1.0)
    toxic_hits: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    override_logged: bool = False


class HookGuardRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    tail_window_chars: int = Field(default=300, ge=50, le=1200)


class HookGuardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    t4_hook_density: float = Field(default=0.0, ge=0.0, le=1.0)
    triggered: bool = False
    suggestions: list[str] = Field(default_factory=list)


class DeadlockUnitSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(default=1, ge=1)
    t2_slope: float = Field(default=0.0)
    t4: float = Field(default=0.0, ge=0.0, le=1.0)
    p3: float = Field(default=0.0, ge=0.0, le=1.0)


class DeadlockCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recent_units: list[DeadlockUnitSnapshot] = Field(default_factory=list)


class DeadlockCheckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    triggered: bool
    strategy: str = "none"
    deadlock_log: dict[str, Any] = Field(default_factory=dict)


class AntiPatternCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vector: NQMVector
    continuous_trigger_count: int = Field(default=1, ge=1)
    hint_flags: dict[str, bool] = Field(default_factory=dict)


class AntiPatternAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern: str
    severity: AntiPatternSeverity
    reason: str


class AntiPatternCheckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alerts: list[AntiPatternAlert] = Field(default_factory=list)
    critical: bool = False


class EmotionSatisfactionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    reader_signals: dict[str, float] = Field(default_factory=dict)


class EmotionSatisfactionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float = Field(default=0.0, ge=0.0, le=1.0)
    dimensions: dict[str, float] = Field(default_factory=dict)
    volume_proxy: float = Field(default=0.0, ge=0.0)


class LoopStructureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_scores: list[float] = Field(default_factory=list)
    cycle_tags: list[str] = Field(default_factory=list)


class LoopStructureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aligned: bool
    trend: Literal["up", "flat", "down"] = "flat"
    suggestions: list[str] = Field(default_factory=list)


class PacingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment_scores: list[float] = Field(default_factory=list)
    info_drop_ratio: float = Field(default=0.5, ge=0.0, le=1.0)


class PacingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["healthy", "overheat", "dragging", "volatile"]
    suggestions: list[str] = Field(default_factory=list)


class BenchmarkIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: str = Field(min_length=1)
    channel: str = "unknown"
    genre_track: str = "unknown"
    sample_payload: dict[str, Any] = Field(default_factory=dict)


class BenchmarkIngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: bool
    version: str
    recalibrated: bool
    message: str = ""


class BenchmarkQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    channel: str = "unknown"
    genre_track: str = "unknown"


class BenchmarkQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    benchmark: BenchmarkParameterSet
    source_count: int = Field(default=0, ge=0)
    corridor_ready: bool = False
    warnings: list[str] = Field(default_factory=list)


class BenchmarkVersionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    created_at: str
    trigger: str = "unknown"
    total_rows: int = Field(default=0, ge=0)
    active_rows: int = Field(default=0, ge=0)
    rows_sha256: str = ""
    integrity_status: Literal["verified", "unverified", "failed"] = "unverified"


class BenchmarkVersionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    versions: list[BenchmarkVersionRecord] = Field(default_factory=list)


class BenchmarkRestoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    restored: bool
    requested_version: str
    active_version: str
    total_rows: int = Field(default=0, ge=0)
    active_rows: int = Field(default=0, ge=0)
    integrity_verified: bool = False
    backup_version: str = ""
    message: str = ""


class BenchmarkVersionDiffResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparable: bool
    base_version: str
    target_version: str
    base_active_rows: int = Field(default=0, ge=0)
    target_active_rows: int = Field(default=0, ge=0)
    base_integrity_verified: bool = False
    target_integrity_verified: bool = False
    added_count: int = Field(default=0, ge=0)
    removed_count: int = Field(default=0, ge=0)
    activated_count: int = Field(default=0, ge=0)
    deactivated_count: int = Field(default=0, ge=0)
    mean_changed_count: int = Field(default=0, ge=0)
    added_book_ids: list[str] = Field(default_factory=list)
    removed_book_ids: list[str] = Field(default_factory=list)
    activated_book_ids: list[str] = Field(default_factory=list)
    deactivated_book_ids: list[str] = Field(default_factory=list)
    mean_changed_book_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkAuditExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    latest_version: str = ""
    version_count: int = Field(default=0, ge=0)
    integrity_verified_count: int = Field(default=0, ge=0)
    integrity_unverified_count: int = Field(default=0, ge=0)
    integrity_failed_count: int = Field(default=0, ge=0)
    versions: list[BenchmarkVersionRecord] = Field(default_factory=list)


class BenchmarkVersionPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    version_count_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    kept_versions: list[str] = Field(default_factory=list)
    pruned_versions: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkVersionHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    total_files: int = Field(default=0, ge=0)
    valid_snapshot_count: int = Field(default=0, ge=0)
    verified_count: int = Field(default=0, ge=0)
    unverified_count: int = Field(default=0, ge=0)
    failed_integrity_count: int = Field(default=0, ge=0)
    malformed_file_count: int = Field(default=0, ge=0)
    failed_versions: list[str] = Field(default_factory=list)
    malformed_files: list[str] = Field(default_factory=list)


class BenchmarkVersionRepairResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    total_files: int = Field(default=0, ge=0)
    candidate_failed_count: int = Field(default=0, ge=0)
    candidate_malformed_count: int = Field(default=0, ge=0)
    moved_count: int = Field(default=0, ge=0)
    moved_failed_count: int = Field(default=0, ge=0)
    moved_malformed_count: int = Field(default=0, ge=0)
    quarantine_dir: str = ""
    moved_files: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    severity: Literal["ok", "warn", "critical"] = "ok"
    recommendations: list[str] = Field(default_factory=list)
    audit: BenchmarkAuditExportResponse
    health: BenchmarkVersionHealthResponse


class BenchmarkVersionAutoRemediateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    health_before: BenchmarkVersionHealthResponse
    repair: BenchmarkVersionRepairResponse
    prune: BenchmarkVersionPruneResponse
    health_after: BenchmarkVersionHealthResponse
    message: str = ""


class BenchmarkMaintenanceSlaPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_failed_integrity: int = Field(default=0, ge=0)
    max_malformed_files: int = Field(default=0, ge=0)
    max_unverified: int = Field(default=0, ge=0)
    max_version_count_warn: int = Field(default=500, ge=0)
    max_version_count_critical: int = Field(default=2000, ge=0)
    page_on_critical: bool = True
    ticket_on_warn: bool = True


class BenchmarkMaintenanceAlertResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    level: Literal["ok", "warn", "critical"] = "ok"
    should_page: bool = False
    should_ticket: bool = False
    breaches: list[str] = Field(default_factory=list)
    policy: BenchmarkMaintenanceSlaPolicy
    report: BenchmarkMaintenanceReportResponse


class BenchmarkMaintenanceAlertEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    generated_at: str
    level: Literal["ok", "warn", "critical"] = "ok"
    should_page: bool = False
    should_ticket: bool = False
    breaches: list[str] = Field(default_factory=list)
    report_severity: Literal["ok", "warn", "critical"] = "ok"


class BenchmarkMaintenanceAlertEmitResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alert: BenchmarkMaintenanceAlertResponse
    event: BenchmarkMaintenanceAlertEvent


class BenchmarkMaintenanceAlertListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_valid_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    alerts: list[BenchmarkMaintenanceAlertEvent] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    total_alerts_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    kept_event_ids: list[str] = Field(default_factory=list)
    pruned_event_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    total_valid_events: int = Field(default=0, ge=0)
    window_event_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    ok_count: int = Field(default=0, ge=0)
    warn_count: int = Field(default=0, ge=0)
    critical_count: int = Field(default=0, ge=0)
    page_event_count: int = Field(default=0, ge=0)
    ticket_event_count: int = Field(default=0, ge=0)
    breach_event_count: int = Field(default=0, ge=0)
    latest_event: BenchmarkMaintenanceAlertEvent | None = None
    message: str = ""


class BenchmarkMaintenanceAlertDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    stale_threshold_seconds: int = Field(default=0, ge=0)
    latest_event_age_seconds: float = Field(default=-1.0, ge=-1.0)
    is_stale: bool = True
    recommended_action: str = "observe"
    current_alert: BenchmarkMaintenanceAlertResponse
    summary: BenchmarkMaintenanceAlertSummaryResponse
    message: str = ""


class BenchmarkMaintenanceAlertExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_valid_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    digest: BenchmarkMaintenanceAlertDigestResponse
    alerts: list[BenchmarkMaintenanceAlertEvent] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertArchiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    shard_size: int = Field(default=0, ge=0)
    total_valid_events_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    archived_count: int = Field(default=0, ge=0)
    archive_shard_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    archive_dir: str = ""
    archive_files: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertArchiveFileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_name: str
    size_bytes: int = Field(default=0, ge=0)
    modified_at: str = ""
    valid_event_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)


class BenchmarkMaintenanceAlertArchiveListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    total_files: int = Field(default=0, ge=0)
    files: list[BenchmarkMaintenanceAlertArchiveFileRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertArchiveReadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_name: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_valid_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    alerts: list[BenchmarkMaintenanceAlertEvent] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertArchiveCleanupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    ttl_days: int = Field(default=0, ge=0)
    max_shard_files: int = Field(default=0, ge=0)
    total_files: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    removed_count: int = Field(default=0, ge=0)
    ttl_candidate_count: int = Field(default=0, ge=0)
    max_shard_candidate_count: int = Field(default=0, ge=0)
    archive_dir: str = ""
    candidate_files: list[str] = Field(default_factory=list)
    removed_files: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertAutoArchiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    trigger_count: int = Field(default=0, ge=0)
    keep_last: int = Field(default=0, ge=0)
    shard_size: int = Field(default=0, ge=0)
    total_valid_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    should_archive: bool = False
    archive: BenchmarkMaintenanceAlertArchiveResponse | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernancePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    archive_trigger_count: int = Field(default=0, ge=0)
    archive_keep_last: int = Field(default=0, ge=0)
    archive_shard_size: int = Field(default=0, ge=0)
    archive_ttl_days: int = Field(default=0, ge=0)
    archive_max_shard_files: int = Field(default=0, ge=0)
    governance_runs_prune_trigger_count: int = Field(default=0, ge=0)
    governance_runs_prune_keep_last: int = Field(default=0, ge=0)
    governance_escalations_prune_trigger_count: int = Field(default=0, ge=0)
    governance_escalations_prune_keep_last: int = Field(default=0, ge=0)
    governance_escalation_remediations_prune_trigger_count: int = Field(default=0, ge=0)
    governance_escalation_remediations_prune_keep_last: int = Field(default=0, ge=0)
    governance_escalation_remediation_auto_remediate_runs_prune_trigger_count: int = Field(default=0, ge=0)
    governance_escalation_remediation_auto_remediate_runs_prune_keep_last: int = Field(default=0, ge=0)
    governance_escalation_remediations_stale_seconds: int = Field(default=0, ge=0)
    governance_escalations_emit_cooldown_seconds: int = Field(default=0, ge=0)
    governance_runs_max_retry_attempts: int = Field(default=0, ge=0)
    governance_runs_escalation_failure_streak: int = Field(default=0, ge=0)
    stale_threshold_seconds: int = Field(default=0, ge=0)


class BenchmarkMaintenanceAlertGovernanceReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    alert_limit: int = Field(default=0, ge=0)
    archive_limit: int = Field(default=0, ge=0)
    policy: BenchmarkMaintenanceAlertGovernancePolicy
    active_summary: BenchmarkMaintenanceAlertSummaryResponse
    archive_index: BenchmarkMaintenanceAlertArchiveListResponse
    projected_auto_archive: BenchmarkMaintenanceAlertAutoArchiveResponse
    projected_archive_cleanup: BenchmarkMaintenanceAlertArchiveCleanupResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    generated_at: str
    completed_at: str = ""
    status: Literal["succeeded", "failed"] = "succeeded"
    dry_run: bool
    alert_limit: int = Field(default=0, ge=0)
    archive_limit: int = Field(default=0, ge=0)
    idempotency_key: str = ""
    request_fingerprint: str = ""
    retry_run_id: str = ""
    attempt: int = Field(default=1, ge=1)
    performed_steps: list[str] = Field(default_factory=list)
    auto_archive_should_archive: bool = False
    archive_cleanup_candidate_count: int = Field(default=0, ge=0)
    error_type: str = ""
    error_message: str = ""
    result_message: str = ""
    response_payload: dict[str, Any] = Field(default_factory=dict)


class BenchmarkMaintenanceAlertGovernanceRunListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    records: list[BenchmarkMaintenanceAlertGovernanceRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    total_runs_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    kept_run_ids: list[str] = Field(default_factory=list)
    pruned_run_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    window_record_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    succeeded_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    consecutive_failed_runs: int = Field(default=0, ge=0)
    latest_run: BenchmarkMaintenanceAlertGovernanceRunRecord | None = None
    latest_failed_run: BenchmarkMaintenanceAlertGovernanceRunRecord | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    summary: BenchmarkMaintenanceAlertGovernanceRunSummaryResponse
    records: list[BenchmarkMaintenanceAlertGovernanceRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    trigger_count: int = Field(default=0, ge=0)
    keep_last: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    should_prune: bool = False
    prune: BenchmarkMaintenanceAlertGovernanceRunPruneResponse | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    stale_threshold_seconds: int = Field(default=0, ge=0)
    latest_run_age_seconds: float = Field(default=-1.0, ge=-1.0)
    retry_max_attempts: int = Field(default=0, ge=0)
    latest_failed_attempt: int = Field(default=0, ge=0)
    retry_exhausted: bool = False
    escalation_failure_streak_limit: int = Field(default=0, ge=0)
    failure_streak_exhausted: bool = False
    is_stale: bool = True
    recommended_action: str = "observe"
    summary: BenchmarkMaintenanceAlertGovernanceRunSummaryResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    generated_at: str
    source: Literal["manual_emit", "auto_remediate"] = "manual_emit"
    recommended_action: str = "observe"
    escalation_reason: str = ""
    digest_message: str = ""
    latest_run_id: str = ""
    latest_failed_run_id: str = ""
    consecutive_failed_runs: int = Field(default=0, ge=0)
    latest_failed_attempt: int = Field(default=0, ge=0)
    retry_max_attempts: int = Field(default=0, ge=0)
    escalation_failure_streak_limit: int = Field(default=0, ge=0)
    retry_exhausted: bool = False
    failure_streak_exhausted: bool = False


class BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    emitted: bool = False
    suppressed: bool = False
    suppression_reason: str = ""
    suppressed_by_event_id: str = ""
    cooldown_seconds: int = Field(default=0, ge=0)
    digest: BenchmarkMaintenanceAlertGovernanceRunDigestResponse
    event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    events: list[BenchmarkMaintenanceAlertGovernanceEscalationEvent] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    total_events: int = Field(default=0, ge=0)
    window_event_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    manual_emit_count: int = Field(default=0, ge=0)
    auto_remediate_count: int = Field(default=0, ge=0)
    retry_exhausted_count: int = Field(default=0, ge=0)
    failure_streak_exhausted_count: int = Field(default=0, ge=0)
    latest_event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    summary: BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse
    events: list[BenchmarkMaintenanceAlertGovernanceEscalationEvent] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    total_events_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    kept_event_ids: list[str] = Field(default_factory=list)
    pruned_event_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    trigger_count: int = Field(default=0, ge=0)
    keep_last: int = Field(default=0, ge=0)
    total_events: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    should_prune: bool = False
    prune: BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    stale_threshold_seconds: int = Field(default=0, ge=0)
    latest_event_age_seconds: float = Field(default=-1.0, ge=-1.0)
    is_stale: bool = True
    recommended_action: str = "observe"
    summary: BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse
    run_digest: BenchmarkMaintenanceAlertGovernanceRunDigestResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    limit: int = Field(default=0, ge=0)
    action: str = "observe"
    executed: bool = False
    emitted: bool = False
    pruned: bool = False
    emitted_event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
    auto_prune: BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse | None = None
    digest_before: BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse
    digest_after: BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    generated_at: str
    dry_run: bool
    limit: int = Field(default=0, ge=0)
    action: str = "observe"
    executed: bool = False
    emitted: bool = False
    pruned: bool = False
    emitted_event_id: str = ""
    auto_prune_pruned_count: int = Field(default=0, ge=0)
    auto_prune_malformed_dropped_count: int = Field(default=0, ge=0)
    digest_before_message: str = ""
    digest_after_message: str = ""
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    window_record_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    dry_run_count: int = Field(default=0, ge=0)
    apply_count: int = Field(default=0, ge=0)
    executed_count: int = Field(default=0, ge=0)
    emitted_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    latest_record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    summary: BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse
    records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    total_records_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    kept_run_ids: list[str] = Field(default_factory=list)
    pruned_run_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    trigger_count: int = Field(default=0, ge=0)
    keep_last: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    should_prune: bool = False
    prune: BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    stale_threshold_seconds: int = Field(default=0, ge=0)
    latest_record_age_seconds: float = Field(default=-1.0, ge=-1.0)
    is_stale: bool = True
    recommended_action: str = "observe"
    summary: BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    limit: int = Field(default=0, ge=0)
    action: str = "observe"
    executed: bool = False
    remediated_escalations: bool = False
    pruned_remediation_history: bool = False
    escalation_auto_remediate: BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse | None = None
    remediation_auto_prune: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse | None = None
    digest_before: BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse
    digest_after: BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    generated_at: str
    dry_run: bool
    limit: int = Field(default=0, ge=0)
    action: str = "observe"
    executed: bool = False
    remediated_escalations: bool = False
    pruned_remediation_history: bool = False
    digest_before_message: str = ""
    digest_after_message: str = ""
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    window_record_count: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    dry_run_count: int = Field(default=0, ge=0)
    apply_count: int = Field(default=0, ge=0)
    executed_count: int = Field(default=0, ge=0)
    remediated_escalations_count: int = Field(default=0, ge=0)
    pruned_remediation_history_count: int = Field(default=0, ge=0)
    latest_record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    limit: int = Field(default=0, ge=0)
    cursor: str = ""
    next_cursor: str = ""
    has_more: bool = False
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    summary: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse
    records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    keep_last: int = Field(default=0, ge=0)
    total_records_before: int = Field(default=0, ge=0)
    kept_count: int = Field(default=0, ge=0)
    candidate_count: int = Field(default=0, ge=0)
    pruned_count: int = Field(default=0, ge=0)
    malformed_candidate_count: int = Field(default=0, ge=0)
    malformed_dropped_count: int = Field(default=0, ge=0)
    kept_run_ids: list[str] = Field(default_factory=list)
    pruned_run_ids: list[str] = Field(default_factory=list)
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    trigger_count: int = Field(default=0, ge=0)
    keep_last: int = Field(default=0, ge=0)
    total_records: int = Field(default=0, ge=0)
    malformed_line_count: int = Field(default=0, ge=0)
    should_prune: bool = False
    prune: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse | None = None
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    dry_run: bool
    limit: int = Field(default=0, ge=0)
    alert_limit: int = Field(default=0, ge=0)
    archive_limit: int = Field(default=0, ge=0)
    action: str = "observe"
    executed: bool = False
    escalation_required: bool = False
    escalation_reason: str = ""
    escalation_event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
    governance_run: BenchmarkMaintenanceAlertGovernanceRunResponse | None = None
    auto_prune: BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse | None = None
    digest_before: BenchmarkMaintenanceAlertGovernanceRunDigestResponse
    digest_after: BenchmarkMaintenanceAlertGovernanceRunDigestResponse
    message: str = ""


class BenchmarkMaintenanceAlertGovernanceRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = ""
    generated_at: str
    dry_run: bool
    alert_limit: int = Field(default=0, ge=0)
    archive_limit: int = Field(default=0, ge=0)
    idempotency_key: str = ""
    request_fingerprint: str = ""
    retry_run_id: str = ""
    attempt: int = Field(default=1, ge=1)
    idempotency_reused: bool = False
    policy: BenchmarkMaintenanceAlertGovernancePolicy
    performed_steps: list[str] = Field(default_factory=list)
    active_summary_before: BenchmarkMaintenanceAlertSummaryResponse
    active_summary_after: BenchmarkMaintenanceAlertSummaryResponse
    archive_index_before: BenchmarkMaintenanceAlertArchiveListResponse
    archive_index_after: BenchmarkMaintenanceAlertArchiveListResponse
    auto_archive: BenchmarkMaintenanceAlertAutoArchiveResponse
    archive_cleanup: BenchmarkMaintenanceAlertArchiveCleanupResponse
    message: str = ""
