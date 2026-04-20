import type { OverviewResponse } from '../api';

export function MetricsGrid({ overview }: { overview: OverviewResponse }) {
  return (
    <section className="metrics-grid">
      <article className="metric-card glass">
        <p className="label">训练样本</p>
        <strong>{overview.sampleCount}</strong>
        <span className="delta up">+4 本周新增</span>
      </article>
      <article className="metric-card glass">
        <p className="label">版本快照</p>
        <strong>{overview.versionCount}</strong>
        <span className="delta up">持续可回滚</span>
      </article>
      <article className="metric-card glass">
        <p className="label">反馈命中率</p>
        <strong>{overview.hitRate}</strong>
        <span className="delta up">较上轮提升 8%</span>
      </article>
      <article className="metric-card glass">
        <p className="label">AI 风险</p>
        <strong>{overview.riskScore}</strong>
        <span className="delta down">低于警戒线</span>
      </article>
    </section>
  );
}
