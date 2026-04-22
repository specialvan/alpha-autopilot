import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { V2WorkbenchPage } from './V2WorkbenchPage';

const { fetchRecommendationPreviewV2 } = vi.hoisted(() => ({
  fetchRecommendationPreviewV2: vi.fn(),
}));

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api');
  return {
    ...actual,
    fetchRecommendationPreviewV2,
  };
});

describe('V2WorkbenchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
      validation: {
        case_id: 'demo-v2-middle-8',
        accepted_actions: ['push_conflict'],
        blocked_actions: ['deliver_payoff'],
        top_action: 'push_conflict',
        notes: 'mapped chapter run',
      },
    });
  });

  it('renders the workbench rails and runs preview against chapter context', async () => {
    const user = userEvent.setup();
    render(<V2WorkbenchPage />);

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Decision Surface' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Validation Rail' })).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText('Chapter Context'), 'chapter-19');
    await user.click(screen.getByRole('button', { name: 'Run Preview' }));

    await waitFor(() =>
      expect(fetchRecommendationPreviewV2).toHaveBeenLastCalledWith(
        expect.objectContaining({ case_id: 'demo-v2-mid_late-19' }),
      ),
    );
  });
});
