import type { TrainingResponse } from '../api';

export function VersionComparePanel({ current, baseline }: { current: TrainingResponse | null; baseline: typeof import('../data').trainingSnapshot }) {
  return (
    <article className="panel glass" id="version-compare">
      <div className="panel-head">
        <div>
          <p className="label">版本对比</p>
          <h3>训练与价值变化</h3>
        </div>
        <span className="pill success">compare</span>
      </div>

      <div className="content-grid two" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))' }}>
        <section className="recommendation-card">
          <p className="label">基线版本</p>
          <div className="matrix-list">
            <div className="matrix-row"><span>版本</span><strong>{baseline.version}</strong></div>
            <div className="matrix-row"><span>样本数</span><strong>{baseline.sampleCount}</strong></div>
            <div className="matrix-row"><span>平均预测分</span><strong>{baseline.averagePredicted.toFixed(3)}</strong></div>
            <div className="matrix-row"><span>平均目标分</span><strong>{baseline.averageTarget.toFixed(3)}</strong></div>
            <div className="matrix-row"><span>平均反馈分</span><strong>{baseline.averageFeedback.toFixed(3)}</strong></div>
          </div>
        </section>

        <section className="recommendation-card top">
          <p className="label">当前版本</p>
          {current ? (
            <div className="matrix-list">
              <div className="matrix-row"><span>版本</span><strong>{current.version}</strong></div>
              <div className="matrix-row"><span>样本数</span><strong>{current.sample_count}</strong></div>
              <div className="matrix-row"><span>平均预测分</span><strong>{current.summary.avg_predicted.toFixed(3)}</strong></div>
              <div className="matrix-row"><span>平均目标分</span><strong>{current.summary.avg_target.toFixed(3)}</strong></div>
              <div className="matrix-row"><span>平均反馈分</span><strong>{current.summary.avg_feedback.toFixed(3)}</strong></div>
              <div className="matrix-row"><span>RMSE</span><strong>{current.summary.rmse.toFixed(3)}</strong></div>
            </div>
          ) : (
            <p className="muted">尚未生成新的训练版本。</p>
          )}
        </section>
      </div>

      <div className="note-list" style={{ marginTop: 16 }}>
        <div className="recommendation-card">
          <p className="label">变化提示</p>
          <p>当前对比区用于观察训练版本是否在稳定度、准确度和价值摘要上优于基线版本。</p>
        </div>
      </div>
    </article>
  );
}
