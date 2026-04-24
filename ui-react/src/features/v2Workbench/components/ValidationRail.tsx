import { RunHistoryPanel } from './RunHistoryPanel';
import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function ValidationRail({ controller }: { controller: Controller }) {
  const decision = controller.currentPreview?.decision;
  const validation = controller.currentPreview?.validation;
  const acceptedActions = Array.isArray(decision?.accepted_actions)
    ? decision.accepted_actions
    : (Array.isArray(validation?.accepted_actions) ? validation.accepted_actions : []);
  const blockedActions = Array.isArray(decision?.blocked_actions)
    ? decision.blocked_actions
    : (Array.isArray(validation?.blocked_actions) ? validation.blocked_actions : []);
  const prerequisiteMissingActions = Array.isArray(decision?.prerequisite_missing_actions)
    ? decision.prerequisite_missing_actions
    : [];
  const caseId = decision?.validation_case_id || validation?.case_id || 'unknown';
  const ruleChecks = Array.isArray(controller.currentPreview?.rule_checks)
    ? controller.currentPreview.rule_checks
    : [];
  const topAction =
    decision?.selected_action
    ?? decision?.top_action
    ?? decision?.action
    ?? validation?.top_action
    ?? controller.currentPreview?.evaluation_summary.top_action
    ?? 'pending';

  return (
    <aside className="panel glass workbench-rail">
      <div className="panel-head">
        <div>
          <p className="label">Validation Rail</p>
          <h2>Validation Rail</h2>
        </div>
        <span className="pill success">{topAction}</span>
      </div>

      <div className="field-card">
        <span className="label">Rule Summary</span>
        {ruleChecks.length ? (
          ruleChecks.map((item) => (
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
              <strong>{caseId}</strong>
            </div>
            <div className="matrix-row">
              <span>Accepted</span>
              <strong>{acceptedActions.join(', ') || 'none'}</strong>
            </div>
            <div className="matrix-row">
              <span>Blocked</span>
              <strong>{blockedActions.join(', ') || 'none'}</strong>
            </div>
            <div className="matrix-row">
              <span>Prerequisite Missing</span>
              <strong>{prerequisiteMissingActions.join(', ') || 'none'}</strong>
            </div>
            {decision?.quality_hint ? (
              <div className="matrix-row">
                <span>Quality Hint</span>
                <strong>{decision.quality_hint}</strong>
              </div>
            ) : null}
            {decision?.rule_status_summary ? (
              <div className="matrix-row">
                <span>Rule Status</span>
                <strong>
                  legal {decision.rule_status_summary.legal_count}
                  {' / '}blocked {decision.rule_status_summary.blocked_count}
                  {' / '}missing {decision.rule_status_summary.prerequisite_missing_count ?? 0}
                </strong>
              </div>
            ) : null}
            {decision?.constraint_hint ? (
              <div className="matrix-row">
                <span>Constraint Hint</span>
                <strong>{decision.constraint_hint}</strong>
              </div>
            ) : null}
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
