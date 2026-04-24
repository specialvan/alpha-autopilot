import type { NarrativeV2PreviewResponse, NarrativeV2StoryState } from '../../api';

export type V2ContextSource = 'demo' | 'mapped_chapter' | 'manual_override';

export type ContextCheckpoint = {
  name: string;
  status: 'pass' | 'mixed' | 'fail';
  evidence?: string;
  implication?: string;
};

export type ContextCheckpointSummary = {
  total: number;
  pass: number;
  mixed: number;
  fail: number;
};

export type ContextQualityMetadata = {
  admission?: string;
  primaryFunction?: string;
  styleDna?: Record<string, string>;
  checkpoints?: ContextCheckpoint[];
  checkpointSummary?: ContextCheckpointSummary;
  qualityNotes?: string;
};

export type ChapterMappedContext = {
  id: string;
  chapterNumber: number;
  title: string;
  stage: NarrativeV2StoryState['stage'];
  summary: string;
  state: NarrativeV2StoryState;
  quality?: ContextQualityMetadata;
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
