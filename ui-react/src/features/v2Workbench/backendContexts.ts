import type {
  NarrativeV2CheckpointSummary,
  NarrativeV2ContextCheckpoint,
  NarrativeV2WorkbenchContext,
  NarrativeV2WorkbenchContextsResponse,
} from '../../api';
import type {
  ChapterMappedContext,
  ContextCheckpoint,
  ContextCheckpointSummary,
  ContextQualityMetadata,
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
    quality: normalizeContextQuality(context),
  }));
}
