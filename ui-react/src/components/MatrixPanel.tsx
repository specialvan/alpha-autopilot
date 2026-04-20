import type { MatrixWeight } from '../api';

export function MatrixPanel({ weights, version }: { weights: MatrixWeight[]; version: string }) {
  return (
    <article className="panel glass" id="matrix">
      <div className="panel-head">
        <div>
          <p className="label">特征矩阵</p>
          <h3>可解释的量化权重</h3>
        </div>
        <span className="pill">{version}</span>
      </div>

      <div className="matrix-list">
        {weights.map(({ label, value }) => (
          <div className="matrix-row" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </article>
  );
}
