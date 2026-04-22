import type { NarrativeV2StoryState } from '../../api';
import { DEFAULT_V2_PREVIEW_STATE } from '../../v2Preview';
import { CHAPTER_MAPPED_CONTEXTS } from './chapterContexts';
import type { StateDiffEntry, V2ContextSource } from './types';

const EXCLUDED_DIFF_FIELDS = new Set<keyof NarrativeV2StoryState>(['characters', 'tags']);

export function listChapterMappedContexts() {
  return CHAPTER_MAPPED_CONTEXTS;
}

export function resolveBaseState(source: V2ContextSource, chapterId?: string): NarrativeV2StoryState {
  if (source === 'mapped_chapter') {
    const context = CHAPTER_MAPPED_CONTEXTS.find((item) => item.id === chapterId) ?? CHAPTER_MAPPED_CONTEXTS[0];
    return context.state;
  }

  return DEFAULT_V2_PREVIEW_STATE;
}

export function computeStateDiff(
  baseState: NarrativeV2StoryState,
  workingState: NarrativeV2StoryState,
): StateDiffEntry[] {
  return (Object.keys(baseState) as Array<keyof NarrativeV2StoryState>)
    .filter((field) => !EXCLUDED_DIFF_FIELDS.has(field))
    .filter((field) => baseState[field] !== workingState[field])
    .map((field) => ({
      field,
      previous: baseState[field] as number | string,
      current: workingState[field] as number | string,
    }));
}
