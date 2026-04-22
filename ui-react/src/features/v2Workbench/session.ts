import type { NarrativeV2PreviewResponse, NarrativeV2StoryState } from '../../api';
import type { V2ContextSource, WorkbenchRunEntry } from './types';

export function appendRunEntry(
  history: WorkbenchRunEntry[],
  input: {
    source: V2ContextSource;
    label: string;
    submittedState: NarrativeV2StoryState;
    preview: NarrativeV2PreviewResponse;
  },
): WorkbenchRunEntry[] {
  return history.concat({
    id: `${Date.now()}-${history.length + 1}`,
    timestamp: new Date().toISOString(),
    source: input.source,
    label: input.label,
    submittedState: input.submittedState,
    preview: input.preview,
  });
}

export function buildComparisonDelta(
  previous: NarrativeV2PreviewResponse,
  current: NarrativeV2PreviewResponse,
) {
  const previousBlockers = new Set(previous.validation.blocked_actions);
  const currentBlockers = new Set(current.validation.blocked_actions);

  return {
    topActionChanged: previous.evaluation_summary.top_action !== current.evaluation_summary.top_action,
    previousTopAction: previous.evaluation_summary.top_action,
    currentTopAction: current.evaluation_summary.top_action,
    topScoreDelta: Number(
      (current.evaluation_summary.top_score - previous.evaluation_summary.top_score).toFixed(4),
    ),
    addedBlockers: [...currentBlockers].filter((item) => !previousBlockers.has(item)),
    removedBlockers: [...previousBlockers].filter((item) => !currentBlockers.has(item)),
  };
}

export function buildSnapshotPayload(input: {
  source: V2ContextSource;
  selectedChapter: string | null;
  baseState: NarrativeV2StoryState;
  overrides: Partial<NarrativeV2StoryState>;
  workingState: NarrativeV2StoryState;
  currentPreview: NarrativeV2PreviewResponse;
  comparisonPreview: NarrativeV2PreviewResponse | null;
}) {
  return {
    exportedAt: new Date().toISOString(),
    source: input.source,
    selectedChapter: input.selectedChapter,
    baseState: input.baseState,
    overrides: input.overrides,
    workingState: input.workingState,
    currentPreview: input.currentPreview,
    comparisonPreview: input.comparisonPreview,
  };
}
