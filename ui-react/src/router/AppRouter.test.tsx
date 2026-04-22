import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AppRoutes } from './AppRouter';

const {
  fetchDashboard,
  fetchHistory,
  fetchRecommendationPreview,
  fetchRecommendationPreviewV2,
  fetchWorkbenchContextsV2,
  runTraining,
  submitFeedback,
  exportHistory,
} = vi.hoisted(() => ({
  fetchDashboard: vi.fn(),
  fetchHistory: vi.fn(),
  fetchRecommendationPreview: vi.fn(),
  fetchRecommendationPreviewV2: vi.fn(),
  fetchWorkbenchContextsV2: vi.fn(),
  runTraining: vi.fn(),
  submitFeedback: vi.fn(),
  exportHistory: vi.fn(),
}));

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api');
  return {
    ...actual,
    fetchDashboard,
    fetchHistory,
    fetchRecommendationPreview,
    fetchRecommendationPreviewV2,
    fetchWorkbenchContextsV2,
    runTraining,
    submitFeedback,
    exportHistory,
  };
});

describe('AppRoutes', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    fetchDashboard.mockResolvedValue({
      overview: {
        matrixVersion: 'v003',
        healthValue: 82,
        sampleCount: 10,
        versionCount: 3,
        hitRate: '76%',
        riskScore: 34,
      },
      narrativeSignals: [],
      matrixWeights: [],
      chapterSummary: {
        title: 'Summary',
        hook: 'Hook',
        conflict: 'Conflict',
        turn: 'Turn',
        payoff: 'Payoff',
      },
      tuningWeights: [],
      recommendations: [],
      feedbackNotes: [],
      logs: [],
    });

    fetchHistory.mockResolvedValue({
      historyLogs: [],
      historySnapshots: [],
      valueSummary: {
        sample_count: 0,
        accept_rate: 0,
        average_chapter_quality: 0,
        average_followup_writeability: 0,
        average_continuity_delta: 0,
      },
      topActions: [],
      versionTimeline: [],
      stageTimeline: [],
      filters: { limit: 20, stage: null, action: null },
    });

    fetchRecommendationPreview.mockResolvedValue({ recommendations: [] });
    fetchRecommendationPreviewV2.mockResolvedValue({
      case_id: 'demo-v2-middle-8',
      state: {
        chapter_index: 8,
        stage: 'middle',
        mainline_progress: 0.45,
        sideplot_progress: 0.22,
        conflict_intensity: 0.64,
        emotional_temperature: 0.58,
        pacing_speed: 0.5,
        foreshadowing_load: 0.38,
        payoff_pressure: 0.32,
        characters: {},
        tags: ['power'],
      },
      rule_checks: [],
      recommendations: [],
      evaluation_summary: { count: 0, top_action: '', top_score: 0 },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: [],
        blocked_actions: [],
        top_action: '',
        notes: '',
      },
    });
    fetchWorkbenchContextsV2.mockResolvedValue({
      contexts: [
        {
          id: 'live-chapter-18',
          chapterNumber: 18,
          title: 'Current Live Chapter',
          stage: 'middle',
          summary: 'History-backed live context',
          state: {
            chapter_index: 18,
            stage: 'middle',
            mainline_progress: 0.61,
            sideplot_progress: 0.37,
            conflict_intensity: 0.64,
            emotional_temperature: 0.53,
            pacing_speed: 0.49,
            foreshadowing_load: 0.36,
            payoff_pressure: 0.31,
            characters: {},
            tags: ['power', 'middle'],
          },
        },
      ],
    });
    runTraining.mockResolvedValue(null);
    submitFeedback.mockResolvedValue({ accepted: true, message: 'ok' });
    exportHistory.mockResolvedValue({
      ok: true,
      path: 'artifacts/exports/history.json',
      counts: { training_logs: 0, value_metrics: 0 },
    });
  });

  it('links the dashboard to the dedicated workbench and no longer renders the embedded lab', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('link', { name: 'Open V2 Workbench' })).toHaveAttribute(
      'href',
      '/v2/workbench',
    );
    expect(screen.queryByRole('heading', { name: 'V2 Preview Lab' })).not.toBeInTheDocument();
  });

  it('renders the dedicated workbench route', async () => {
    render(
      <MemoryRouter initialEntries={['/v2/workbench']}>
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
  });
});
