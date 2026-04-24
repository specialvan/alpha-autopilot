import { describe, expect, it } from 'vitest';
import { normalizeWorkbenchContexts } from './backendContexts';

describe('backendContexts', () => {
  it('normalizes backend workbench contexts into chapter mapped contexts with quality metadata', () => {
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
          admission: 'approved',
          primary_function: 'conflict-escalation',
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
          quality_notes: 'Derived from imported quality pipeline.',
        },
      ],
    });

    expect(contexts[0].chapterNumber).toBe(18);
    expect(contexts[0].summary).toContain('History-backed');
    expect(contexts[0].quality).toEqual({
      admission: 'approved',
      primaryFunction: 'conflict-escalation',
      styleDna: {
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
      checkpointSummary: {
        total: 2,
        pass: 1,
        mixed: 1,
        fail: 0,
      },
      qualityNotes: 'Derived from imported quality pipeline.',
    });
  });

  it('keeps quality metadata undefined when the backend does not provide it', () => {
    const contexts = normalizeWorkbenchContexts({
      contexts: [
        {
          id: 'live-chapter-04',
          chapterNumber: 4,
          title: 'Live Context',
          stage: 'middle',
          summary: 'No quality metadata attached',
          state: {
            chapter_index: 4,
            stage: 'middle',
            mainline_progress: 0.38,
            sideplot_progress: 0.28,
            conflict_intensity: 0.55,
            emotional_temperature: 0.47,
            pacing_speed: 0.46,
            foreshadowing_load: 0.33,
            payoff_pressure: 0.29,
            characters: {},
            tags: ['middle'],
          },
        },
      ],
    });

    expect(contexts[0].quality).toBeUndefined();
  });
});
