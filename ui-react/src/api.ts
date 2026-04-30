export type OverviewResponse = {
  matrixVersion: string;
  healthValue: number;
  sampleCount: number;
  versionCount: number;
  hitRate: string;
  riskScore: number;
};

export type StorySignal = { label: string; value: number };
export type MatrixWeight = { label: string; value: string };
export type ChapterSummary = {
  title: string;
  hook: string;
  conflict: string;
  turn: string;
  payoff: string;
};
export type TuningWeight = {
  label: string;
  value: number;
  direction: 'up' | 'down';
  description: string;
};
export type Recommendation = {
  action: string;
  score: string;
  description: string;
  riskLevel?: 'low' | 'medium' | 'high';
  prerequisites?: string[];
  nextStep?: string;
  top?: boolean;
};
export type LogEntry = { time: string; text: string };
export type FeedbackNote = string;
export type V4GenreObservability = {
  genre: string;
  sampleCount: number;
  acceptRate: number;
  feedbackSignal: number;
};
export type V4Observability = {
  enabled: boolean;
  windowLimit: number;
  activeContexts: number;
  relationshipRows: number;
  feedbackRows: number;
  averageTension: number;
  feedbackSignal: number;
  acceptRate: number;
  genresTracked: number;
  autoLearningReadyGenres: number;
  topGenres: V4GenreObservability[];
  trend?: Array<{
    windowSize: number;
    sampleCount: number;
    feedbackSignal: number;
    acceptRate: number;
  }>;
  alerts?: Array<{
    code: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
    value?: number;
    threshold?: number;
  }>;
  alertCount?: number;
  criticalAlertCount?: number;
  alertRouting?: {
    enabled: boolean;
    routed: boolean;
    reason: string;
    criticalCount: number;
    signature?: string;
    cooldownSeconds?: number;
  };
  lastUpdated?: string | null;
};

export type DashboardResponse = {
  overview: OverviewResponse;
  narrativeSignals: StorySignal[];
  matrixWeights: MatrixWeight[];
  chapterSummary: ChapterSummary;
  tuningWeights: TuningWeight[];
  recommendations: Recommendation[];
  feedbackNotes: FeedbackNote[];
  logs: LogEntry[];
  v4Observability?: V4Observability;
};

export type TrainingSummary = {
  count: number;
  avg_predicted: number;
  avg_target: number;
  avg_feedback: number;
  rmse: number;
};

export type ValueMetricsSummary = {
  sample_count: number;
  accept_rate: number;
  average_chapter_quality: number;
  average_followup_writeability: number;
  average_continuity_delta: number;
};

export type TopActionMetric = {
  action: string;
  average_quality: number;
};

export type TrainingResponse = {
  version: string;
  sample_count: number;
  bias: number;
  weights: Record<string, number>;
  summary: TrainingSummary;
  history: Array<{
    action: string;
    predicted: number;
    target: number;
    feedback?: number;
  }>;
  value_metrics?: ValueMetricsSummary;
  top_actions?: TopActionMetric[];
};

export type FeedbackRequest = {
  recommendationAction: string;
  accepted: boolean;
  score: number;
  notes?: string;
};

export type FeedbackResponse = {
  accepted: boolean;
  version?: string | null;
  message: string;
  value_summary?: ValueMetricsSummary;
  top_actions?: TopActionMetric[];
};

export type RecommendationPreviewRequest = {
  tuningWeights: TuningWeight[];
  recommendations: Recommendation[];
};

export type RecommendationPreviewResponse = {
  recommendations: Recommendation[];
};

export type NarrativeV2CharacterState = {
  name: string;
  presence: number;
  consistency_risk: number;
  relationship_tension: number;
  arc_progress: number;
};

export type NarrativeV2StoryState = {
  chapter_index: number;
  stage: 'opening' | 'middle' | 'mid_late' | 'late';
  mainline_progress: number;
  sideplot_progress: number;
  conflict_intensity: number;
  emotional_temperature: number;
  pacing_speed: number;
  foreshadowing_load: number;
  payoff_pressure: number;
  characters: Record<string, NarrativeV2CharacterState>;
  tags: string[];
  retention_desire?: {
    primal_desire: number;
    value_recognition: number;
    knowledge_curiosity: number;
    information_gap: number;
    dominant?: 'primal_desire' | 'value_recognition' | 'knowledge_curiosity' | 'information_gap';
    dominant_override?: 'primal_desire' | 'value_recognition' | 'knowledge_curiosity' | 'information_gap';
  };
  macro_structure?: 'progressive' | 'hub_and_spoke' | 'anthology';
};

export type PlotTurnType = 'obstacle_shift' | 'goal_inversion' | 'character_contrast';

export type PlotUnitScaffold = {
  encounter_event: string;
  desire_goal: string;
  obstacle: string;
  solution_method: string;
  action_climax: {
    node: string;
    turn_type: PlotTurnType;
  };
  resolution: string;
};

export type NarrativeV2PreviewRequest = {
  case_id: string;
  state: NarrativeV2StoryState;
  plot_unit_scaffold?: PlotUnitScaffold;
};

export type NarrativeV2RuleCheck = {
  action: string;
  status: 'legal' | 'blocked' | 'prerequisite_missing';
  prerequisites: string[];
  blockers: string[];
  risk_flags: string[];
};

export type NarrativeV2Action = {
  action: string;
  delta: Record<string, number>;
  explanation: string;
};

export type NarrativeV2SearchResult = {
  action: NarrativeV2Action;
  rule_check: NarrativeV2RuleCheck;
  score: number;
  details: Record<string, number>;
};

export type NarrativeV2ContextCheckpoint = {
  name: string;
  status: 'pass' | 'mixed' | 'fail';
  evidence?: string;
  implication?: string;
};

export type NarrativeV2CheckpointSummary = {
  total: number;
  pass: number;
  mixed: number;
  fail: number;
};

export type NarrativeV2ContextQualityMetadata = {
  admission?: string;
  primary_function?: string;
  style_dna?: Record<string, string>;
  checkpoints?: NarrativeV2ContextCheckpoint[];
  checkpoint_summary?: NarrativeV2CheckpointSummary;
  quality_notes?: string;
};

export type NarrativeV4WorkbenchCandidate = {
  candidate_id: string;
  predicted_action: string;
  predicted_turning_point: string;
  predicted_conflict_type: string;
  predicted_payoff_type: string;
  retention_score: number;
  tension_score: number;
  explanation?: string;
  risk_flags?: string[];
};

export type NarrativeV4WorkbenchPreview = {
  enabled: boolean;
  fallback_reason?: string | null;
  candidate_count: number;
  retention_sort_key?: string;
  memory_summary?: {
    context_id?: string;
    history_window?: number;
    relationship_history_count: number;
    feedback_history_count: number;
    relationship_timeline_displacement_count?: number;
    memory_strategy?: string;
    relationship_merge_deduped_count?: number;
    feedback_merge_deduped_count?: number;
    relationship_collapsed_count?: number;
    feedback_collapsed_count?: number;
    relationship_clipped_count?: number;
    feedback_clipped_count?: number;
    relationship_decay_dropped_count?: number;
    feedback_decay_dropped_count?: number;
    candidate_timeline_count?: number;
    genre_auto_learning_mode?: string;
    genre_auto_learning_applied?: boolean;
    genre_auto_learning_sample_count?: number;
    genre_auto_learning_denoised_count?: number;
    genre_auto_learning_feedback_signal?: number;
    genre_auto_learning_bias_count?: number;
    genre_auto_learning_guard_triggered?: boolean;
    genre_auto_learning_guard_reason?: string;
    genre_auto_learning_fallback_mode?: string;
    genre_auto_learning_guard_profile?: {
      min_samples?: number;
      decay?: number;
      bias_limit?: number;
      max_volatility?: number;
      max_signal_divergence?: number;
      extreme_signal?: number;
      extreme_min_samples?: number;
      reversal_divergence_min?: number;
    };
  };
  relationship_graph?: {
    node_count: number;
    edge_count: number;
    displacement_count: number;
    high_tension_edges?: Array<Record<string, unknown>>;
  };
  relationship_displacements?: Array<Record<string, unknown>>;
  relationship_timeline?: Array<Record<string, unknown>>;
  candidate_timeline?: Array<Record<string, unknown>>;
  genre_calibration?: {
    genre?: string;
    learning_mode?: string;
    applied?: boolean;
    feedback_signal?: number;
    sample_count?: number;
    denoised_count?: number;
    guard_triggered?: boolean;
    guard_reason?: string;
    fallback_mode?: string;
    accept_rate?: number;
    signal_recent?: number;
    signal_long?: number;
    signal_volatility?: number;
    signal_divergence?: number;
    guard_profile?: {
      min_samples?: number;
      decay?: number;
      bias_limit?: number;
      max_volatility?: number;
      max_signal_divergence?: number;
      extreme_signal?: number;
      extreme_min_samples?: number;
      reversal_divergence_min?: number;
    };
    bias_updates?: Record<string, number>;
  };
  retention_writeback?: Record<string, unknown>;
  character_behavior_constraints?: Array<Record<string, unknown>>;
  character_validation?: Record<string, unknown>;
  relationship_graph_constraints?: Record<string, unknown>;
  prompt_documents?: Record<string, string>;
  prompt_compression_logs?: Array<Record<string, unknown>>;
  selected_candidate?: NarrativeV4WorkbenchCandidate | null;
  top_candidates?: NarrativeV4WorkbenchCandidate[];
  qc_summary?: Record<string, unknown>;
  v4_input_profile?: Record<string, unknown>;
};

export type NarrativeV2DecisionCandidate = {
  action: string;
  score: number;
  explanation?: string;
  details?: Record<string, number>;
  delta?: Record<string, number>;
};

export type NarrativeV2DecisionRuleStatusSummary = {
  legal_count: number;
  blocked_count: number;
  prerequisite_missing_count?: number;
};

export type NarrativeV2RetentionDriver = {
  target_function: string;
  primary_objective: string;
  priority_order: string[];
  guardrails: string[];
  selected_base_score: number;
  selected_retention_score: number;
  selected_guardrail_penalty: number;
  selected_final_score: number;
  control_mode: string;
  decision_tags?: Record<string, unknown>;
};

export type NarrativeV2Decision = {
  selected_action?: string;
  selected_score?: number;
  accepted_actions?: string[];
  blocked_actions?: string[];
  prerequisite_missing_actions?: string[];
  rule_status_summary?: NarrativeV2DecisionRuleStatusSummary;
  constraint_hint?: 'clear' | 'hard_blocked' | 'prerequisite_missing' | 'mixed_constraints' | string;
  validation_case_id?: string;
  quality_hint?: 'ready' | 'review' | 'blocked' | 'prerequisite_missing' | string;
  action?: string;
  top_action?: string;
  score?: number;
  top_score?: number;
  explanation?: string;
  details?: Record<string, number>;
  delta?: Record<string, number>;
  candidates?: NarrativeV2DecisionCandidate[];
  retention_driver?: NarrativeV2RetentionDriver;
};

export type NarrativeV2ValidationRecord = {
  case_id: string;
  accepted_actions: string[];
  blocked_actions: string[];
  top_action: string;
  notes: string;
};

export type NarrativeV2PreviewResponse = {
  case_id: string;
  state: NarrativeV2StoryState;
  rule_checks: NarrativeV2RuleCheck[];
  recommendations: NarrativeV2SearchResult[];
  decision?: NarrativeV2Decision;
  evaluation_summary: {
    count: number;
    top_action: string;
    top_score: number;
  };
  validation: NarrativeV2ValidationRecord;
};

export type NarrativeV2WorkbenchContext = {
  id: string;
  chapterNumber: number;
  title: string;
  stage: NarrativeV2StoryState['stage'];
  summary: string;
  state: NarrativeV2StoryState;
  compare_baseline?: {
    baseline_context_id?: string;
    baseline_chapter_number?: number;
    delta?: Record<string, number>;
  };
  v4_preview?: NarrativeV4WorkbenchPreview;
  quality?: NarrativeV2ContextQualityMetadata;
  admission?: string;
  primary_function?: string;
  style_dna?: Record<string, string>;
  checkpoints?: NarrativeV2ContextCheckpoint[];
  checkpoint_summary?: NarrativeV2CheckpointSummary;
  quality_notes?: string;
};

export type NarrativeV2WorkbenchContextsResponse = {
  contexts: NarrativeV2WorkbenchContext[];
  source?: string;
  context_contract?: string;
  fallback_reason?: string;
  report_path?: string;
  report_url?: string;
  run_id?: string;
  manifest_path?: string;
  preferred_model?: string;
  resolved_model?: string;
  report_success_rate?: number;
  report_timestamp?: string;
  arbitration_strategy?: string;
  source_diagnostics?: Record<string, unknown>;
};

export type NarrativeV6InterviewMode =
  | 'voice_test'
  | 'scene_reaction'
  | 'secret_probe'
  | 'free_chat';

export type NarrativeV6CharacterInterviewRequest = {
  profile: Record<string, unknown>;
  chapter_memory?: string[];
  relationship_graph_input?: Record<string, unknown>;
  group_memory_graph?: Record<string, unknown>;
  user_message: string;
  mode?: NarrativeV6InterviewMode;
  allow_hidden_info?: boolean;
};

export type NarrativeV6CharacterInterviewResponse = {
  character_id: string;
  reply: string;
  memory_evidence: string[];
  emotion_state_shift: string;
  ooc_risk_flags: string[];
  hidden_info_risk_flags: string[];
  transcript: Array<{ role: string; content: string }>;
  plot_foreshadow_candidates: string[];
};

export type NarrativeV7DecisionPreviewRequest = {
  text: string;
  story_state: Record<string, unknown>;
  character_states?: Array<Record<string, unknown>>;
  project_state?: {
    project_id: string;
    platform: string;
    genre_track: string;
    reader_profile: string;
    ip_flavor_tag: string;
    selling_point_contract: string;
  };
  benchmark_state?: Record<string, unknown>;
  metric_overrides?: Record<string, number>;
  decision_state?: Record<string, unknown>;
  override_confirmed?: boolean;
};

export type NarrativeV7DecisionPreviewResponse = {
  market_state: Record<string, unknown>;
  vector: {
    metrics: Record<string, number>;
    composite: number;
  };
  ohlcv: {
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  };
  decision: {
    decision_type: string;
    risk_level: string;
    route_id: string;
    reasons: string[];
    suggested_actions: string[];
    observe_next_metrics: string[];
  };
  defaults_applied: string[];
};

export type HistoryTimelineItem = {
  version: string;
  count: number;
  latest_time: string;
  average_feedback: number;
  average_chapter_quality: number;
  average_followup_writeability: number;
  average_continuity_delta: number;
  accept_rate: number;
  actions: string[];
  stage: string;
};

export type StageTimelineItem = {
  stage: string;
  count: number;
  latest_time: string;
  versions: string[];
  average_feedback: number;
};

export type HistoryResponse = {
  historyLogs: { time: string; text: string }[];
  historySnapshots: Array<{
    timestamp: string;
    stage: string;
    action: string;
    predicted: number;
    target: number;
    feedback: number;
    notes?: string;
    version?: string;
  }>;
  valueSummary: ValueMetricsSummary;
  topActions: TopActionMetric[];
  versionTimeline: HistoryTimelineItem[];
  stageTimeline: StageTimelineItem[];
  filters: { stage?: string | null; action?: string | null; limit: number };
};

export type HistoryExportResponse = {
  ok: boolean;
  path: string;
  counts: {
    training_logs: number;
    value_metrics: number;
  };
};

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/dashboard`);
  if (!response.ok) {
    throw new Error(`dashboard fetch failed: ${response.status}`);
  }
  return (await response.json()) as DashboardResponse;
}

export async function fetchHistory(filter: { stage?: string; action?: string; limit?: number } = {}): Promise<HistoryResponse> {
  const params = new URLSearchParams();
  if (filter.stage) params.set('stage', filter.stage);
  if (filter.action) params.set('action', filter.action);
  if (typeof filter.limit === 'number') params.set('limit', String(filter.limit));
  const query = params.toString();
  const response = await fetch(`${DEFAULT_BASE_URL}/api/history${query ? `?${query}` : ''}`);
  if (!response.ok) {
    throw new Error(`history fetch failed: ${response.status}`);
  }
  return (await response.json()) as HistoryResponse;
}

export async function fetchRecommendationPreview(
  payload: RecommendationPreviewRequest,
): Promise<RecommendationPreviewResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/recommendation/preview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`recommendation preview failed: ${response.status}`);
  }
  return (await response.json()) as RecommendationPreviewResponse;
}

export async function fetchRecommendationPreviewV2(
  payload: NarrativeV2PreviewRequest,
): Promise<NarrativeV2PreviewResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/v2/recommendation/preview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`v2 recommendation preview failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV2PreviewResponse;
}

export async function fetchWorkbenchContextsV2(): Promise<NarrativeV2WorkbenchContextsResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/v2/workbench/contexts`);
  if (!response.ok) {
    throw new Error(`v2 workbench contexts failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV2WorkbenchContextsResponse;
}

export async function refreshWorkbenchContextsV2(
  options: { onlineOnly?: boolean } = {},
): Promise<NarrativeV2WorkbenchContextsResponse> {
  const params = new URLSearchParams();
  if (options.onlineOnly) {
    params.set('online_only', 'true');
  }
  const query = params.toString();
  const response = await fetch(
    `${DEFAULT_BASE_URL}/api/v2/workbench/contexts/refresh${query ? `?${query}` : ''}`,
    { method: 'POST' },
  );
  if (!response.ok) {
    throw new Error(`v2 workbench context refresh failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV2WorkbenchContextsResponse;
}

export async function fetchNarrativeV4WorkbenchPreview(
  payload: { id?: string; state: NarrativeV2StoryState },
): Promise<NarrativeV4WorkbenchPreview> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/v4/workbench/preview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`v4 workbench preview failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV4WorkbenchPreview;
}

export async function fetchNarrativeV6CharacterInterview(
  characterId: string,
  payload: NarrativeV6CharacterInterviewRequest,
): Promise<NarrativeV6CharacterInterviewResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/narrative/v6/characters/${characterId}/interview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`v6 character interview failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV6CharacterInterviewResponse;
}

export async function fetchNarrativeV7DecisionPreview(
  payload: NarrativeV7DecisionPreviewRequest,
): Promise<NarrativeV7DecisionPreviewResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/narrative/v7/decision/preview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`v7 decision preview failed: ${response.status}`);
  }
  return (await response.json()) as NarrativeV7DecisionPreviewResponse;
}

export async function runTraining(): Promise<TrainingResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/training`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`training failed: ${response.status}`);
  }
  return (await response.json()) as TrainingResponse;
}

export async function submitFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`feedback failed: ${response.status}`);
  }
  return (await response.json()) as FeedbackResponse;
}

export async function exportHistory(): Promise<HistoryExportResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/history/export`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`export failed: ${response.status}`);
  }
  return (await response.json()) as HistoryExportResponse;
}
