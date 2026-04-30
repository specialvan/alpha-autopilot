import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { CharacterInterviewPanel } from './components/CharacterInterviewPanel';

const { fetchNarrativeV6CharacterInterview, fetchNarrativeV7DecisionPreview } = vi.hoisted(() => ({
  fetchNarrativeV6CharacterInterview: vi.fn(),
  fetchNarrativeV7DecisionPreview: vi.fn(),
}));

vi.mock('../../api', async () => {
  const actual = await vi.importActual<typeof import('../../api')>('../../api');
  return {
    ...actual,
    fetchNarrativeV6CharacterInterview,
    fetchNarrativeV7DecisionPreview,
  };
});

describe('CharacterInterviewPanel', () => {
  it('runs interview and renders returned reply', async () => {
    fetchNarrativeV6CharacterInterview.mockResolvedValue({
      character_id: 'hero',
      reply: '我会先稳住局面，再反击。',
      memory_evidence: ['chapter memory'],
      emotion_state_shift: 'stable',
      ooc_risk_flags: [],
      hidden_info_risk_flags: [],
      transcript: [
        { role: 'user', content: 'test' },
        { role: 'character', content: 'reply' },
      ],
      plot_foreshadow_candidates: ['candidate'],
    });

    const controller = {
      contexts: [
        {
          id: 'ctx-1',
          chapterNumber: 6,
          title: 'Chapter 6',
          summary: 'Context summary',
          state: { characters: { hero: { name: 'hero' } } },
        },
      ],
      selectedChapter: 'ctx-1',
    } as any;

    const user = userEvent.setup();
    render(<CharacterInterviewPanel controller={controller} />);

    await user.click(screen.getByRole('button', { name: 'Run Character Interview' }));

    await waitFor(() => expect(fetchNarrativeV6CharacterInterview).toHaveBeenCalled());
    expect(await screen.findByText('我会先稳住局面，再反击。')).toBeInTheDocument();
  });

  it('runs V6/V7 decision preview and renders route id', async () => {
    fetchNarrativeV7DecisionPreview.mockResolvedValue({
      market_state: {},
      vector: {
        metrics: {},
        composite: 0.57,
      },
      ohlcv: {
        open: 0.56,
        high: 0.62,
        low: 0.51,
        close: 0.57,
        volume: 320,
      },
      decision: {
        decision_type: 'stop_loss',
        risk_level: 'P0',
        route_id: 'R-04',
        reasons: ['T8 opening hook below gate threshold'],
        suggested_actions: ['pause_generation'],
        observe_next_metrics: ['T8'],
      },
      defaults_applied: ['benchmark_state.defaulted'],
    });

    const controller = {
      contexts: [
        {
          id: 'ctx-1',
          chapterNumber: 6,
          title: 'Chapter 6',
          summary: 'Context summary',
          state: {
            chapter_index: 6,
            stage: 'middle',
            conflict_intensity: 0.7,
            foreshadowing_load: 0.4,
            payoff_pressure: 0.35,
            tags: [],
            characters: { hero: { name: 'hero' } },
          },
        },
      ],
      selectedChapter: 'ctx-1',
    } as any;

    const user = userEvent.setup();
    render(<CharacterInterviewPanel controller={controller} />);
    await user.click(screen.getByRole('button', { name: 'Run V6/V7 Decision Preview' }));

    await waitFor(() => expect(fetchNarrativeV7DecisionPreview).toHaveBeenCalled());
    expect(await screen.findByText('R-04')).toBeInTheDocument();
    expect(screen.getByText('stop_loss')).toBeInTheDocument();
  });
});
