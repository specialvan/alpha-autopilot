import type {
  NarrativeV2CheckpointSummary,
  NarrativeV2ContextCheckpoint,
  NarrativeV2WorkbenchContext,
  NarrativeV2WorkbenchContextsResponse,
  NarrativeV4WorkbenchCandidate,
  NarrativeV4WorkbenchPreview,
} from '../../api';
import type {
  ChapterMappedContext,
  ContextCheckpoint,
  ContextCheckpointSummary,
  ContextQualityMetadata,
  V4WorkbenchCandidate,
  V4WorkbenchPreview,
} from './types';

function normalizeCheckpoints(checkpoints?: NarrativeV2ContextCheckpoint[]): ContextCheckpoint[] | undefined {
  if (!checkpoints?.length) {
    return undefined;
  }

  return checkpoints.map((checkpoint) => ({
    name: checkpoint.name,
    status: checkpoint.status,
    evidence: checkpoint.evidence,
    implication: checkpoint.implication,
  }));
}

function normalizeCheckpointSummary(
  summary?: NarrativeV2CheckpointSummary,
  checkpoints?: ContextCheckpoint[],
): ContextCheckpointSummary | undefined {
  if (summary) {
    return {
      total: summary.total,
      pass: summary.pass,
      mixed: summary.mixed,
      fail: summary.fail,
    };
  }

  if (!checkpoints?.length) {
    return undefined;
  }

  return checkpoints.reduce<ContextCheckpointSummary>(
    (accumulator, checkpoint) => {
      accumulator.total += 1;
      accumulator[checkpoint.status] += 1;
      return accumulator;
    },
    { total: 0, pass: 0, mixed: 0, fail: 0 },
  );
}

function normalizeStyleDna(styleDna?: Record<string, string>): Record<string, string> | undefined {
  if (!styleDna || Object.keys(styleDna).length === 0) {
    return undefined;
  }

  return styleDna;
}

function normalizeContextQuality(context: NarrativeV2WorkbenchContext): ContextQualityMetadata | undefined {
  const rawQuality = context.quality;
  const checkpoints = normalizeCheckpoints(rawQuality?.checkpoints ?? context.checkpoints);
  const checkpointSummary = normalizeCheckpointSummary(
    rawQuality?.checkpoint_summary ?? context.checkpoint_summary,
    checkpoints,
  );
  const styleDna = normalizeStyleDna(rawQuality?.style_dna ?? context.style_dna);
  const quality: ContextQualityMetadata = {
    admission: rawQuality?.admission ?? context.admission,
    primaryFunction: rawQuality?.primary_function ?? context.primary_function,
    styleDna,
    checkpoints,
    checkpointSummary,
    qualityNotes: rawQuality?.quality_notes ?? context.quality_notes,
  };

  if (
    !quality.admission
    && !quality.primaryFunction
    && !quality.styleDna
    && !quality.checkpoints
    && !quality.checkpointSummary
    && !quality.qualityNotes
  ) {
    return undefined;
  }

  return quality;
}

function normalizeV4Candidate(
  candidate?: NarrativeV4WorkbenchCandidate | null,
): V4WorkbenchCandidate | undefined {
  if (!candidate) {
    return undefined;
  }

  return {
    candidateId: candidate.candidate_id,
    predictedAction: candidate.predicted_action,
    predictedTurningPoint: candidate.predicted_turning_point,
    predictedConflictType: candidate.predicted_conflict_type,
    predictedPayoffType: candidate.predicted_payoff_type,
    retentionScore: candidate.retention_score,
    tensionScore: candidate.tension_score,
    explanation: candidate.explanation,
    riskFlags: candidate.risk_flags ?? [],
  };
}

export function normalizeV4Preview(
  preview?: NarrativeV4WorkbenchPreview,
): V4WorkbenchPreview | undefined {
  if (!preview) {
    return undefined;
  }

  const topCandidates = (preview.top_candidates ?? [])
    .map((candidate) => normalizeV4Candidate(candidate))
    .filter((candidate): candidate is V4WorkbenchCandidate => Boolean(candidate));
  const selectedCandidate = normalizeV4Candidate(preview.selected_candidate);
  const relationshipGraphRaw = preview.relationship_graph;
  const relationshipGraph = relationshipGraphRaw
    ? {
      nodeCount: relationshipGraphRaw.node_count,
      edgeCount: relationshipGraphRaw.edge_count,
      displacementCount: relationshipGraphRaw.displacement_count,
    }
    : undefined;
  const relationshipDisplacements = (preview.relationship_displacements ?? [])
    .map((item) => {
      if (!item || typeof item !== 'object') {
        return null;
      }
      const row = item as Record<string, unknown>;
      const sourceCharacter = typeof row.source_character === 'string' ? row.source_character : '';
      const targetCharacter = typeof row.target_character === 'string' ? row.target_character : '';
      const deltaTension = typeof row.delta_tension === 'number' ? row.delta_tension : 0;
      if (!sourceCharacter || !targetCharacter) {
        return null;
      }
      return {
        sourceCharacter,
        targetCharacter,
        deltaTension,
      };
    })
    .filter((item): item is { sourceCharacter: string; targetCharacter: string; deltaTension: number } => Boolean(item));
  const relationshipTimeline = (preview.relationship_timeline ?? [])
    .map((item) => {
      if (!item || typeof item !== 'object') {
        return null;
      }
      const row = item as Record<string, unknown>;
      const chapterIndex = typeof row.chapter_index === 'number' ? row.chapter_index : null;
      const averageTension = typeof row.average_tension === 'number' ? row.average_tension : null;
      const dominantGap = typeof row.dominant_gap === 'string' ? row.dominant_gap : '';
      const sampleCount = typeof row.sample_count === 'number' ? row.sample_count : null;
      const displacementCount = typeof row.displacement_count === 'number' ? row.displacement_count : 0;
      const peakDeltaTension = typeof row.peak_delta_tension === 'number' ? row.peak_delta_tension : 0;
      if (chapterIndex === null || averageTension === null || !dominantGap || sampleCount === null) {
        return null;
      }
      return {
        chapterIndex,
        averageTension,
        dominantGap,
        sampleCount,
        displacementCount,
        peakDeltaTension,
      };
    })
    .filter(
      (
        item,
      ): item is {
        chapterIndex: number;
        averageTension: number;
        dominantGap: string;
        sampleCount: number;
        displacementCount: number;
        peakDeltaTension: number;
      } =>
        Boolean(item),
    );
  const candidateTimeline = (preview.candidate_timeline ?? [])
    .map((item) => {
      if (!item || typeof item !== 'object') {
        return null;
      }
      const row = item as Record<string, unknown>;
      const chapterIndex = typeof row.chapter_index === 'number' ? row.chapter_index : null;
      const feedbackSignal = typeof row.feedback_signal === 'number' ? row.feedback_signal : null;
      const acceptRate = typeof row.accept_rate === 'number' ? row.accept_rate : null;
      const sampleCount = typeof row.sample_count === 'number' ? row.sample_count : null;
      if (chapterIndex === null || feedbackSignal === null || acceptRate === null || sampleCount === null) {
        return null;
      }
      return {
        chapterIndex,
        feedbackSignal,
        acceptRate,
        sampleCount,
      };
    })
    .filter(
      (
        item,
      ): item is {
        chapterIndex: number;
        feedbackSignal: number;
        acceptRate: number;
        sampleCount: number;
      } =>
        Boolean(item),
    );
  const genreCalibrationRaw = preview.genre_calibration;
  const genreCalibration = genreCalibrationRaw && typeof genreCalibrationRaw === 'object'
    ? (() => {
      const row = genreCalibrationRaw as Record<string, unknown>;
      const normalized: {
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
      } = {};
      if (typeof row.genre === 'string' && row.genre.length > 0) {
        normalized.genre = row.genre;
      }
      if (typeof row.learning_mode === 'string' && row.learning_mode.length > 0) {
        normalized.learningMode = row.learning_mode;
      }
      if (typeof row.applied === 'boolean') {
        normalized.applied = row.applied;
      }
      if (typeof row.feedback_signal === 'number') {
        normalized.feedbackSignal = row.feedback_signal;
      }
      if (typeof row.sample_count === 'number') {
        normalized.sampleCount = row.sample_count;
      }
      if (typeof row.denoised_count === 'number') {
        normalized.denoisedCount = row.denoised_count;
      }
      if (typeof row.guard_triggered === 'boolean') {
        normalized.guardTriggered = row.guard_triggered;
      }
      if (typeof row.guard_reason === 'string' && row.guard_reason.length > 0) {
        normalized.guardReason = row.guard_reason;
      }
      if (typeof row.fallback_mode === 'string' && row.fallback_mode.length > 0) {
        normalized.fallbackMode = row.fallback_mode;
      }
      if (typeof row.accept_rate === 'number') {
        normalized.acceptRate = row.accept_rate;
      }
      if (typeof row.signal_recent === 'number') {
        normalized.signalRecent = row.signal_recent;
      }
      if (typeof row.signal_long === 'number') {
        normalized.signalLong = row.signal_long;
      }
      if (typeof row.signal_volatility === 'number') {
        normalized.signalVolatility = row.signal_volatility;
      }
      if (typeof row.signal_divergence === 'number') {
        normalized.signalDivergence = row.signal_divergence;
      }
      if (row.guard_profile && typeof row.guard_profile === 'object') {
        const profile = row.guard_profile as Record<string, unknown>;
        const normalizedProfile: {
          minSamples?: number;
          decay?: number;
          biasLimit?: number;
          maxVolatility?: number;
          maxSignalDivergence?: number;
          extremeSignal?: number;
          extremeMinSamples?: number;
          reversalDivergenceMin?: number;
        } = {};
        if (typeof profile.min_samples === 'number') {
          normalizedProfile.minSamples = profile.min_samples;
        }
        if (typeof profile.decay === 'number') {
          normalizedProfile.decay = profile.decay;
        }
        if (typeof profile.bias_limit === 'number') {
          normalizedProfile.biasLimit = profile.bias_limit;
        }
        if (typeof profile.max_volatility === 'number') {
          normalizedProfile.maxVolatility = profile.max_volatility;
        }
        if (typeof profile.max_signal_divergence === 'number') {
          normalizedProfile.maxSignalDivergence = profile.max_signal_divergence;
        }
        if (typeof profile.extreme_signal === 'number') {
          normalizedProfile.extremeSignal = profile.extreme_signal;
        }
        if (typeof profile.extreme_min_samples === 'number') {
          normalizedProfile.extremeMinSamples = profile.extreme_min_samples;
        }
        if (typeof profile.reversal_divergence_min === 'number') {
          normalizedProfile.reversalDivergenceMin = profile.reversal_divergence_min;
        }
        if (Object.keys(normalizedProfile).length > 0) {
          normalized.guardProfile = normalizedProfile;
        }
      }
      if (row.bias_updates && typeof row.bias_updates === 'object') {
        const parsedUpdates = Object.fromEntries(
          Object.entries(row.bias_updates as Record<string, unknown>).filter(
            (entry): entry is [string, number] => typeof entry[1] === 'number',
          ),
        );
        if (Object.keys(parsedUpdates).length > 0) {
          normalized.biasUpdates = parsedUpdates;
        }
      }
      return normalized;
    })()
    : undefined;
  const retentionWritebackRaw = preview.retention_writeback;
  const retentionWriteback = retentionWritebackRaw && typeof retentionWritebackRaw === 'object'
    ? (() => {
      const row = retentionWritebackRaw as Record<string, unknown>;
      const normalized: {
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
      } = {
        feedbackCount:
          typeof row.feedback_count === 'number'
            ? row.feedback_count
            : 0,
        feedbackSignal:
          typeof row.feedback_signal === 'number'
            ? row.feedback_signal
            : 0,
      };
      const adaptationMode =
        typeof row.adaptation_mode === 'string'
          ? row.adaptation_mode
          : undefined;
      if (adaptationMode !== undefined) {
        normalized.adaptationMode = adaptationMode;
      }
      const aggregationStrategy =
        typeof row.aggregation_strategy === 'string'
          ? row.aggregation_strategy
          : undefined;
      if (aggregationStrategy !== undefined) {
        normalized.aggregationStrategy = aggregationStrategy;
      }
      if (typeof row.feedback_denoised_count === 'number') {
        normalized.feedbackDenoisedCount = row.feedback_denoised_count;
      }
      if (Array.isArray(row.window_signals)) {
        const parsedWindowSignals = row.window_signals
          .map((item) => {
            if (!item || typeof item !== 'object') {
              return null;
            }
            const signalRow = item as Record<string, unknown>;
            const windowSize =
              typeof signalRow.window_size === 'number'
                ? signalRow.window_size
                : null;
            const signal =
              typeof signalRow.signal === 'number'
                ? signalRow.signal
                : null;
            const count =
              typeof signalRow.count === 'number'
                ? signalRow.count
                : null;
            const weight =
              typeof signalRow.weight === 'number'
                ? signalRow.weight
                : null;
            if (windowSize === null || signal === null || count === null || weight === null) {
              return null;
            }
            return {
              windowSize,
              signal,
              count,
              weight,
            };
          })
          .filter(
            (
              item,
            ): item is { windowSize: number; signal: number; count: number; weight: number } =>
              Boolean(item),
          );
        if (parsedWindowSignals.length > 0) {
          normalized.windowSignals = parsedWindowSignals;
        }
      }
      return normalized;
    })()
    : undefined;

  const memorySummaryRaw = preview.memory_summary;
  const memorySummary = memorySummaryRaw
    ? (() => {
      const normalized: {
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
      } = {
        relationshipHistoryCount:
          typeof memorySummaryRaw.relationship_history_count === 'number'
            ? memorySummaryRaw.relationship_history_count
            : 0,
        feedbackHistoryCount:
          typeof memorySummaryRaw.feedback_history_count === 'number'
            ? memorySummaryRaw.feedback_history_count
            : 0,
      };
      if (typeof memorySummaryRaw.context_id === 'string') {
        normalized.contextId = memorySummaryRaw.context_id;
      }
      if (typeof memorySummaryRaw.history_window === 'number') {
        normalized.historyWindow = memorySummaryRaw.history_window;
      }
      if (typeof memorySummaryRaw.relationship_timeline_displacement_count === 'number') {
        normalized.relationshipTimelineDisplacementCount = memorySummaryRaw.relationship_timeline_displacement_count;
      }
      if (typeof memorySummaryRaw.memory_strategy === 'string') {
        normalized.memoryStrategy = memorySummaryRaw.memory_strategy;
      }
      if (typeof memorySummaryRaw.relationship_merge_deduped_count === 'number') {
        normalized.relationshipMergeDedupedCount = memorySummaryRaw.relationship_merge_deduped_count;
      }
      if (typeof memorySummaryRaw.feedback_merge_deduped_count === 'number') {
        normalized.feedbackMergeDedupedCount = memorySummaryRaw.feedback_merge_deduped_count;
      }
      if (typeof memorySummaryRaw.relationship_collapsed_count === 'number') {
        normalized.relationshipCollapsedCount = memorySummaryRaw.relationship_collapsed_count;
      }
      if (typeof memorySummaryRaw.feedback_collapsed_count === 'number') {
        normalized.feedbackCollapsedCount = memorySummaryRaw.feedback_collapsed_count;
      }
      if (typeof memorySummaryRaw.relationship_clipped_count === 'number') {
        normalized.relationshipClippedCount = memorySummaryRaw.relationship_clipped_count;
      }
      if (typeof memorySummaryRaw.feedback_clipped_count === 'number') {
        normalized.feedbackClippedCount = memorySummaryRaw.feedback_clipped_count;
      }
      if (typeof memorySummaryRaw.relationship_decay_dropped_count === 'number') {
        normalized.relationshipDecayDroppedCount = memorySummaryRaw.relationship_decay_dropped_count;
      }
      if (typeof memorySummaryRaw.feedback_decay_dropped_count === 'number') {
        normalized.feedbackDecayDroppedCount = memorySummaryRaw.feedback_decay_dropped_count;
      }
      if (typeof memorySummaryRaw.candidate_timeline_count === 'number') {
        normalized.candidateTimelineCount = memorySummaryRaw.candidate_timeline_count;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_mode === 'string') {
        normalized.genreAutoLearningMode = memorySummaryRaw.genre_auto_learning_mode;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_applied === 'boolean') {
        normalized.genreAutoLearningApplied = memorySummaryRaw.genre_auto_learning_applied;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_sample_count === 'number') {
        normalized.genreAutoLearningSampleCount = memorySummaryRaw.genre_auto_learning_sample_count;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_denoised_count === 'number') {
        normalized.genreAutoLearningDenoisedCount = memorySummaryRaw.genre_auto_learning_denoised_count;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_feedback_signal === 'number') {
        normalized.genreAutoLearningFeedbackSignal = memorySummaryRaw.genre_auto_learning_feedback_signal;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_bias_count === 'number') {
        normalized.genreAutoLearningBiasCount = memorySummaryRaw.genre_auto_learning_bias_count;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_guard_triggered === 'boolean') {
        normalized.genreAutoLearningGuardTriggered = memorySummaryRaw.genre_auto_learning_guard_triggered;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_guard_reason === 'string') {
        normalized.genreAutoLearningGuardReason = memorySummaryRaw.genre_auto_learning_guard_reason;
      }
      if (typeof memorySummaryRaw.genre_auto_learning_fallback_mode === 'string') {
        normalized.genreAutoLearningFallbackMode = memorySummaryRaw.genre_auto_learning_fallback_mode;
      }
      if (memorySummaryRaw.genre_auto_learning_guard_profile && typeof memorySummaryRaw.genre_auto_learning_guard_profile === 'object') {
        const profile = memorySummaryRaw.genre_auto_learning_guard_profile as Record<string, unknown>;
        const normalizedProfile: {
          minSamples?: number;
          decay?: number;
          biasLimit?: number;
          maxVolatility?: number;
          maxSignalDivergence?: number;
          extremeSignal?: number;
          extremeMinSamples?: number;
          reversalDivergenceMin?: number;
        } = {};
        if (typeof profile.min_samples === 'number') {
          normalizedProfile.minSamples = profile.min_samples;
        }
        if (typeof profile.decay === 'number') {
          normalizedProfile.decay = profile.decay;
        }
        if (typeof profile.bias_limit === 'number') {
          normalizedProfile.biasLimit = profile.bias_limit;
        }
        if (typeof profile.max_volatility === 'number') {
          normalizedProfile.maxVolatility = profile.max_volatility;
        }
        if (typeof profile.max_signal_divergence === 'number') {
          normalizedProfile.maxSignalDivergence = profile.max_signal_divergence;
        }
        if (typeof profile.extreme_signal === 'number') {
          normalizedProfile.extremeSignal = profile.extreme_signal;
        }
        if (typeof profile.extreme_min_samples === 'number') {
          normalizedProfile.extremeMinSamples = profile.extreme_min_samples;
        }
        if (typeof profile.reversal_divergence_min === 'number') {
          normalizedProfile.reversalDivergenceMin = profile.reversal_divergence_min;
        }
        if (Object.keys(normalizedProfile).length > 0) {
          normalized.genreAutoLearningGuardProfile = normalizedProfile;
        }
      }
      return normalized;
    })()
    : undefined;

  const normalized: V4WorkbenchPreview = {
    enabled: preview.enabled,
    candidateCount: preview.candidate_count,
    relationshipDisplacements,
    topCandidates,
  };
  if (preview.fallback_reason !== null && preview.fallback_reason !== undefined) {
    normalized.fallbackReason = preview.fallback_reason;
  }
  if (preview.retention_sort_key !== undefined) {
    normalized.retentionSortKey = preview.retention_sort_key;
  }
  if (memorySummary) {
    normalized.memorySummary = memorySummary;
  }
  if (genreCalibration) {
    normalized.genreCalibration = genreCalibration;
  }
  if (relationshipGraph) {
    normalized.relationshipGraph = relationshipGraph;
  }
  if (relationshipTimeline.length > 0) {
    normalized.relationshipTimeline = relationshipTimeline;
  }
  if (candidateTimeline.length > 0) {
    normalized.candidateTimeline = candidateTimeline;
  }
  if (retentionWriteback) {
    normalized.retentionWriteback = retentionWriteback;
  }
  if (preview.selected_candidate === null) {
    normalized.selectedCandidate = null;
  } else if (selectedCandidate) {
    normalized.selectedCandidate = selectedCandidate;
  }
  if (preview.qc_summary) {
    normalized.qcSummary = preview.qc_summary;
  }
  return normalized;
}

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
    compareBaseline: context.compare_baseline
      ? {
        baselineContextId:
          typeof context.compare_baseline.baseline_context_id === 'string'
            ? context.compare_baseline.baseline_context_id
            : undefined,
        baselineChapterNumber:
          typeof context.compare_baseline.baseline_chapter_number === 'number'
            ? context.compare_baseline.baseline_chapter_number
            : undefined,
        delta:
          context.compare_baseline.delta && typeof context.compare_baseline.delta === 'object'
            ? Object.fromEntries(
              Object.entries(context.compare_baseline.delta).filter(
                (entry): entry is [string, number] => typeof entry[1] === 'number',
              ),
            )
            : {},
      }
      : undefined,
    v4Preview: normalizeV4Preview(context.v4_preview),
    quality: normalizeContextQuality(context),
  }));
}
