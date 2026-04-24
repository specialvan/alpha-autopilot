import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { V2WorkbenchPage } from './V2WorkbenchPage';

const { fetchRecommendationPreviewV2, fetchWorkbenchContextsV2 } = vi.hoisted(() => ({
  fetchRecommendationPreviewV2: vi.fn(),
  fetchWorkbenchContextsV2: vi.fn(),
}));

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api');
  return {
    ...actual,
    fetchRecommendationPreviewV2,
    fetchWorkbenchContextsV2,
  };
});

describe('V2WorkbenchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
          admission: 'approved',
          style_dna: {
            pace: 'brisk',
            dialogue_reliance: 'medium',
          },
          checkpoints: [
            {
              name: 'chapter-function-fit',
              status: 'pass',
              evidence: 'Primary function resolved.',
              implication: 'Function label is stable.',
            },
            {
              name: 'continuity-stability',
              status: 'mixed',
              evidence: 'Identity is mostly stable.',
              implication: 'Manual review may be useful.',
            },
          ],
        },
      ],
    });
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
      rule_checks: [
        {
          action: 'push_conflict',
          status: 'legal',
          prerequisites: ['mainline_progress>=0.20'],
          blockers: [],
          risk_flags: [],
        },
      ],
      recommendations: [
        {
          action: {
            action: 'push_conflict',
            delta: { conflict_intensity: 0.16 },
            explanation: 'Raise direct confrontation.',
          },
          rule_check: {
            action: 'push_conflict',
            status: 'legal',
            prerequisites: ['mainline_progress>=0.20'],
            blockers: [],
            risk_flags: [],
          },
          score: 0.8123,
          details: {
            structure_value: 0.82,
            continuity_safety: 0.71,
            emotional_payoff: 0.67,
            foreshadow_balance: 0.62,
            stage_fit: 1,
            feasibility: 1,
          },
        },
      ],
      evaluation_summary: {
        count: 1,
        top_action: 'push_conflict',
        top_score: 0.8123,
      },
      decision: {
        selected_action: 'deliver_payoff',
        selected_score: 0.9234,
        quality_hint: 'ready',
        rule_status_summary: {
          legal_count: 1,
          blocked_count: 0,
        },
        validation_case_id: 'demo-v2-middle-8',
        explanation: 'Payoff pressure is mature enough for a decisive release.',
        details: {
          payoff_readiness: 0.93,
          continuity_safety: 0.82,
        },
      },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: ['push_conflict'],
        blocked_actions: ['deliver_payoff'],
        top_action: 'push_conflict',
        notes: 'mapped chapter run',
      },
    });
  });

  it('renders backend quality metadata and runs preview against the loaded backend context', async () => {
    const user = userEvent.setup();
    render(<V2WorkbenchPage />);

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Decision Surface' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Validation Rail' })).toBeInTheDocument();
    expect(await screen.findByText('Current Live Chapter')).toBeInTheDocument();
    expect(screen.getByText('approved')).toBeInTheDocument();
    expect(screen.getByText('brisk')).toBeInTheDocument();
    expect(screen.getAllByText('deliver_payoff').length).toBeGreaterThan(0);
    expect(screen.getByText('ready')).toBeInTheDocument();
    expect(
      screen.getAllByText('Payoff pressure is mature enough for a decisive release.').length,
    ).toBeGreaterThan(0);

    await user.selectOptions(screen.getByLabelText('Chapter Context'), 'live-chapter-18');
    await user.click(screen.getByRole('button', { name: 'Run Preview' }));

    await waitFor(() =>
      expect(fetchRecommendationPreviewV2).toHaveBeenLastCalledWith(
        expect.objectContaining({ case_id: 'demo-v2-middle-18' }),
      ),
    );
  });

  it('falls back to legacy recommendation fields when the backend decision object is absent', async () => {
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
    fetchRecommendationPreviewV2.mockResolvedValue({
      case_id: 'demo-v2-middle-18',
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
      rule_checks: [],
      recommendations: [
        {
          action: {
            action: 'push_conflict',
            delta: { conflict_intensity: 0.16 },
            explanation: 'Raise direct confrontation.',
          },
          rule_check: {
            action: 'push_conflict',
            status: 'legal',
            prerequisites: [],
            blockers: [],
            risk_flags: [],
          },
          score: 0.8123,
          details: {
            structure_value: 0.82,
          },
        },
      ],
      evaluation_summary: {
        count: 1,
        top_action: 'push_conflict',
        top_score: 0.8123,
      },
      validation: {
        case_id: 'demo-v2-middle-18',
        accepted_actions: ['push_conflict'],
        blocked_actions: [],
        top_action: 'push_conflict',
        notes: 'mapped chapter run',
      },
    });

    render(<V2WorkbenchPage />);

    expect((await screen.findAllByText('Raise direct confrontation.')).length).toBeGreaterThan(0);
    expect(screen.getByText('No quality metadata loaded.')).toBeInTheDocument();
  });

  it('uses recommendation explanation when decision payload omits explanation details', async () => {
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
      recommendations: [
        {
          action: {
            action: 'push_conflict',
            delta: { conflict_intensity: 0.16 },
            explanation: 'Raise direct confrontation.',
          },
          rule_check: {
            action: 'push_conflict',
            status: 'legal',
            prerequisites: [],
            blockers: [],
            risk_flags: [],
          },
          score: 0.8123,
          details: {
            structure_value: 0.82,
          },
        },
      ],
      evaluation_summary: {
        count: 1,
        top_action: 'push_conflict',
        top_score: 0.8123,
      },
      decision: {
        selected_action: 'push_conflict',
        selected_score: 0.8123,
        quality_hint: 'review',
      },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: ['push_conflict'],
        blocked_actions: [],
        top_action: 'push_conflict',
        notes: 'mapped chapter run',
      },
    });

    render(<V2WorkbenchPage />);

    expect((await screen.findAllByText('Raise direct confrontation.')).length).toBeGreaterThan(0);
  });

  it('ignores stale preview responses and keeps the newest decision visible', async () => {
    let resolveFirst!: (value: unknown) => void;
    let resolveSecond!: (value: unknown) => void;
    const firstResponse = new Promise((resolve) => {
      resolveFirst = resolve;
    });
    const secondResponse = new Promise((resolve) => {
      resolveSecond = resolve;
    });

    fetchRecommendationPreviewV2
      .mockReturnValueOnce(firstResponse)
      .mockReturnValueOnce(secondResponse);

    render(<V2WorkbenchPage />);

    resolveSecond({
      case_id: 'demo-v2-middle-18',
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
      rule_checks: [],
      recommendations: [
        {
          action: {
            action: 'deliver_payoff',
            delta: { payoff_pressure: 0.11 },
            explanation: 'Resolve an owed emotional beat.',
          },
          rule_check: {
            action: 'deliver_payoff',
            status: 'legal',
            prerequisites: [],
            blockers: [],
            risk_flags: [],
          },
          score: 0.93,
          details: {
            payoff_readiness: 0.93,
          },
        },
      ],
      evaluation_summary: {
        count: 1,
        top_action: 'deliver_payoff',
        top_score: 0.93,
      },
      decision: {
        selected_action: 'deliver_payoff',
        selected_score: 0.93,
      },
      validation: {
        case_id: 'demo-v2-middle-18',
        accepted_actions: ['deliver_payoff'],
        blocked_actions: [],
        top_action: 'deliver_payoff',
        notes: 'new run',
      },
    });

    expect((await screen.findAllByText('deliver_payoff')).length).toBeGreaterThan(0);

    resolveFirst({
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
      recommendations: [
        {
          action: {
            action: 'push_conflict',
            delta: { conflict_intensity: 0.16 },
            explanation: 'Raise direct confrontation.',
          },
          rule_check: {
            action: 'push_conflict',
            status: 'legal',
            prerequisites: [],
            blockers: [],
            risk_flags: [],
          },
          score: 0.81,
          details: {
            structure_value: 0.82,
          },
        },
      ],
      evaluation_summary: {
        count: 1,
        top_action: 'push_conflict',
        top_score: 0.81,
      },
      decision: {
        selected_action: 'push_conflict',
        selected_score: 0.81,
      },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: ['push_conflict'],
        blocked_actions: [],
        top_action: 'push_conflict',
        notes: 'old run',
      },
    });

    await waitFor(() =>
      expect(screen.getAllByText('deliver_payoff').length).toBeGreaterThan(0),
    );
    expect(screen.queryByText('Raise direct confrontation.')).not.toBeInTheDocument();
  });

  it('shows fallback notice when backend contexts loading fails', async () => {
    fetchWorkbenchContextsV2.mockRejectedValueOnce(new Error('network-down'));
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
      evaluation_summary: {
        count: 0,
        top_action: '',
        top_score: 0,
      },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: [],
        blocked_actions: [],
        top_action: '',
        notes: 'fallback run',
      },
    });

    render(<V2WorkbenchPage />);

    expect(await screen.findByText(/Using mapped chapter fallback\./)).toBeInTheDocument();
  });

  it('prefers decision accepted and blocked actions over legacy validation arrays', async () => {
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
      evaluation_summary: {
        count: 0,
        top_action: '',
        top_score: 0,
      },
      decision: {
        selected_action: 'push_conflict',
        selected_score: 0.8,
        accepted_actions: ['accepted-from-decision'],
        blocked_actions: ['blocked-from-decision'],
      },
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: [],
        blocked_actions: [],
        top_action: '',
        notes: 'legacy arrays intentionally empty',
      },
    });

    render(<V2WorkbenchPage />);

    expect(await screen.findByText('accepted-from-decision')).toBeInTheDocument();
    expect(screen.getByText('blocked-from-decision')).toBeInTheDocument();
  });
});
