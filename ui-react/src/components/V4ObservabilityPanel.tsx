import type { V4Observability } from '../api';

function percentage(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function V4ObservabilityPanel({ snapshot }: { snapshot?: V4Observability }) {
  return (
    <article className="panel glass" aria-label="V4 Observability Panel">
      <div className="panel-head">
        <div>
          <p className="label">V4 Observability</p>
          <h3>Memory And Genre Learning</h3>
        </div>
        <span className="pill">v4-memory</span>
      </div>

      {snapshot?.enabled ? (
        <>
          <div className="matrix-row">
            <span>Contexts</span>
            <strong>{snapshot.activeContexts}</strong>
          </div>
          <div className="matrix-row">
            <span>Memory Rows</span>
            <strong>
              rel {snapshot.relationshipRows}
              {' / '}fb {snapshot.feedbackRows}
            </strong>
          </div>
          <div className="matrix-row">
            <span>Feedback Signal</span>
            <strong>{snapshot.feedbackSignal.toFixed(2)}</strong>
          </div>
          <div className="matrix-row">
            <span>Accept Rate</span>
            <strong>{percentage(snapshot.acceptRate)}</strong>
          </div>
          <div className="matrix-row">
            <span>Avg Tension</span>
            <strong>{snapshot.averageTension.toFixed(2)}</strong>
          </div>
          <div className="matrix-row">
            <span>Genres Tracked</span>
            <strong>
              {snapshot.genresTracked}
              {' / ready '}
              {snapshot.autoLearningReadyGenres}
            </strong>
          </div>
          {(snapshot.alertCount ?? 0) > 0 ? (
            <div className="matrix-row">
              <span>Alerts</span>
              <strong>
                {snapshot.alertCount}
                {' / critical '}
                {snapshot.criticalAlertCount ?? 0}
              </strong>
            </div>
          ) : null}
          {snapshot.alertRouting ? (
            <div className="matrix-row">
              <span>Alert Routing</span>
              <strong>
                {snapshot.alertRouting.routed ? 'routed' : snapshot.alertRouting.reason}
              </strong>
            </div>
          ) : null}
          {snapshot.alerts?.slice(0, 3).map((item) => (
            <div className="matrix-row" key={item.code}>
              <span>
                {item.severity}
                {' / '}
                {item.code}
              </span>
              <strong>{item.message}</strong>
            </div>
          ))}
          {snapshot.topGenres.slice(0, 3).map((item) => (
            <div className="matrix-row" key={item.genre}>
              <span>
                {item.genre}
                {' / '}
                {item.sampleCount}
              </span>
              <strong>
                {item.feedbackSignal.toFixed(2)}
                {' / '}
                {percentage(item.acceptRate)}
              </strong>
            </div>
          ))}
          {snapshot.trend?.slice(0, 3).map((item) => (
            <div className="matrix-row" key={`trend-${item.windowSize}`}>
              <span>
                Trend {item.windowSize}
                {' / '}
                {item.sampleCount}
              </span>
              <strong>
                {item.feedbackSignal.toFixed(2)}
                {' / '}
                {percentage(item.acceptRate)}
              </strong>
            </div>
          ))}
          {snapshot.lastUpdated ? (
            <p className="muted">Last updated: {snapshot.lastUpdated}</p>
          ) : null}
        </>
      ) : (
        <p className="muted">No persisted V4 memory metrics yet.</p>
      )}
    </article>
  );
}
