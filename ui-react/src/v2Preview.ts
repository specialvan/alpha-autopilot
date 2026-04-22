import type { NarrativeV2PreviewRequest, NarrativeV2StoryState } from './api';

export const DEFAULT_V2_PREVIEW_STATE: NarrativeV2StoryState = {
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
};

export type NarrativeV2EditableField =
  | 'chapter_index'
  | 'mainline_progress'
  | 'sideplot_progress'
  | 'conflict_intensity'
  | 'emotional_temperature'
  | 'pacing_speed'
  | 'foreshadowing_load'
  | 'payoff_pressure';

export function buildNarrativeV2PreviewRequest(state: NarrativeV2StoryState): NarrativeV2PreviewRequest {
  return {
    case_id: `demo-v2-${state.stage}-${state.chapter_index}`,
    state,
  };
}

export function clampNarrativeV2Value(value: number): number {
  return Math.max(0, Math.min(1, Number(value.toFixed(2))));
}
