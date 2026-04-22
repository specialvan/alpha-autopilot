import type { NarrativeV2PreviewResponse, NarrativeV2StoryState } from '../../api';

export type V2ContextSource = 'demo' | 'mapped_chapter' | 'manual_override';

export type ChapterMappedContext = {
  id: string;
  chapterNumber: number;
  title: string;
  stage: NarrativeV2StoryState['stage'];
  summary: string;
  state: NarrativeV2StoryState;
};

export type StateDiffEntry = {
  field: keyof NarrativeV2StoryState;
  previous: number | string;
  current: number | string;
};

export type WorkbenchRunEntry = {
  id: string;
  timestamp: string;
  source: V2ContextSource;
  label: string;
  submittedState: NarrativeV2StoryState;
  preview: NarrativeV2PreviewResponse;
};
