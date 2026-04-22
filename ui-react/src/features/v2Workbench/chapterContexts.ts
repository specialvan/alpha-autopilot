import type { ChapterMappedContext } from './types';

export const CHAPTER_MAPPED_CONTEXTS: ChapterMappedContext[] = [
  {
    id: 'chapter-08',
    chapterNumber: 8,
    title: 'Pressure Rises in the Midpoint',
    stage: 'middle',
    summary: 'Mainline pressure climbs while payoff remains immature.',
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
  },
  {
    id: 'chapter-19',
    chapterNumber: 19,
    title: 'Foreshadow Threads Start Converging',
    stage: 'mid_late',
    summary: 'Setups are mature enough for stronger clue and payoff decisions.',
    state: {
      chapter_index: 19,
      stage: 'mid_late',
      mainline_progress: 0.7,
      sideplot_progress: 0.43,
      conflict_intensity: 0.69,
      emotional_temperature: 0.61,
      pacing_speed: 0.53,
      foreshadowing_load: 0.56,
      payoff_pressure: 0.62,
      characters: {},
      tags: ['payoff'],
    },
  },
];
