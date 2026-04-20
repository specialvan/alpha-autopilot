import type { TuningWeight } from '../api';

type TuningPanelProps = {
  weights: TuningWeight[];
  onAdjust: (label: string, delta: number) => void;
  onPreview: () => void;
};

export function TuningPanel({ weights, onAdjust, onPreview }: TuningPanelProps) {
  return (
    <article className="panel glass" id="tuning">
      <div className="panel-head">
        <div>
          <p className="label">推荐生成调参</p>
          <h3>爽点、节奏、打斗等量化细节</h3>
        </div>
        <span className="pill success">interactive</span>
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
            <div className="review-flag-row" style={{ marginTop: 12 }}>
              <button className="secondary micro-action" type="button" onClick={() => onAdjust(item.label, -0.05)}>削弱</button>
              <button className="primary micro-action" type="button" onClick={() => onAdjust(item.label, 0.05)}>强化</button>
            </div>
          </div>
        ))}
      </div>

      <div className="review-flag-row" style={{ marginTop: 16 }}>
        <span className="micro-pill">可强化</span>
        <span className="micro-pill">可削弱</span>
        <span className="micro-pill">可对比上一版</span>
        <button className="secondary" type="button" onClick={onPreview}>刷新推荐预览</button>
      </div>
    </article>
  );
}
