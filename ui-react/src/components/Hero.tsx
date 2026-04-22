import { Link } from 'react-router-dom';

export function Hero() {
  return (
    <header className="hero glass" id="overview">
      <div>
        <p className="eyebrow">Decision cockpit for narrative action calibration</p>
        <h2>面向小说章节规划的量化推荐工作台</h2>
        <p className="lede">
          Keep the v1 dashboard for overview and launch the dedicated v2 cockpit for
          transparent chapter-level decisions.
        </p>
      </div>
      <div className="hero-actions">
        <Link className="primary hero-link" to="/v2/workbench">
          Open V2 Workbench
        </Link>
        <button className="secondary" type="button">
          导入拆解样本
        </button>
      </div>
    </header>
  );
}
