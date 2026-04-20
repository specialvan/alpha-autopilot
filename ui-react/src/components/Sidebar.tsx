import type { OverviewResponse } from '../api';

export function Sidebar({ overview }: { overview: OverviewResponse }) {
  return (
    <aside className="sidebar glass">
      <div className="brand">
        <div className="brand-mark">NQ</div>
        <div>
          <p className="eyebrow">Novel Quant Lab</p>
          <h1>章节推荐中台</h1>
        </div>
      </div>

      <nav className="nav">
        <a href="#overview" className="nav-item active">总览</a>
        <a href="#state" className="nav-item">叙事状态</a>
        <a href="#matrix" className="nav-item">特征矩阵</a>
        <a href="#recommendations" className="nav-item">推荐结果</a>
        <a href="#feedback" className="nav-item">反馈闭环</a>
        <a href="#logs" className="nav-item">训练日志</a>
      </nav>

      <div className="sidebar-card">
        <p className="label">当前版本</p>
        <strong>{overview.matrixVersion}</strong>
        <p className="muted">可追踪、可回滚、可比较的矩阵快照</p>
      </div>

      <div className="sidebar-card accent">
        <p className="label">推荐健康度</p>
        <div className="ring">
          <span>{overview.healthValue}</span>
          <small>/100</small>
        </div>
        <p className="muted">当前处于可用的早期收敛阶段</p>
      </div>
    </aside>
  );
}
