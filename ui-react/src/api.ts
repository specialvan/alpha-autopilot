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

export type TrainingResponse = {
  version: string;
  sample_count: number;
  bias: number;
  weights: Record<string, number>;
  summary: {
    sample_count: number;
    average_predicted: number;
    average_target: number;
    average_feedback: number;
  };
  history: Array<{
    action: string;
    predicted: number;
    target: number;
    feedback?: number;
  }>;
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
};

export type RecommendationPreviewRequest = {
  tuningWeights: TuningWeight[];
  recommendations: Recommendation[];
};

export type RecommendationPreviewResponse = {
  recommendations: Recommendation[];
};

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/dashboard`);
  if (!response.ok) {
    throw new Error(`dashboard fetch failed: ${response.status}`);
  }
  return (await response.json()) as DashboardResponse;
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
