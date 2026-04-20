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
export type Recommendation = {
  action: string;
  score: string;
  description: string;
  top?: boolean;
};
export type LogEntry = { time: string; text: string };
export type FeedbackNote = string;

export type DashboardResponse = {
  overview: OverviewResponse;
  narrativeSignals: StorySignal[];
  matrixWeights: MatrixWeight[];
  recommendations: Recommendation[];
  feedbackNotes: FeedbackNote[];
  logs: LogEntry[];
};

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${DEFAULT_BASE_URL}/api/dashboard`);
  if (!response.ok) {
    throw new Error(`dashboard fetch failed: ${response.status}`);
  }
  return (await response.json()) as DashboardResponse;
}
