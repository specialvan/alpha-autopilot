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

export type V4WorkbenchCandidate = {
  candidateId: string;
  predictedAction: string;
  predictedTurningPoint: string;
  predictedConflictType: string;
  predictedPayoffType: string;
  retentionScore: number;
  tensionScore: number;
  explanation?: string;
  riskFlags: string[];
};

export type V4WorkbenchPreview = {
  enabled: boolean;
  fallbackReason?: string | null;
  candidateCount: number;
  retentionSortKey?: string;
  memorySummary?: {
    contextId?: string;
    historyWindow?: number;
    relationshipHistoryCount: number;
    feedbackHistoryCount: number;
    relationshipTimelineDisplacementCount?: number;
    memoryStrategy?: string;
    relationshipMergeDedupedCount?: number;
    feedbackMergeDedupedCount?: number;
    relationshipCollapsedCount?: number;
    feedbackCollapsedCount?: number;
    relationshipClippedCount?: number;
    feedbackClippedCount?: number;
    relationshipDecayDroppedCount?: number;
    feedbackDecayDroppedCount?: number;
    candidateTimelineCount?: number;
    genreAutoLearningMode?: string;
    genreAutoLearningApplied?: boolean;
    genreAutoLearningSampleCount?: number;
    genreAutoLearningDenoisedCount?: number;
    genreAutoLearningFeedbackSignal?: number;
    genreAutoLearningBiasCount?: number;
    genreAutoLearningGuardTriggered?: boolean;
    genreAutoLearningGuardReason?: string;
    genreAutoLearningFallbackMode?: string;
    genreAutoLearningGuardProfile?: {
      minSamples?: number;
      decay?: number;
      biasLimit?: number;
      maxVolatility?: number;
      maxSignalDivergence?: number;
      extremeSignal?: number;
      extremeMinSamples?: number;
      reversalDivergenceMin?: number;
    };
  };
  genreCalibration?: {
    genre?: string;
    learningMode?: string;
    applied?: boolean;
    feedbackSignal?: number;
    sampleCount?: number;
    denoisedCount?: number;
    guardTriggered?: boolean;
    guardReason?: string;
    fallbackMode?: string;
    acceptRate?: number;
    signalRecent?: number;
    signalLong?: number;
    signalVolatility?: number;
    signalDivergence?: number;
    guardProfile?: {
      minSamples?: number;
      decay?: number;
      biasLimit?: number;
      maxVolatility?: number;
      maxSignalDivergence?: number;
      extremeSignal?: number;
      extremeMinSamples?: number;
      reversalDivergenceMin?: number;
    };
    biasUpdates?: Record<string, number>;
  };
  relationshipGraph?: {
    nodeCount: number;
    edgeCount: number;
    displacementCount: number;
  };
  relationshipDisplacements: Array<{
    sourceCharacter: string;
    targetCharacter: string;
    deltaTension: number;
  }>;
  relationshipTimeline?: Array<{
    chapterIndex: number;
    averageTension: number;
    dominantGap: string;
    sampleCount: number;
    displacementCount: number;
    peakDeltaTension: number;
  }>;
  candidateTimeline?: Array<{
    chapterIndex: number;
    feedbackSignal: number;
    acceptRate: number;
    sampleCount: number;
  }>;
  retentionWriteback?: {
    feedbackCount: number;
    feedbackSignal: number;
    adaptationMode?: string;
    aggregationStrategy?: string;
    feedbackDenoisedCount?: number;
    windowSignals?: Array<{
      windowSize: number;
      signal: number;
      count: number;
      weight: number;
    }>;
  };
  selectedCandidate?: V4WorkbenchCandidate | null;
  topCandidates: V4WorkbenchCandidate[];
  qcSummary?: Record<string, unknown>;
};

export type ChapterMappedContext = {
  id: string;
  chapterNumber: number;
  title: string;
  stage: NarrativeV2StoryState['stage'];
  summary: string;
  state: NarrativeV2StoryState;
  compareBaseline?: {
    baselineContextId?: string;
    baselineChapterNumber?: number;
    delta: Record<string, number>;
  };
  v4Preview?: V4WorkbenchPreview;
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
