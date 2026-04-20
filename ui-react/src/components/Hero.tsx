export function Hero() {
  return (
    <header className="hero glass" id="overview">
      <div>
        <p className="eyebrow">爆款拆解 · 特征矩阵 · 状态推演 · 反馈闭环</p>
        <h2>面向小说章节规划的量化推荐工作台</h2>
        <p className="lede">
          参考成熟量化系统的生产实践，将“数据接入、信号评分、候选排序、版本追踪、人工复核”统一到一个现代化仪表盘中。
        </p>
      </div>
      <div className="hero-actions">
        <button className="primary">运行一次推荐</button>
        <button className="secondary">导入拆解样本</button>
      </div>
    </header>
  );
}
