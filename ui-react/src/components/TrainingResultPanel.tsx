import type { TrainingResponse } from '../api';

export function TrainingResultPanel({ result }: { result: TrainingResponse | null }) {
  return (
    <article className="panel glass" id="training-result">
      <div className="panel-head">
        <div>
          <p className="label">训练结果展示</p>
          <h3>版本、样本与权重变化</h3>
        </div>
        <span className="pill success">latest</span>
      </div>

      {result ? (
        <>
          <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))' }}>
            <article className="metric-card glass">
              <p className="label">版本号</p>
              <strong>{result.version}</strong>
            </article>
            <article className="metric-card glass">
              <p className="label">样本数</p>
              <strong>{result.sample_count}</strong>
            </article>
            <article className="metric-card glass">
              <p className="label">偏置</p>
              <strong>{result.bias.toFixed(3)}</strong>
            </article>
          </div>

          <div className="matrix-list" style={{ marginTop: 16 }}>
            <div className="matrix-row"><span>平均预测分</span><strong>{result.summary.average_predicted.toFixed(3)}</strong></div>
            <div className="matrix-row"><span>平均目标分</span><strong>{result.summary.average_target.toFixed(3)}</strong></div>
            <div className="matrix-row"><span>平均反馈分</span><strong>{result.summary.average_feedback.toFixed(3)}</strong></div>
          </div>

          <p className="label" style={{ marginTop: 16 }}>权重摘要</p>
          <div className="matrix-list">
            {Object.entries(result.weights).map(([name, value]) => (
              <div className="matrix-row" key={name}>
                <span>{name}</span>
                <strong>{value.toFixed(3)}</strong>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="muted">尚未触发训练，训练结果会显示在这里。</p>
      )}
    </article>
  );
}
