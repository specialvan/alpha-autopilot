import type { NarrativeV2WorkbenchContextsResponse } from '../../api';
import type { ChapterMappedContext } from './types';

export function normalizeWorkbenchContexts(
  payload: NarrativeV2WorkbenchContextsResponse,
): ChapterMappedContext[] {
  return payload.contexts.map((context) => ({
    id: context.id,
    chapterNumber: context.chapterNumber,
    title: context.title,
    stage: context.stage,
    summary: context.summary,
    state: context.state,
  }));
}
