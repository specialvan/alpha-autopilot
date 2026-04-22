import { describe, expect, it } from 'vitest';
import { computeStateDiff, listChapterMappedContexts, resolveBaseState } from './contextMapping';

describe('contextMapping', () => {
  it('resolves a mapped chapter into a story state', () => {
    const chapter = listChapterMappedContexts()[0];
    const state = resolveBaseState('mapped_chapter', chapter.id);

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
