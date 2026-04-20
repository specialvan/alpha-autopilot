import type { TuningWeight } from '../api';

export function TuningPanel({ weights }: { weights: TuningWeight[] }) {
  return (
    <article className="panel glass" id="tuning">
      <div className="panel-head">
        <div>
          <p className="label">推荐生成调参</p>
          <h3>爽点、节奏、打斗等量化细节</h3>
        </div>
        <span className="pill success">editable</span>
      </div>

      <div className="signal-stack">
        {weights.map((item) => (
          <div className="signal" key={item.label}>
            <div className="signal-row">
              <span>{item.label}</span>
              <strong>{item.direction === 'up' ? '+' : '-'}{item.value.toFixed(2)}</strong>
            </div>
            <div className="bar">
              <span style={{ width: `${Math.round(item.value * 100)}%` }} />
            </div>
            <p className="muted" style={{ marginTop: 8 }}>{item.description}</p>
          </div>
        ))}
      </div>

      <div className="review-flag-row" style={{ marginTop: 16 }}>
        <span className="micro-pill">可强化</span>
        <span className="micro-pill">可削弱</span>
        <span className="micro-pill">可对比上一版</span>
      </div>
    </article>
  );
}
