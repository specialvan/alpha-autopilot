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
            <div className="review-flag-row">
              <span className={`micro-pill ${item.riskLevel === 'high' ? 'danger' : ''}`}>
                风险 {item.riskLevel ?? 'unknown'}
              </span>
            </div>
            {item.prerequisites?.length ? (
              <>
                <p className="label" style={{ marginTop: '14px' }}>前置条件</p>
                <ul className="note-list">
                  {item.prerequisites.map((prerequisite) => <li key={prerequisite}>{prerequisite}</li>)}
                </ul>
              </>
            ) : null}
            {item.nextStep ? (
              <>
                <p className="label" style={{ marginTop: '14px' }}>下一步建议</p>
                <p>{item.nextStep}</p>
              </>
            ) : null}
          </div>
        ))}
      </div>
    </article>
  );
}
