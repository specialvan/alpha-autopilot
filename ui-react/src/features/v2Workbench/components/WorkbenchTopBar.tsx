import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function WorkbenchTopBar({ controller }: { controller: Controller }) {
  const latestHistory = controller.runHistory.at(-1);
  const exportReady = controller.exportSnapshot();

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
      </div>
      {latestHistory ? (
        <p className="muted workbench-status">
          last run {new Date(latestHistory.timestamp).toLocaleTimeString()}
        </p>
      ) : null}
      <p className="muted workbench-status">status: {controller.uiStatus}</p>
      {controller.contextNotice ? (
        <p className="muted workbench-status">{controller.contextNotice}</p>
      ) : null}
      {controller.error ? (
        <p className="muted workbench-status">error: {controller.error}</p>
      ) : null}
    </header>
  );
}
