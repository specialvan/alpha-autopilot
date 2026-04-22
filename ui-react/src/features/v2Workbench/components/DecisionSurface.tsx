import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

export function DecisionSurface({ controller }: { controller: Controller }) {
  const topRecommendation = controller.currentPreview?.recommendations[0] ?? null;

  return (
    <section className="panel glass workbench-center">
      <div className="panel-head">
        <div>
          <p className="label">Decision Surface</p>
          <h2>Decision Surface</h2>
        </div>
        {controller.comparisonDelta ? (
          <span className="pill">
            Δ {controller.comparisonDelta.topScoreDelta.toFixed(4)}
          </span>
        ) : null}
      </div>

      <article className="recommendation-card top">
        <div className="rec-head">
          <strong>{topRecommendation?.action.action ?? 'pending'}</strong>
          <span>{topRecommendation ? topRecommendation.score.toFixed(4) : '0.0000'}</span>
        </div>
        <p>{topRecommendation?.action.explanation ?? 'Run a preview to inspect the best action.'}</p>
      </article>

      <div className="workbench-stack" style={{ marginTop: 16 }}>
        {controller.currentPreview?.recommendations.map((item) => (
          <div className="recommendation-card" key={`${item.action.action}-${item.score}`}>
            <div className="rec-head">
              <strong>{item.action.action}</strong>
              <span>{item.score.toFixed(4)}</span>
            </div>
            <div className="detail-grid">
              {Object.entries(item.details).map(([key, value]) => (
                <div className="matrix-row" key={key}>
                  <span>{key}</span>
                  <strong>{value.toFixed(2)}</strong>
                </div>
              ))}
            </div>
          </div>
        )) ?? <p className="muted">No recommendations yet.</p>}
      </div>
    </section>
  );
}
