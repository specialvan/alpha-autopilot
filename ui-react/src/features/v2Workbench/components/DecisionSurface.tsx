import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;
type RecommendationEntry = NonNullable<Controller['currentPreview']>['recommendations'][number];
type DecisionEntry = {
  key: string;
  action: string;
  score: number;
  explanation: string;
  details: Record<string, number>;
};

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function normalizeDetails(details: Record<string, unknown> | undefined): Record<string, number> {
  if (!details) return {};
  const normalized: Record<string, number> = {};
  for (const [key, value] of Object.entries(details)) {
    if (typeof value === 'number' && Number.isFinite(value)) {
      normalized[key] = value;
    }
  }
  return normalized;
}

function buildRecommendationIndex(controller: Controller): Map<string, RecommendationEntry> {
  const index = new Map<string, RecommendationEntry>();
  const recommendations = controller.currentPreview?.recommendations ?? [];
  for (const recommendation of recommendations) {
    if (!index.has(recommendation.action.action)) {
      index.set(recommendation.action.action, recommendation);
    }
  }
  return index;
}

function buildLegacyDecisionEntries(controller: Controller): DecisionEntry[] {
  return controller.currentPreview?.recommendations.map((item) => ({
    key: `${item.action.action}-${item.score}`,
    action: item.action.action,
    score: asNumber(item.score),
    explanation: item.action.explanation,
    details: normalizeDetails(item.details),
  })) ?? [];
}

function buildDecisionEntries(controller: Controller): DecisionEntry[] {
  const decision = controller.currentPreview?.decision;
  const recommendationIndex = buildRecommendationIndex(controller);
  if (!decision) {
    return buildLegacyDecisionEntries(controller);
  }

  if (decision.candidates?.length) {
    return decision.candidates.map((candidate) => ({
      key: `${candidate.action}-${candidate.score}`,
      action: candidate.action,
      score: asNumber(candidate.score),
      explanation:
        candidate.explanation
        ?? recommendationIndex.get(candidate.action)?.action.explanation
        ?? 'No explanation provided.',
      details: {
        ...normalizeDetails(recommendationIndex.get(candidate.action)?.details),
        ...normalizeDetails(candidate.details),
      },
    }));
  }

  const action = decision.selected_action ?? decision.top_action ?? decision.action;
  const score = asNumber(decision.selected_score ?? decision.top_score ?? decision.score, 0);
  if (!action) {
    return buildLegacyDecisionEntries(controller);
  }
  const recommendation = recommendationIndex.get(action);

  return [
    {
      key: `${action}-${score}`,
      action,
      score,
      explanation: decision.explanation ?? recommendation?.action.explanation ?? 'No explanation provided.',
      details: {
        ...normalizeDetails(recommendation?.details),
        ...normalizeDetails(decision.details),
      },
    },
  ];
}

function resolveTopDecision(controller: Controller, entries: DecisionEntry[]): DecisionEntry | null {
  const decision = controller.currentPreview?.decision;
  const recommendationIndex = buildRecommendationIndex(controller);
  if (decision) {
    const leadCandidate = decision.candidates?.[0];
    const action = decision.selected_action ?? decision.top_action ?? decision.action ?? leadCandidate?.action;
    if (action) {
      const recommendation = recommendationIndex.get(action);
      const score = asNumber(
        decision.selected_score ?? decision.top_score ?? decision.score ?? leadCandidate?.score,
      );
      return {
        key: `decision-top-${action}-${score}`,
        action,
        score,
        explanation:
          decision.explanation
          ?? leadCandidate?.explanation
          ?? recommendation?.action.explanation
          ?? 'Run a preview to inspect the best action.',
        details: {
          ...normalizeDetails(recommendation?.details),
          ...normalizeDetails(leadCandidate?.details),
          ...normalizeDetails(decision.details),
        },
      };
    }
  }

  return entries[0] ?? null;
}

export function DecisionSurface({ controller }: { controller: Controller }) {
  const decisionEntries = buildDecisionEntries(controller);
  const topDecision = resolveTopDecision(controller, decisionEntries);

  return (
    <section className="panel glass workbench-center">
      <div className="panel-head">
        <div>
          <p className="label">Decision Surface</p>
          <h2>Decision Surface</h2>
        </div>
        {controller.comparisonDelta ? (
          <span className="pill">
            delta {controller.comparisonDelta.topScoreDelta.toFixed(4)}
          </span>
        ) : null}
      </div>

      <article className="recommendation-card top">
        <div className="rec-head">
          <strong>{topDecision?.action ?? 'pending'}</strong>
          <span>{topDecision ? topDecision.score.toFixed(4) : '0.0000'}</span>
        </div>
        <p>{topDecision?.explanation ?? 'Run a preview to inspect the best action.'}</p>
      </article>

      <div className="workbench-stack" style={{ marginTop: 16 }}>
        {decisionEntries.length ? decisionEntries.map((item) => (
          <div className="recommendation-card" key={item.key}>
            <div className="rec-head">
              <strong>{item.action}</strong>
              <span>{item.score.toFixed(4)}</span>
            </div>
            <p>{item.explanation}</p>
            <div className="detail-grid">
              {Object.entries(item.details).map(([key, value]) => (
                <div className="matrix-row" key={key}>
                  <span>{key}</span>
                  <strong>{value.toFixed(2)}</strong>
                </div>
              ))}
            </div>
          </div>
        )) : <p className="muted">No recommendations yet.</p>}
      </div>
    </section>
  );
}
