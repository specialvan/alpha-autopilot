import { useEffect, useMemo, useRef, useState } from 'react';
import {
  fetchNarrativeV4WorkbenchPreview,
  refreshWorkbenchContextsV2,
  fetchWorkbenchContextsV2,
  fetchRecommendationPreviewV2,
  type NarrativeV2PreviewResponse,
  type NarrativeV2StoryState,
  type NarrativeV2WorkbenchContextsResponse,
} from '../../api';
import { buildNarrativeV2PreviewRequest, clampNarrativeV2Value } from '../../v2Preview';
import { computeStateDiff, listChapterMappedContexts, resolveBaseState } from './contextMapping';
import { normalizeV4Preview, normalizeWorkbenchContexts } from './backendContexts';
import { appendRunEntry, buildComparisonDelta, buildSnapshotPayload } from './session';
import type { ChapterMappedContext, V2ContextSource, V4WorkbenchPreview, WorkbenchRunEntry } from './types';

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
  const fallbackContexts = listChapterMappedContexts();
  const [contexts, setContexts] = useState<ChapterMappedContext[]>(fallbackContexts);
  const [contextSource, setContextSource] = useState<V2ContextSource>('mapped_chapter');
  const [selectedChapter, setSelectedChapter] = useState<string>(fallbackContexts[0]?.id ?? '');
  const [overrides, setOverrides] = useState<Partial<NarrativeV2StoryState>>({});
  const [currentPreview, setCurrentPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [currentV4Preview, setCurrentV4Preview] = useState<V4WorkbenchPreview | null>(null);
  const [comparisonPreview, setComparisonPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [runHistory, setRunHistory] = useState<WorkbenchRunEntry[]>([]);
  const [uiStatus, setUiStatus] = useState<UiStatus>('loading_context');
  const [error, setError] = useState<string | null>(null);
  const [contextNotice, setContextNotice] = useState<string | null>(null);
  const [isRefreshingContexts, setIsRefreshingContexts] = useState(false);
  const [backendSourceMeta, setBackendSourceMeta] = useState<{
    source?: string;
    contextContract?: string;
    fallbackReason?: string;
    reportPath?: string;
    reportUrl?: string;
    runId?: string;
    manifestPath?: string;
    preferredModel?: string;
    resolvedModel?: string;
    reportSuccessRate?: number;
    reportTimestamp?: string;
    arbitrationStrategy?: string;
  }>({});
  const [sourceDiagnostics, setSourceDiagnostics] = useState<Record<string, unknown> | null>(null);
  const previewRequestTokenRef = useRef(0);

  const baseState = useMemo(
    () => resolveBaseState(contextSource, contexts, selectedChapter),
    [contextSource, contexts, selectedChapter],
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
    const requestToken = previewRequestTokenRef.current + 1;
    previewRequestTokenRef.current = requestToken;
    setUiStatus('running');
    try {
      const [preview, v4PreviewRaw] = await Promise.all([
        fetchRecommendationPreviewV2(
          buildNarrativeV2PreviewRequest(workingState),
        ),
        fetchNarrativeV4WorkbenchPreview({
          id: selectedChapter || contextSource,
          state: workingState,
        }).catch(() => null),
      ]);
      if (previewRequestTokenRef.current != requestToken) {
        return;
      }
      setCurrentPreview((previous) => {
        setComparisonPreview(previous);
        return preview;
      });
      setCurrentV4Preview(normalizeV4Preview(v4PreviewRaw) ?? null);
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
      if (previewRequestTokenRef.current != requestToken) {
        return;
      }
      setError(err instanceof Error ? err.message : 'v2 preview failed');
      setUiStatus('error');
    }
  };

  useEffect(() => {
    void runPreview();
  }, [baseState, contextSource, selectedChapter]);

  useEffect(() => {
    let cancelled = false;
    void fetchWorkbenchContextsV2()
      .then((payload) => {
        if (cancelled) return;
        applyWorkbenchContextsPayload(payload, {
          fallbackToMappedOnEmpty: true,
        });
      })
      .catch((err) => {
        if (cancelled) return;
        setContexts(listChapterMappedContexts());
        setBackendSourceMeta({});
        setSourceDiagnostics(null);
        setContextNotice(
          err instanceof Error
            ? `Failed to load backend contexts (${err.message}). Using mapped chapter fallback.`
            : 'Failed to load backend contexts. Using mapped chapter fallback.',
        );
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const applyWorkbenchContextsPayload = (
    payload: NarrativeV2WorkbenchContextsResponse,
    options: { fallbackToMappedOnEmpty: boolean },
  ) => {
    setBackendSourceMeta({
      source: payload.source,
      contextContract: payload.context_contract,
      fallbackReason: payload.fallback_reason,
      reportPath: payload.report_path,
      reportUrl: payload.report_url,
      runId: payload.run_id,
      manifestPath: payload.manifest_path,
      preferredModel: payload.preferred_model,
      resolvedModel: payload.resolved_model,
      reportSuccessRate: payload.report_success_rate,
      reportTimestamp: payload.report_timestamp,
      arbitrationStrategy: payload.arbitration_strategy,
    });
    setSourceDiagnostics(payload.source_diagnostics ?? null);

    const normalized = normalizeWorkbenchContexts(payload);
    if (!normalized.length) {
      if (options.fallbackToMappedOnEmpty) {
        const fallback = listChapterMappedContexts();
        setContexts(fallback);
        setSelectedChapter((current) =>
          fallback.some((item) => item.id === current) ? current : fallback[0]?.id ?? '',
        );
      }
      if (payload.fallback_reason) {
        setContextNotice(`Context source fallback: ${payload.fallback_reason}.`);
      } else {
        setContextNotice(
          options.fallbackToMappedOnEmpty
            ? 'No backend contexts returned. Using mapped chapter fallback.'
            : 'No backend contexts returned. Keeping current contexts.',
        );
      }
      return;
    }

    setContexts(normalized);
    setSelectedChapter((current) =>
      normalized.some((item) => item.id === current) ? current : normalized[0].id,
    );
    if (payload.fallback_reason) {
      setContextNotice(`Context source fallback: ${payload.fallback_reason}.`);
    } else {
      setContextNotice(null);
    }
  };

  const refreshContexts = async (onlineOnly = false) => {
    setIsRefreshingContexts(true);
    try {
      const payload = await refreshWorkbenchContextsV2({ onlineOnly });
      applyWorkbenchContextsPayload(payload, {
        fallbackToMappedOnEmpty: !onlineOnly,
      });
    } catch (err) {
      setContextNotice(
        err instanceof Error
          ? `Failed to refresh backend contexts (${err.message}).`
          : 'Failed to refresh backend contexts.',
      );
    } finally {
      setIsRefreshingContexts(false);
    }
  };

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
    currentV4Preview,
    comparisonPreview,
    comparisonDelta,
    runHistory,
    uiStatus,
    error,
    contextNotice,
    backendSourceMeta,
    sourceDiagnostics,
    isRefreshingContexts,
    setContextSource,
    setSelectedChapter,
    setNumericOverride,
    runPreview,
    refreshContexts,
    selectComparisonRun,
    exportSnapshot,
  };
}
