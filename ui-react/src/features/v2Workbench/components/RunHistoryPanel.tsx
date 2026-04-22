import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function RunHistoryPanel({ controller }: { controller: Controller }) {
  return (
    <div className="workbench-stack">
      {controller.runHistory.length ? (
        controller.runHistory.slice(-5).reverse().map((entry) => (
          <button
            className="timeline-button"
            key={entry.id}
            type="button"
            onClick={() => controller.selectComparisonRun(entry.id)}
          >
            <div className="signal-row">
              <span>{entry.label}</span>
              <strong>{entry.preview.evaluation_summary.top_action}</strong>
            </div>
            <p className="muted">
              {new Date(entry.timestamp).toLocaleTimeString()} /{' '}
              {entry.preview.evaluation_summary.top_score.toFixed(4)}
            </p>
          </button>
        ))
      ) : (
        <p className="muted">No prior runs yet.</p>
      )}
    </div>
  );
}
