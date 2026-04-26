import { useMemo, useState } from 'react';
import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function WorkbenchTopBar({ controller }: { controller: Controller }) {
  const latestHistory = controller.runHistory.at(-1);
  const exportReady = controller.exportSnapshot();
  const [diagnosticsExpanded, setDiagnosticsExpanded] = useState(false);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'copied-online' | 'failed'>('idle');
  const [diagnosticsSourceFilter, setDiagnosticsSourceFilter] = useState<string>('all');
  const [diagnosticsFailuresOnly, setDiagnosticsFailuresOnly] = useState(false);
  const onlineSourceRaw = controller.sourceDiagnostics?.online_report;
  const onlineSource =
    onlineSourceRaw && typeof onlineSourceRaw === 'object'
      ? (onlineSourceRaw as Record<string, unknown>)
      : null;
  const onlineStatus =
    onlineSource && typeof onlineSource.status === 'string'
      ? onlineSource.status
      : null;
  const onlineErrorType =
    onlineSource && typeof onlineSource.error_type === 'string'
      ? onlineSource.error_type
      : null;
  const onlineHttpStatus =
    onlineSource && typeof onlineSource.http_status === 'number'
      ? onlineSource.http_status
      : null;
  const onlineRequestUrl =
    onlineSource && typeof onlineSource.request_url === 'string'
      ? onlineSource.request_url
      : null;
  const onlineErrorMessage =
    onlineSource && typeof onlineSource.error_message === 'string'
      ? onlineSource.error_message
      : null;
  const onlineAttemptsCount =
    onlineSource && typeof onlineSource.attempts_count === 'number'
      ? onlineSource.attempts_count
      : null;
  const onlineMaxAttempts =
    onlineSource && typeof onlineSource.max_attempts === 'number'
      ? onlineSource.max_attempts
      : null;
  const onlineRetried =
    onlineSource && typeof onlineSource.retried === 'boolean'
      ? onlineSource.retried
      : null;
  const onlineRetryExhausted =
    onlineSource && typeof onlineSource.retry_exhausted === 'boolean'
      ? onlineSource.retry_exhausted
      : null;
  const allSourceDiagnosticsRows = controller.sourceDiagnostics
    ? Object.entries(controller.sourceDiagnostics)
      .map(([sourceKey, sourceValue]) => {
        if (!sourceValue || typeof sourceValue !== 'object') {
          return null;
        }
        const row = sourceValue as Record<string, unknown>;
        const status = typeof row.status === 'string' ? row.status : 'unknown';
        return {
          sourceKey,
          status,
        };
      })
      .filter((item): item is { sourceKey: string; status: string } => Boolean(item))
    : [];
  const diagnosticsSourceOptions = allSourceDiagnosticsRows.map((item) => item.sourceKey);
  const filteredSourceDiagnosticsRows = allSourceDiagnosticsRows.filter((item) => {
    if (diagnosticsSourceFilter !== 'all' && item.sourceKey !== diagnosticsSourceFilter) {
      return false;
    }
    if (diagnosticsFailuresOnly && item.status === 'ok') {
      return false;
    }
    return true;
  });
  const onlineAttemptHistoryRaw = onlineSource && Array.isArray(onlineSource.attempt_history)
    ? onlineSource.attempt_history
      .map((item, index) => {
        if (!item || typeof item !== 'object') {
          return null;
        }
        const row = item as Record<string, unknown>;
        const attempt =
          typeof row.attempt === 'number'
            ? row.attempt
            : index + 1;
        const status =
          typeof row.status === 'string'
            ? row.status
            : 'unknown';
        const httpStatus =
          typeof row.http_status === 'number'
            ? row.http_status
            : null;
        const errorType =
          typeof row.error_type === 'string'
            ? row.error_type
            : null;
        return {
          attempt,
          status,
          httpStatus,
          errorType,
          severity: _attemptSeverity(status),
        };
      })
      .filter(
        (item): item is {
          attempt: number;
          status: string;
          httpStatus: number | null;
          errorType: string | null;
          severity: number;
        } => Boolean(item),
      )
      .sort((left, right) => {
        if (left.severity !== right.severity) {
          return right.severity - left.severity;
        }
        return right.attempt - left.attempt;
      })
    : [];
  const filteredOnlineAttemptHistory =
    diagnosticsSourceFilter === 'all' || diagnosticsSourceFilter === 'online_report'
      ? onlineAttemptHistoryRaw.filter((item) => {
        if (diagnosticsFailuresOnly && item.status === 'ok') {
          return false;
        }
        return true;
      })
      : [];
  const hasDiagnostics = allSourceDiagnosticsRows.length > 0;
  const filteredDiagnosticsPayload = useMemo(() => {
    const sourceDiagnosticsRaw = controller.sourceDiagnostics;
    if (!sourceDiagnosticsRaw || typeof sourceDiagnosticsRaw !== 'object') {
      return {};
    }
    const rows = Object.entries(sourceDiagnosticsRaw)
      .filter(([sourceKey]) => diagnosticsSourceFilter === 'all' || sourceKey === diagnosticsSourceFilter)
      .filter(([_sourceKey, sourceValue]) => {
        if (!diagnosticsFailuresOnly) {
          return true;
        }
        if (!sourceValue || typeof sourceValue !== 'object') {
          return true;
        }
        const row = sourceValue as Record<string, unknown>;
        const status = typeof row.status === 'string' ? row.status : '';
        return status !== 'ok';
      });
    return Object.fromEntries(rows);
  }, [controller.sourceDiagnostics, diagnosticsSourceFilter, diagnosticsFailuresOnly]);
  const diagnosticsJson = useMemo(
    () =>
      JSON.stringify(
        {
          backendSourceMeta: controller.backendSourceMeta,
          sourceDiagnostics: filteredDiagnosticsPayload,
        },
        null,
        2,
      ),
    [controller.backendSourceMeta, filteredDiagnosticsPayload],
  );
  const onlineDiagnosticsJson = useMemo(
    () =>
      JSON.stringify(
        {
          online_report: onlineSource ?? {},
        },
        null,
        2,
      ),
    [onlineSource],
  );
  const handleCopyDiagnostics = async () => {
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error('clipboard-unavailable');
      }
      await navigator.clipboard.writeText(diagnosticsJson);
      setCopyStatus('copied');
    } catch {
      setCopyStatus('failed');
    }
  };
  const handleCopyOnlineDiagnostics = async () => {
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error('clipboard-unavailable');
      }
      await navigator.clipboard.writeText(onlineDiagnosticsJson);
      setCopyStatus('copied-online');
    } catch {
      setCopyStatus('failed');
    }
  };

  return (
    <header className="v2-workbench-topbar panel glass">
      <div>
        <p className="label">Decision Cockpit</p>
        <h1>V2 Workbench</h1>
        <p className="muted">
          {controller.contextSource} / {controller.selectedChapter || 'no chapter'} /{' '}
          {controller.workingState.stage}
        </p>
      </div>
      <div className="review-flag-row" style={{ gap: 8 }}>
        <button
          className="secondary"
          type="button"
          onClick={() => {
            void controller.refreshContexts(false);
          }}
          disabled={controller.isRefreshingContexts}
        >
          Refresh Contexts
        </button>
        <button
          className="secondary"
          type="button"
          onClick={() => {
            void controller.refreshContexts(true);
          }}
          disabled={controller.isRefreshingContexts}
        >
          Refresh Online Only
        </button>
        <button
          className="secondary"
          type="button"
          onClick={() => controller.selectComparisonRun(controller.runHistory.at(-2)?.id ?? '')}
          disabled={controller.runHistory.length < 2}
        >
          Compare Last Run
        </button>
        <button
          className="secondary"
          type="button"
          disabled={!exportReady}
          onClick={() => {
            const snapshot = controller.exportSnapshot();
            if (!snapshot) return;
            navigator.clipboard?.writeText(JSON.stringify(snapshot, null, 2));
          }}
        >
          Export Snapshot
        </button>
        <button className="primary" type="button" onClick={controller.runPreview}>
          Run Preview
        </button>
        {hasDiagnostics ? (
          <>
            <button
              className="secondary"
              type="button"
              onClick={() => setDiagnosticsExpanded((current) => !current)}
            >
              {diagnosticsExpanded ? 'Hide Diagnostics' : 'Show Diagnostics'}
            </button>
            <button
              className="secondary"
              type="button"
              onClick={() => {
                void handleCopyDiagnostics();
              }}
            >
              Copy Diagnostics
            </button>
            {onlineSource ? (
              <button
                className="secondary"
                type="button"
                onClick={() => {
                  void handleCopyOnlineDiagnostics();
                }}
              >
                Copy Online Diagnostics
              </button>
            ) : null}
          </>
        ) : null}
      </div>
      {latestHistory ? (
        <p className="muted workbench-status">
          last run {new Date(latestHistory.timestamp).toLocaleTimeString()}
        </p>
      ) : null}
      <p className="muted workbench-status">
        backend source: {controller.backendSourceMeta.source ?? 'unknown'}
        {' / '}
        {controller.backendSourceMeta.contextContract ?? 'n/a'}
      </p>
      {(controller.backendSourceMeta.runId || controller.backendSourceMeta.resolvedModel) ? (
        <p className="muted workbench-status">
          run: {controller.backendSourceMeta.runId ?? 'n/a'}
          {' / '}
          model: {controller.backendSourceMeta.resolvedModel ?? controller.backendSourceMeta.preferredModel ?? 'n/a'}
        </p>
      ) : null}
      {controller.backendSourceMeta.arbitrationStrategy ? (
        <p className="muted workbench-status">
          arbitration: {controller.backendSourceMeta.arbitrationStrategy}
        </p>
      ) : null}
      {typeof controller.backendSourceMeta.reportSuccessRate === 'number' ? (
        <p className="muted workbench-status">
          success rate: {(controller.backendSourceMeta.reportSuccessRate * 100).toFixed(1)}%
        </p>
      ) : null}
      {controller.backendSourceMeta.reportPath ? (
        <p className="muted workbench-status">
          report path: {controller.backendSourceMeta.reportPath}
        </p>
      ) : null}
      {controller.backendSourceMeta.reportUrl ? (
        <p className="muted workbench-status">
          report url: {controller.backendSourceMeta.reportUrl}
        </p>
      ) : null}
      {controller.backendSourceMeta.fallbackReason ? (
        <p className="muted workbench-status">
          fallback: {controller.backendSourceMeta.fallbackReason}
        </p>
      ) : null}
      {onlineStatus ? (
        <p className="muted workbench-status">
          online source: {onlineStatus}
          {onlineHttpStatus !== null ? ` (${onlineHttpStatus})` : ''}
          {onlineErrorType ? ` / ${onlineErrorType}` : ''}
        </p>
      ) : null}
      {onlineRequestUrl ? (
        <p className="muted workbench-status">online request: {onlineRequestUrl}</p>
      ) : null}
      {onlineErrorMessage ? (
        <p className="muted workbench-status">online error: {onlineErrorMessage}</p>
      ) : null}
      {onlineAttemptsCount !== null ? (
        <p className="muted workbench-status">
          online attempts: {onlineAttemptsCount}
          {onlineMaxAttempts !== null ? `/${onlineMaxAttempts}` : ''}
          {onlineRetried !== null ? ` / retried=${onlineRetried ? 'yes' : 'no'}` : ''}
          {onlineRetryExhausted !== null
            ? ` / exhausted=${onlineRetryExhausted ? 'yes' : 'no'}`
            : ''}
        </p>
      ) : null}
      {hasDiagnostics ? (
        <p className="muted workbench-status">
          diagnostics:{' '}
          {filteredSourceDiagnosticsRows.length
            ? filteredSourceDiagnosticsRows
              .map((item) => `${item.sourceKey}=${item.status}`)
              .join(' | ')
            : 'none'}
        </p>
      ) : null}
      {hasDiagnostics && copyStatus !== 'idle' ? (
        <p className="muted workbench-status">
          diagnostics copy: {copyStatus === 'copied-online' ? 'copied-online' : copyStatus}
        </p>
      ) : null}
      <p className="muted workbench-status">status: {controller.uiStatus}</p>
      {controller.isRefreshingContexts ? (
        <p className="muted workbench-status">refreshing contexts...</p>
      ) : null}
      {controller.contextNotice ? (
        <p className="muted workbench-status">{controller.contextNotice}</p>
      ) : null}
      {controller.error ? (
        <p className="muted workbench-status">error: {controller.error}</p>
      ) : null}
      {hasDiagnostics && diagnosticsExpanded ? (
        <section className="workbench-diagnostics">
          <p className="label">Diagnostics Details</p>
          <div className="workbench-diagnostics-controls">
            <label className="workbench-control-item">
              <span>Source</span>
              <select
                aria-label="Diagnostics Source Filter"
                value={diagnosticsSourceFilter}
                onChange={(event) => setDiagnosticsSourceFilter(event.target.value)}
              >
                <option value="all">all</option>
                {diagnosticsSourceOptions.map((sourceKey) => (
                  <option key={sourceKey} value={sourceKey}>
                    {sourceKey}
                  </option>
                ))}
              </select>
            </label>
            <label className="workbench-control-item workbench-control-item--checkbox">
              <input
                aria-label="Diagnostics Failures Only"
                type="checkbox"
                checked={diagnosticsFailuresOnly}
                onChange={(event) => setDiagnosticsFailuresOnly(event.target.checked)}
              />
              <span>Failures Only</span>
            </label>
          </div>
          {filteredOnlineAttemptHistory.length ? (
            <div className="workbench-attempt-history">
              <p className="label">Online Attempt History</p>
              <table aria-label="Online Attempt History">
                <thead>
                  <tr>
                    <th>Attempt</th>
                    <th>Status</th>
                    <th>HTTP</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOnlineAttemptHistory.map((item) => (
                    <tr
                      key={`${item.attempt}-${item.status}-${item.httpStatus ?? 'none'}`}
                      className={item.status === 'ok' ? undefined : 'workbench-attempt-row--error'}
                    >
                      <td>{item.attempt}</td>
                      <td>{item.status}</td>
                      <td>{item.httpStatus ?? '-'}</td>
                      <td>{item.errorType ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
          <pre aria-label="Diagnostics JSON">{diagnosticsJson}</pre>
        </section>
      ) : null}
    </header>
  );
}


function _attemptSeverity(status: string): number {
  if (status === 'ok') return 0;
  if (status === 'http-error' || status === 'timeout' || status === 'network-error') return 3;
  if (status === 'invalid-json' || status === 'invalid-payload') return 2;
  if (status === 'invalid-report-payload' || status === 'empty-contexts') return 1;
  return 1;
}
