import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { V2WorkbenchPage } from './V2WorkbenchPage';

const {
  fetchNarrativeV4WorkbenchPreview,
  fetchRecommendationPreviewV2,
  fetchWorkbenchContextsV2,
  refreshWorkbenchContextsV2,
} = vi.hoisted(() => ({
  fetchNarrativeV4WorkbenchPreview: vi.fn(),
  fetchRecommendationPreviewV2: vi.fn(),
  fetchWorkbenchContextsV2: vi.fn(),
  refreshWorkbenchContextsV2: vi.fn(),
}));

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api');
  return {
    ...actual,
    fetchNarrativeV4WorkbenchPreview,
    fetchRecommendationPreviewV2,
    fetchWorkbenchContextsV2,
    refreshWorkbenchContextsV2,
  };
});

describe('V2WorkbenchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchNarrativeV4WorkbenchPreview.mockResolvedValue({
      enabled: true,
      candidate_count: 2,
      retention_sort_key: 'retention_score',
      relationship_graph: {
        node_count: 2,
        edge_count: 1,
        displacement_count: 1,
      },
      relationship_displacements: [
        {
          source_character: 'live-chapter-18-hero',
          target_character: 'live-chapter-18-rival',
          delta_tension: 0.22,
        },
      ],
      retention_writeback: {
        feedback_count: 2,
        feedback_signal: -0.3,
      },
      memory_summary: {
        context_id: 'live-chapter-18',
        history_window: 50,
        relationship_history_count: 6,
        feedback_history_count: 4,
        relationship_timeline_displacement_count: 1,
        memory_strategy: 'append-window-decay-denoise-v2',
        relationship_decay_dropped_count: 1,
        feedback_decay_dropped_count: 1,
        candidate_timeline_count: 1,
        genre_auto_learning_mode: 'feedback-adaptive-v1',
        genre_auto_learning_applied: true,
        genre_auto_learning_sample_count: 5,
        genre_auto_learning_denoised_count: 0,
        genre_auto_learning_feedback_signal: 0.27,
        genre_auto_learning_bias_count: 2,
        genre_auto_learning_guard_triggered: false,
        genre_auto_learning_fallback_mode: 'bias-update-applied',
      },
      genre_calibration: {
        genre: 'power_fantasy',
        learning_mode: 'feedback-adaptive-v1',
        applied: true,
        feedback_signal: 0.27,
        sample_count: 5,
        denoised_count: 0,
        guard_triggered: false,
        fallback_mode: 'bias-update-applied',
        accept_rate: 0.8,
        signal_recent: 0.31,
        signal_long: 0.27,
        signal_volatility: 0.18,
        signal_divergence: 0.04,
        bias_updates: {
          risk_appetite_bias: 0.024,
          avoidance_bias: -0.018,
        },
      },
      relationship_timeline: [
        {
          chapter_index: 18,
          average_tension: 0.71,
          dominant_gap: 'status',
          sample_count: 2,
          displacement_count: 1,
          peak_delta_tension: 0.22,
        },
      ],
      candidate_timeline: [
        {
          chapter_index: 18,
          feedback_signal: -0.15,
          accept_rate: 0.5,
          sample_count: 2,
        },
      ],
      selected_candidate: {
        candidate_id: 'candidate-1',
        predicted_action: 'break-the-balance',
        predicted_turning_point: 'relationship-shift',
        predicted_conflict_type: 'status-clash',
        predicted_payoff_type: 'relationship-reversal',
        retention_score: 0.73,
        tension_score: 0.71,
        explanation: 'Relationship tension escalates into a direct confrontation.',
        risk_flags: ['template-risk'],
      },
      top_candidates: [
        {
          candidate_id: 'candidate-1',
          predicted_action: 'break-the-balance',
          predicted_turning_point: 'relationship-shift',
          predicted_conflict_type: 'status-clash',
          predicted_payoff_type: 'relationship-reversal',
          retention_score: 0.73,
          tension_score: 0.71,
          explanation: 'Relationship tension escalates into a direct confrontation.',
          risk_flags: ['template-risk'],
        },
      ],
      qc_summary: {
        warnings: ['template-risk'],
      },
      v4_input_profile: {
        chapter_index: 18,
        stage: 'middle',
      },
    });
    fetchWorkbenchContextsV2.mockResolvedValue({
      source: 'plotpilot_report',
      context_contract: 'real_chapter_context_v2',
      report_path: 'D:/workspace/alpha-autopilot/artifacts/testing/plotpilot/raw/model_switch_tests/run-01/report.json',
      report_url: 'https://plotpilot.example/api/latest-report?model=gpt-5.4',
      run_id: 'v3_20260421_220604',
      preferred_model: 'gpt-5.4',
      resolved_model: 'gpt-5.4',
      report_success_rate: 0.9,
      arbitration_strategy: 'manifest-model-success-rate-v1',
      source_diagnostics: {
        online_report: {
          status: 'http-error',
          attempted: true,
          attempts_count: 2,
          max_attempts: 3,
          retried: true,
          retry_exhausted: false,
          attempt_history: [
            {
              attempt: 2,
              status: 'ok',
            },
            {
              attempt: 1,
              status: 'http-error',
              http_status: 503,
              error_type: 'HTTPError',
            },
          ],
          http_status: 503,
          error_type: 'HTTPError',
          request_url: 'https://plotpilot.example/api/latest-report?model=gpt-5.4',
          error_message: 'HTTP Error 503: Service Unavailable',
        },
        local_report: {
          status: 'ok',
        },
      },
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
          compare_baseline: {
            baseline_context_id: 'live-chapter-17',
            baseline_chapter_number: 17,
            delta: {
              mainline_progress: 0.03,
              payoff_pressure: 0.07,
            },
          },
          v4_preview: {
            enabled: true,
            candidate_count: 2,
            retention_sort_key: 'retention_score',
            memory_summary: {
              context_id: 'live-chapter-18',
              history_window: 50,
              relationship_history_count: 6,
              feedback_history_count: 4,
              relationship_timeline_displacement_count: 1,
              memory_strategy: 'append-window-decay-denoise-v2',
              relationship_decay_dropped_count: 1,
              feedback_decay_dropped_count: 1,
              candidate_timeline_count: 1,
              genre_auto_learning_mode: 'feedback-adaptive-v1',
              genre_auto_learning_applied: true,
              genre_auto_learning_sample_count: 5,
              genre_auto_learning_denoised_count: 0,
              genre_auto_learning_feedback_signal: 0.27,
              genre_auto_learning_bias_count: 2,
              genre_auto_learning_guard_triggered: false,
              genre_auto_learning_fallback_mode: 'bias-update-applied',
            },
            genre_calibration: {
              genre: 'power_fantasy',
              learning_mode: 'feedback-adaptive-v1',
              applied: true,
              feedback_signal: 0.27,
              sample_count: 5,
              denoised_count: 0,
              guard_triggered: false,
              fallback_mode: 'bias-update-applied',
              accept_rate: 0.8,
              signal_recent: 0.31,
              signal_long: 0.27,
              signal_volatility: 0.18,
              signal_divergence: 0.04,
              bias_updates: {
                risk_appetite_bias: 0.024,
                avoidance_bias: -0.018,
              },
            },
            relationship_timeline: [
              {
                chapter_index: 18,
                average_tension: 0.71,
                dominant_gap: 'status',
                sample_count: 2,
                displacement_count: 1,
                peak_delta_tension: 0.22,
              },
            ],
            candidate_timeline: [
              {
                chapter_index: 18,
                feedback_signal: -0.15,
                accept_rate: 0.5,
                sample_count: 2,
              },
            ],
            selected_candidate: {
              candidate_id: 'candidate-1',
              predicted_action: 'break-the-balance',
              predicted_turning_point: 'relationship-shift',
              predicted_conflict_type: 'status-clash',
              predicted_payoff_type: 'relationship-reversal',
              retention_score: 0.73,
              tension_score: 0.71,
              explanation: 'Relationship tension escalates into a direct confrontation.',
              risk_flags: ['template-risk'],
            },
            top_candidates: [
              {
                candidate_id: 'candidate-1',
                predicted_action: 'break-the-balance',
                predicted_turning_point: 'relationship-shift',
                predicted_conflict_type: 'status-clash',
                predicted_payoff_type: 'relationship-reversal',
                retention_score: 0.73,
                tension_score: 0.71,
                explanation: 'Relationship tension escalates into a direct confrontation.',
                risk_flags: ['template-risk'],
              },
            ],
            qc_summary: {
              warnings: ['template-risk'],
            },
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
    refreshWorkbenchContextsV2.mockResolvedValue({
      source: 'plotpilot_api',
      context_contract: 'real_chapter_context_v2',
      run_id: 'online-run-03',
      preferred_model: 'gpt-5.4',
      resolved_model: 'gpt-5.4',
      source_diagnostics: {
        online_report: {
          status: 'ok',
          attempted: true,
        },
      },
      contexts: [
        {
          id: 'plotpilot-chapter-03',
          chapterNumber: 3,
          title: 'Online Chapter Three',
          stage: 'middle',
          summary: 'Online report context',
          state: {
            chapter_index: 3,
            stage: 'middle',
            mainline_progress: 0.31,
            sideplot_progress: 0.24,
            conflict_intensity: 0.66,
            emotional_temperature: 0.52,
            pacing_speed: 0.49,
            foreshadowing_load: 0.29,
            payoff_pressure: 0.25,
            characters: {},
            tags: ['plotpilot_import', 'middle'],
          },
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
    expect(screen.getByText(/backend source:/i)).toBeInTheDocument();
    expect(screen.getByText(/online source:/i)).toBeInTheDocument();
    expect(screen.getByText(/arbitration:/i)).toBeInTheDocument();
    expect(screen.getByText(/success rate:/i)).toBeInTheDocument();
    expect(screen.getByText(/report path:/i)).toBeInTheDocument();
    expect(screen.getByText(/report url:/i)).toBeInTheDocument();
    expect(screen.getByText(/online request:/i)).toBeInTheDocument();
    expect(screen.getByText(/online error:/i)).toBeInTheDocument();
    expect(screen.getByText(/online attempts:/i)).toBeInTheDocument();
    expect(screen.getByText(/diagnostics:/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Show Diagnostics' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Copy Diagnostics' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Copy Online Diagnostics' })).toBeInTheDocument();
    expect(await screen.findByText('Current Live Chapter')).toBeInTheDocument();
    expect(screen.getByText('approved')).toBeInTheDocument();
    expect(screen.getByText('brisk')).toBeInTheDocument();
    expect(screen.getAllByText('break-the-balance').length).toBeGreaterThan(0);
    expect(screen.getAllByText('template-risk').length).toBeGreaterThan(0);
    expect(screen.getByText('Graph Nodes / Edges')).toBeInTheDocument();
    expect(screen.getByText('2 / 1')).toBeInTheDocument();
    expect(screen.getByText('Retention Feedback')).toBeInTheDocument();
    expect(screen.getByText('Memory Histories')).toBeInTheDocument();
    expect(screen.getByText('Relationship Timeline')).toBeInTheDocument();
    expect(screen.getByText('Candidate Timeline')).toBeInTheDocument();
    expect(screen.getByText('Timeline Displacements')).toBeInTheDocument();
    expect(screen.getByText('Memory Strategy')).toBeInTheDocument();
    expect(screen.getByText('Genre Learning')).toBeInTheDocument();
    expect(screen.getByText('Genre Feedback Signal')).toBeInTheDocument();
    expect(screen.getByText('Genre Bias Updates')).toBeInTheDocument();
    expect(screen.getByText('Genre Fallback')).toBeInTheDocument();
    expect(screen.getByText('Recent/Long Divergence')).toBeInTheDocument();
    expect(screen.getByText('Genre Profile')).toBeInTheDocument();
    expect(screen.getByText('Feedback Decay Drops')).toBeInTheDocument();
    expect(screen.getByText('Relationship Decay Drops')).toBeInTheDocument();
    expect(screen.getByLabelText('Relationship Timeline Chart')).toBeInTheDocument();
    expect(screen.getByLabelText('Candidate Timeline Chart')).toBeInTheDocument();
    expect(screen.getByText('Compare Baseline')).toBeInTheDocument();
    expect(screen.getAllByText('deliver_payoff').length).toBeGreaterThan(0);
    expect(screen.getByText('ready')).toBeInTheDocument();
    expect(
      screen.getAllByText('Payoff pressure is mature enough for a decisive release.').length,
    ).toBeGreaterThan(0);
    await user.click(screen.getByRole('button', { name: 'Show Diagnostics' }));
    expect(screen.getByRole('button', { name: 'Hide Diagnostics' })).toBeInTheDocument();
    expect(screen.getByLabelText('Diagnostics JSON')).toBeInTheDocument();
    expect(screen.getByLabelText('Diagnostics Source Filter')).toBeInTheDocument();
    expect(screen.getByLabelText('Diagnostics Failures Only')).toBeInTheDocument();
    expect(screen.getByLabelText('Online Attempt History')).toBeInTheDocument();
    const initialTableRows = within(screen.getByLabelText('Online Attempt History')).getAllByRole('row');
    expect(initialTableRows[1]).toHaveTextContent('http-error');

    await user.selectOptions(screen.getByLabelText('Diagnostics Source Filter'), 'local_report');
    expect(screen.queryByLabelText('Online Attempt History')).not.toBeInTheDocument();

    await user.click(screen.getByLabelText('Diagnostics Failures Only'));
    expect(screen.getByText(/diagnostics:\s*none/i)).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText('Diagnostics Source Filter'), 'all');
    const filteredTableRows = within(screen.getByLabelText('Online Attempt History')).getAllByRole('row');
    expect(filteredTableRows).toHaveLength(2);
    expect(filteredTableRows[1]).toHaveTextContent('http-error');
    await user.click(screen.getByRole('button', { name: 'Copy Diagnostics' }));
    expect(await screen.findByText(/diagnostics copy:/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Copy Online Diagnostics' }));
    expect(await screen.findByText(/diagnostics copy:/i)).toBeInTheDocument();

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

  it('refreshes contexts with normal and online-only modes', async () => {
    const user = userEvent.setup();
    render(<V2WorkbenchPage />);

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Refresh Contexts' }));
    await waitFor(() =>
      expect(refreshWorkbenchContextsV2).toHaveBeenCalledWith({ onlineOnly: false }),
    );

    await user.click(screen.getByRole('button', { name: 'Refresh Online Only' }));
    await waitFor(() =>
      expect(refreshWorkbenchContextsV2).toHaveBeenCalledWith({ onlineOnly: true }),
    );
  });

  it('shows copied-online status when clipboard write succeeds', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    });

    render(<V2WorkbenchPage />);

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Show Diagnostics' }));
    await user.click(screen.getByRole('button', { name: 'Copy Online Diagnostics' }));

    await waitFor(() => expect(writeText).toHaveBeenCalled());
    expect(await screen.findByText(/diagnostics copy: copied-online/i)).toBeInTheDocument();
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
