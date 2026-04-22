import { describe, expect, it } from 'vitest';
import { normalizeWorkbenchContexts } from './backendContexts';

describe('backendContexts', () => {
  it('normalizes backend workbench contexts into chapter mapped contexts', () => {
    const contexts = normalizeWorkbenchContexts({
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

    expect(contexts[0].chapterNumber).toBe(18);
    expect(contexts[0].summary).toContain('History-backed');
  });
});
