import { RunHistoryPanel } from './RunHistoryPanel';
import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function ValidationRail({ controller }: { controller: Controller }) {
  return (
    <aside className="panel glass workbench-rail">
      <div className="panel-head">
        <div>
          <p className="label">Validation Rail</p>
          <h2>Validation Rail</h2>
        </div>
        <span className="pill success">{controller.currentPreview?.validation.top_action ?? 'pending'}</span>
      </div>

      <div className="field-card">
        <span className="label">Rule Summary</span>
        {controller.currentPreview?.rule_checks.length ? (
          controller.currentPreview.rule_checks.map((item) => (
            <div className="matrix-row" key={`${item.action}-${item.status}`}>
              <span>{item.action}</span>
              <strong>{item.status}</strong>
            </div>
          ))
        ) : (
          <p className="muted">No rule checks yet.</p>
        )}
      </div>

      <div className="field-card">
        <span className="label">Validation Record</span>
        {controller.currentPreview ? (
          <>
            <div className="matrix-row">
              <span>Case</span>
              <strong>{controller.currentPreview.validation.case_id}</strong>
            </div>
            <div className="matrix-row">
              <span>Accepted</span>
              <strong>{controller.currentPreview.validation.accepted_actions.join(', ') || 'none'}</strong>
            </div>
            <div className="matrix-row">
              <span>Blocked</span>
              <strong>{controller.currentPreview.validation.blocked_actions.join(', ') || 'none'}</strong>
            </div>
          </>
        ) : (
          <p className="muted">No validation record yet.</p>
        )}
      </div>

      <div className="field-card">
        <span className="label">Run History</span>
        <RunHistoryPanel controller={controller} />
      </div>
    </aside>
  );
}
