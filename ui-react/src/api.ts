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

export type DashboardResponse = {
  overview: OverviewResponse;
  narrativeSignals: StorySignal[];
  matrixWeights: MatrixWeight[];
  chapterSummary: ChapterSummary;
  tuningWeights: TuningWeight[];
  recommendations: Recommendation[];
  feedbackNotes: FeedbackNote[];
  logs: LogEntry[];
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
};

export type NarrativeV2PreviewRequest = {
  case_id: string;
  state: NarrativeV2StoryState;
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
};

export type NarrativeV2WorkbenchContextsResponse = {
  contexts: NarrativeV2WorkbenchContext[];
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
