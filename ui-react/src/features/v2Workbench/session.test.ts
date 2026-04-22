import { describe, expect, it, vi } from 'vitest';
import { appendRunEntry, buildComparisonDelta, buildSnapshotPayload } from './session';

describe('session helpers', () => {
  it('appends a run entry and computes deltas', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-04-22T10:00:00Z'));

    const previous = appendRunEntry([], {
      source: 'demo',
      label: 'demo-middle',
      submittedState: {
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
      preview: {
        case_id: 'demo-middle',
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
        evaluation_summary: { count: 1, top_action: 'push_conflict', top_score: 0.81 },
        validation: {
          case_id: 'demo-middle',
          accepted_actions: ['push_conflict'],
          blocked_actions: ['deliver_payoff'],
          top_action: 'push_conflict',
          notes: 'demo',
        },
      },
    })[0];

    const current = appendRunEntry([previous], {
      source: 'demo',
      label: 'demo-middle',
      submittedState: previous.submittedState,
      preview: {
        ...previous.preview,
        evaluation_summary: { count: 1, top_action: 'reveal_clue', top_score: 0.77 },
        validation: {
          ...previous.preview.validation,
          top_action: 'reveal_clue',
          blocked_actions: [],
        },
      },
    })[1];

    expect(buildComparisonDelta(previous.preview, current.preview).topActionChanged).toBe(true);
    expect(
      buildSnapshotPayload({
        source: 'demo',
        selectedChapter: null,
        baseState: previous.submittedState,
        overrides: {},
        workingState: current.submittedState,
        currentPreview: current.preview,
        comparisonPreview: previous.preview,
      }).currentPreview.validation.top_action,
    ).toBe('reveal_clue');

    vi.useRealTimers();
  });
});
