import type { TrainingResponse } from '../api';

export function ValueTrendPanel({ current, baseline }: { current: TrainingResponse | null; baseline: typeof import('../data').trainingSnapshot }) {
  const points = current
    ? [
        { label: '基线', value: baseline.averageFeedback },
        { label: '当前反馈', value: current.summary.avg_feedback },
        { label: '当前预测', value: current.summary.avg_predicted },
        { label: '当前目标', value: current.summary.avg_target },
      ]
    : [
        { label: '基线', value: baseline.averageFeedback },
        { label: '当前反馈', value: baseline.averageFeedback },
        { label: '当前预测', value: baseline.averagePredicted },
        { label: '当前目标', value: baseline.averageTarget },
      ];

  return (
    <article className="panel glass" id="value-trend">
      <div className="panel-head">
        <div>
          <p className="label">推荐价值趋势</p>
          <h3>训练与反馈价值轨迹</h3>
        </div>
        <span className="pill success">trend</span>
      </div>

      <div className="feedback-graph">
        {points.map((item) => (
          <div className="bar-col active" key={item.label}>
            <span style={{ height: `${Math.max(20, Math.min(100, item.value * 100))}%` }} />
            <small>{item.label}</small>
          </div>
        ))}
      </div>

      <div className="matrix-list" style={{ marginTop: 16 }}>
        {points.map((item) => (
          <div className="matrix-row" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value.toFixed(3)}</strong>
          </div>
        ))}
      </div>

      <p className="muted" style={{ marginTop: 16 }}>
        该区域用于观察推荐价值在训练、反馈和预览中的整体变化趋势。
      </p>
    </article>
  );
}
