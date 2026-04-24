import { describe, expect, it } from 'vitest';
import { computeStateDiff, listChapterMappedContexts, resolveBaseState } from './contextMapping';
import type { ChapterMappedContext } from './types';

const BACKEND_CONTEXT: ChapterMappedContext = {
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
  quality: {
    admission: 'approved',
    styleDna: { pace: 'brisk' },
    checkpointSummary: { total: 2, pass: 2, mixed: 0, fail: 0 },
  },
};

describe('contextMapping', () => {
  it('resolves mapped chapter state from loaded backend contexts before legacy constants', () => {
    const state = resolveBaseState('mapped_chapter', [BACKEND_CONTEXT], BACKEND_CONTEXT.id);

    expect(state.chapter_index).toBe(18);
    expect(state.mainline_progress).toBe(0.61);
    expect(state.stage).toBe('middle');
  });

  it('falls back to legacy mapped contexts when backend contexts are unavailable', () => {
    const chapter = listChapterMappedContexts()[0];
    const state = resolveBaseState('mapped_chapter', [], chapter.id);

    expect(state.chapter_index).toBe(chapter.chapterNumber);
    expect(state.stage).toBe(chapter.stage);
  });

  it('returns only changed fields in the state diff', () => {
    const chapter = listChapterMappedContexts()[0];
    const working = { ...chapter.state, payoff_pressure: 0.48 };

    expect(computeStateDiff(chapter.state, working)).toEqual([
      { field: 'payoff_pressure', previous: 0.32, current: 0.48 },
    ]);
  });
});
