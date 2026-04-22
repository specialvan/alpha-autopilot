import { useEffect, useMemo, useState } from 'react';
import {
  fetchWorkbenchContextsV2,
  fetchRecommendationPreviewV2,
  type NarrativeV2PreviewResponse,
  type NarrativeV2StoryState,
} from '../../api';
import { buildNarrativeV2PreviewRequest, clampNarrativeV2Value } from '../../v2Preview';
import { computeStateDiff, listChapterMappedContexts, resolveBaseState } from './contextMapping';
import { normalizeWorkbenchContexts } from './backendContexts';
import { appendRunEntry, buildComparisonDelta, buildSnapshotPayload } from './session';
import type { ChapterMappedContext, V2ContextSource, WorkbenchRunEntry } from './types';

type UiStatus = 'loading_context' | 'ready' | 'dirty' | 'running' | 'error';

type NumericStateField = Extract<
  keyof NarrativeV2StoryState,
  | 'mainline_progress'
  | 'sideplot_progress'
  | 'conflict_intensity'
  | 'emotional_temperature'
  | 'pacing_speed'
  | 'foreshadowing_load'
  | 'payoff_pressure'
>;

export function useV2WorkbenchController() {
  const [contexts, setContexts] = useState<ChapterMappedContext[]>(listChapterMappedContexts());
  const [contextSource, setContextSource] = useState<V2ContextSource>('mapped_chapter');
  const [selectedChapter, setSelectedChapter] = useState<string>(listChapterMappedContexts()[0]?.id ?? '');
  const [overrides, setOverrides] = useState<Partial<NarrativeV2StoryState>>({});
  const [currentPreview, setCurrentPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [comparisonPreview, setComparisonPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [runHistory, setRunHistory] = useState<WorkbenchRunEntry[]>([]);
  const [uiStatus, setUiStatus] = useState<UiStatus>('loading_context');
  const [error, setError] = useState<string | null>(null);

  const baseState = useMemo(
    () => resolveBaseState(contextSource, selectedChapter),
    [contextSource, selectedChapter],
  );
  const workingState = useMemo(
    () => ({ ...baseState, ...overrides }),
    [baseState, overrides],
  );
  const stateDiff = useMemo(
    () => computeStateDiff(baseState, workingState),
    [baseState, workingState],
  );
  const comparisonDelta = useMemo(
    () =>
      currentPreview && comparisonPreview
        ? buildComparisonDelta(comparisonPreview, currentPreview)
        : null,
    [comparisonPreview, currentPreview],
  );

  const runPreview = async () => {
    setUiStatus('running');
    try {
      const preview = await fetchRecommendationPreviewV2(
        buildNarrativeV2PreviewRequest(workingState),
      );
      setComparisonPreview(currentPreview);
      setCurrentPreview(preview);
      setRunHistory((history) =>
        appendRunEntry(history, {
          source: contextSource,
          label: selectedChapter || contextSource,
          submittedState: workingState,
          preview,
        }),
      );
      setError(null);
      setUiStatus('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'v2 preview failed');
      setUiStatus('error');
    }
  };

  useEffect(() => {
    void runPreview();
  }, [contextSource, selectedChapter]);

  useEffect(() => {
    let cancelled = false;
    void fetchWorkbenchContextsV2()
      .then((payload) => {
        if (cancelled) return;
        const normalized = normalizeWorkbenchContexts(payload);
        if (!normalized.length) return;
        setContexts(normalized);
        setSelectedChapter((current) =>
          normalized.some((item) => item.id === current) ? current : normalized[0].id,
        );
      })
      .catch(() => {
        if (!cancelled) setContexts(listChapterMappedContexts());
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const setNumericOverride = (field: NumericStateField, value: number) => {
    setOverrides((current) => ({
      ...current,
      [field]: clampNarrativeV2Value(value),
    }));
    setUiStatus('dirty');
  };

  const selectComparisonRun = (id: string) => {
    const selected = runHistory.find((entry) => entry.id === id);
    setComparisonPreview(selected?.preview ?? null);
  };

  const exportSnapshot = () => {
    if (!currentPreview) return null;
    return buildSnapshotPayload({
      source: contextSource,
      selectedChapter: selectedChapter || null,
      baseState,
      overrides,
      workingState,
      currentPreview,
      comparisonPreview,
    });
  };

  return {
    contexts,
    contextSource,
    selectedChapter,
    baseState,
    workingState,
    stateDiff,
    currentPreview,
    comparisonPreview,
    comparisonDelta,
    runHistory,
    uiStatus,
    error,
    setContextSource,
    setSelectedChapter,
    setNumericOverride,
    runPreview,
    selectComparisonRun,
    exportSnapshot,
  };
}
