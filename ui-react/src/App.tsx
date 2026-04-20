import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Hero } from './components/Hero';
import { MetricsGrid } from './components/MetricsGrid';
import { StoryStatePanel } from './components/StoryStatePanel';
import { MatrixPanel } from './components/MatrixPanel';
import { ChapterSummaryPanel } from './components/ChapterSummaryPanel';
import { TuningPanel } from './components/TuningPanel';
import { RecommendationsPanel } from './components/RecommendationsPanel';
import { TrainingResultPanel } from './components/TrainingResultPanel';
import { FeedbackPanel } from './components/FeedbackPanel';
import { LogsPanel } from './components/LogsPanel';
import { fetchDashboard, fetchRecommendationPreview, runTraining, submitFeedback, type DashboardResponse, type Recommendation, type TrainingResponse, type TuningWeight } from './api';
import { overview as fallbackOverview, narrativeSignals as fallbackSignals, matrixWeights as fallbackWeights, chapterSummary as fallbackSummary, tuningWeights as fallbackTuning, recommendations as fallbackRecommendations, feedbackNotes as fallbackFeedback, logs as fallbackLogs, trainingSnapshot as fallbackTraining } from './data';

export function App() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tuning, setTuning] = useState<TuningWeight[]>(fallbackTuning);
  const [recommendations, setRecommendations] = useState<Recommendation[]>(fallbackRecommendations);
  const [trainingResult, setTrainingResult] = useState<TrainingResponse | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDashboard()
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setTuning(result.tuningWeights ?? fallbackTuning);
          setRecommendations(result.recommendations ?? fallbackRecommendations);
        }
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
  const feedbackNotes = data?.feedbackNotes ?? fallbackFeedback;
  const logs = data?.logs ?? fallbackLogs;

  const handleAdjust = (label: string, delta: number) => {
    setTuning((current) =>
      current.map((item) =>
        item.label === label
          ? {
              ...item,
              value: Math.max(0, Math.min(1, Number((item.value + delta).toFixed(2)))),
              direction: delta >= 0 ? 'up' : 'down',
            }
          : item,
      ),
    );
  };

  const handlePreview = async () => {
    setPreviewLoading(true);
    try {
      const result = await fetchRecommendationPreview({ tuningWeights: tuning, recommendations });
      setRecommendations(result.recommendations);
    } catch (previewError) {
      setError(previewError instanceof Error ? previewError.message : 'preview failed');
      setRecommendations((current) => current.slice());
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleTrain = async () => {
    setActionLoading('training');
    try {
      const result = await runTraining();
      setTrainingResult(result);
      setError(null);
    } catch (trainError) {
      setError(trainError instanceof Error ? trainError.message : 'training failed');
      setTrainingResult({
        version: fallbackTraining.version,
        sample_count: fallbackTraining.sampleCount,
        bias: 0.0,
        weights: Object.fromEntries(fallbackTraining.weights.map(([name, value]) => [name, Number(value)])),
        summary: {
          sample_count: fallbackTraining.sampleCount,
          average_predicted: fallbackTraining.averagePredicted,
          average_target: fallbackTraining.averageTarget,
          average_feedback: fallbackTraining.averageFeedback,
        },
        history: fallbackTraining.history,
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleFeedback = async () => {
    setActionLoading('feedback');
    try {
      const top = recommendations[0];
      if (!top) return;
      const result = await submitFeedback({
        recommendationAction: top.action,
        accepted: true,
        score: Number(top.score),
        notes: 'from frontend feedback panel',
      });
      if (!result.accepted) {
        setError(result.message);
      }
    } catch (feedbackError) {
      setError(feedbackError instanceof Error ? feedbackError.message : 'feedback failed');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar overview={overview} />
      <main className="main">
        <Hero />
        {error ? <div className="banner warning">后端接口暂不可用，当前展示本地回退数据：{error}</div> : null}
        {previewLoading ? <div className="banner info">正在刷新推荐预览...</div> : null}
        {actionLoading === 'training' ? <div className="banner info">正在运行训练...</div> : null}
        {actionLoading === 'feedback' ? <div className="banner info">正在提交反馈...</div> : null}
        <MetricsGrid overview={overview} />
        <section className="content-grid">
          <StoryStatePanel signals={narrativeSignals} />
          <MatrixPanel weights={matrixWeights} version={overview.matrixVersion} />
        </section>
        <section className="content-grid two">
          <ChapterSummaryPanel summary={chapterSummary} />
          <TuningPanel weights={tuning} onAdjust={handleAdjust} onPreview={handlePreview} />
        </section>
        <section className="content-grid two">
          <RecommendationsPanel recommendations={recommendations} />
          <TrainingResultPanel result={trainingResult} />
        </section>
        <section className="content-grid two">
          <FeedbackPanel notes={feedbackNotes} onTrain={handleTrain} onFeedback={handleFeedback} />
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
