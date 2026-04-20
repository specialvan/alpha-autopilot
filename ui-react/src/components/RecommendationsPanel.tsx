import type { Recommendation } from '../api';

export function RecommendationsPanel({ recommendations }: { recommendations: Recommendation[] }) {
  return (
    <article className="panel glass" id="recommendations">
      <div className="panel-head">
        <div>
          <p className="label">推荐结果</p>
          <h3>候选章节推进排序</h3>
        </div>
        <span className="pill success">Top 3</span>
      </div>

      <div className="recommendation-list">
        {recommendations.map((item) => (
          <div className={`recommendation-card ${item.top ? 'top' : ''}`} key={item.action}>
            <div className="rec-head">
              <strong>{item.action}</strong>
              <span>{item.score}</span>
            </div>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </article>
  );
}
