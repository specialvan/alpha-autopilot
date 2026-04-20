import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Hero } from './components/Hero';
import { MetricsGrid } from './components/MetricsGrid';
import { StoryStatePanel } from './components/StoryStatePanel';
import { MatrixPanel } from './components/MatrixPanel';
import { ChapterSummaryPanel } from './components/ChapterSummaryPanel';
import { RecommendationsPanel } from './components/RecommendationsPanel';
import { FeedbackPanel } from './components/FeedbackPanel';
import { LogsPanel } from './components/LogsPanel';
import { fetchDashboard, type DashboardResponse } from './api';
import { overview as fallbackOverview, narrativeSignals as fallbackSignals, matrixWeights as fallbackWeights, chapterSummary as fallbackSummary, recommendations as fallbackRecommendations, feedbackNotes as fallbackFeedback, logs as fallbackLogs } from './data';

export function App() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDashboard()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'unknown error');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const overview = data?.overview ?? fallbackOverview;
  const narrativeSignals = data?.narrativeSignals ?? fallbackSignals;
  const matrixWeights = data?.matrixWeights ?? fallbackWeights;
  const chapterSummary = data?.chapterSummary ?? fallbackSummary;
  const recommendations = data?.recommendations ?? fallbackRecommendations;
  const feedbackNotes = data?.feedbackNotes ?? fallbackFeedback;
  const logs = data?.logs ?? fallbackLogs;

  return (
    <div className="app-shell">
      <Sidebar overview={overview} />
      <main className="main">
        <Hero />
        {error ? <div className="banner warning">后端接口暂不可用，当前展示本地回退数据：{error}</div> : null}
        <MetricsGrid overview={overview} />
        <section className="content-grid">
          <StoryStatePanel signals={narrativeSignals} />
          <MatrixPanel weights={matrixWeights} version={overview.matrixVersion} />
        </section>
        <section className="content-grid two">
          <ChapterSummaryPanel summary={chapterSummary} />
          <RecommendationsPanel recommendations={recommendations} />
        </section>
        <section className="content-grid two">
          <FeedbackPanel notes={feedbackNotes} />
          <LogsPanel logs={logs} />
        </section>
        <section className="content-grid two">
          <section className="panel glass">
            <div className="panel-head">
              <div>
                <p className="label">生产实践对齐</p>
                <h3>量化系统的 UX 重点</h3>
              </div>
              <span className="pill">review-ready</span>
            </div>
            <ul className="note-list">
              <li>突出关键指标，避免信息面板过载。</li>
              <li>使用分层卡片和清晰状态色，支持快速扫读。</li>
              <li>每个推荐结果都保留解释理由和权重分布。</li>
              <li>版本、样本、反馈、风险分区展示，便于审查。</li>
              <li>操作按钮集中在可见区域，减少页面跳转成本。</li>
            </ul>
          </section>
          <section className="panel glass">
            <div className="panel-head">
              <div>
                <p className="label">摘要解释</p>
                <h3>章节建议的结构化表达</h3>
              </div>
              <span className="pill success">ready</span>
            </div>
            <ul className="note-list">
              <li>章节建议摘要负责把推荐动作翻译成可写作的结构提示。</li>
              <li>它应该与推荐排序同源，避免前后矛盾。</li>
              <li>后续可扩展为“开头-冲突-转折-回报”的模板化输出。</li>
            </ul>
          </section>
        </section>
      </main>
    </div>
  );
}
