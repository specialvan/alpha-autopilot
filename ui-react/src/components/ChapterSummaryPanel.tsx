import type { ChapterSummary } from '../api';

export function ChapterSummaryPanel({ summary }: { summary: ChapterSummary }) {
  return (
    <article className="panel glass" id="summary">
      <div className="panel-head">
        <div>
          <p className="label">章节建议摘要</p>
          <h3>{summary.title}</h3>
        </div>
        <span className="pill">draft</span>
      </div>

      <div className="note-list" style={{ marginTop: 0 }}>
        <div className="recommendation-card top">
          <p className="label">钩子</p>
          <p>{summary.hook}</p>
        </div>
        <div className="recommendation-card">
          <p className="label">冲突</p>
          <p>{summary.conflict}</p>
        </div>
        <div className="recommendation-card">
          <p className="label">转折</p>
          <p>{summary.turn}</p>
        </div>
        <div className="recommendation-card">
          <p className="label">回报</p>
          <p>{summary.payoff}</p>
        </div>
      </div>
    </article>
  );
}
