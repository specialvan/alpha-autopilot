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
import { ValueTrendPanel } from './components/ValueTrendPanel';
import { VersionComparePanel } from './components/VersionComparePanel';
import { HistoryPanel } from './components/HistoryPanel';
import { FeedbackPanel } from './components/FeedbackPanel';
import { LogsPanel } from './components/LogsPanel';
import { V4ObservabilityPanel } from './components/V4ObservabilityPanel';
import { exportHistory, fetchDashboard, fetchHistory, fetchRecommendationPreview, runTraining, submitFeedback, type DashboardResponse, type HistoryResponse, type Recommendation, type TrainingResponse, type TuningWeight } from './api';
import { overview as fallbackOverview, narrativeSignals as fallbackSignals, matrixWeights as fallbackWeights, chapterSummary as fallbackSummary, tuningWeights as fallbackTuning, recommendations as fallbackRecommendations, feedbackNotes as fallbackFeedback, logs as fallbackLogs, trainingSnapshot as fallbackTraining } from './data';

const DEFAULT_HISTORY_FILTER = { limit: 20 };

export function App() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [historyFilter, setHistoryFilter] = useState<{ stage?: string; action?: string; limit?: number }>(DEFAULT_HISTORY_FILTER);
  const [tuning, setTuning] = useState<TuningWeight[]>(fallbackTuning);
  const [recommendations, setRecommendations] = useState<Recommendation[]>(fallbackRecommendations);
  const [trainingResult, setTrainingResult] = useState<TrainingResponse | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [feedbackSummary, setFeedbackSummary] = useState<TrainingResponse['value_metrics'] | null>(null);
  const [feedbackTopActions, setFeedbackTopActions] = useState<Array<{ action: string; average_quality: number }> | null>(null);
  const [historySnapshots, setHistorySnapshots] = useState<TrainingResponse[]>([]);
  const [historyLogs, setHistoryLogs] = useState<string[]>([]);

  const normalizeHistoryFilter = (filter: { stage?: string; action?: string; limit?: number } = {}) => ({
    ...(filter.stage ? { stage: filter.stage } : {}),
    ...(filter.action ? { action: filter.action } : {}),
    limit: filter.limit ?? DEFAULT_HISTORY_FILTER.limit,
  });

  const refreshHistory = (filter = historyFilter) => {
    const next = normalizeHistoryFilter(filter);
    fetchHistory(next)
      .then((result) => {
        setHistory(result);
        setHistoryLogs(result.historyLogs.map((item) => `${item.time} ${item.text}`));
      })
      .catch(() => setHistory(null));
  };

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

    fetchHistory(historyFilter)
      .then((result) => {
        if (!cancelled) {
          setHistory(result);
          setHistoryLogs(result.historyLogs.map((item) => `${item.time} ${item.text}`));
        }
      })
      .catch(() => {
        if (!cancelled) setHistory(null);
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
  const v4Observability = data?.v4Observability;

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
      setHistorySnapshots((current) => [...current, result].slice(-5));
      setHistoryLogs((current) => [...current, `训练版本 ${result.version} 完成，反馈 ${result.summary.avg_feedback.toFixed(3)}`].slice(-8));
      setError(null);
      refreshHistory();
    } catch (trainError) {
      setError(trainError instanceof Error ? trainError.message : 'training failed');
      const fallbackResult: TrainingResponse = {
        version: fallbackTraining.version,
        sample_count: fallbackTraining.sampleCount,
        bias: 0.0,
        weights: Object.fromEntries(fallbackTraining.weights.map(([name, value]) => [name, Number(value)])),
        summary: {
          count: fallbackTraining.sampleCount,
          avg_predicted: fallbackTraining.averagePredicted,
          avg_target: fallbackTraining.averageTarget,
          avg_feedback: fallbackTraining.averageFeedback,
          rmse: 0.031,
        },
        history: fallbackTraining.history,
        value_metrics: {
          sample_count: fallbackTraining.sampleCount,
          accept_rate: 0.75,
          average_chapter_quality: 0.82,
          average_followup_writeability: 0.79,
          average_continuity_delta: 0.03,
        },
        top_actions: fallbackTraining.history.map((item) => ({ action: item.action, average_quality: item.feedback })).slice(0, 3),
      };
      setTrainingResult(fallbackResult);
      setHistorySnapshots((current) => [...current, fallbackResult].slice(-5));
      setHistoryLogs((current) => [...current, `训练版本 ${fallbackResult.version} 使用本地回退数据`].slice(-8));
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
      if (result.value_summary) setFeedbackSummary(result.value_summary);
      if (result.top_actions) setFeedbackTopActions(result.top_actions);
      if (!result.accepted) {
        setError(result.message);
      } else {
        setHistoryLogs((current) => [...current, `反馈 ${top.action} 已记录${result.version ? `，版本 ${result.version}` : ''}`].slice(-8));
        refreshHistory();
      }
    } catch (feedbackError) {
      setError(feedbackError instanceof Error ? feedbackError.message : 'feedback failed');
    } finally {
      setActionLoading(null);
    }
  };

  const handleHistoryFilter = (filter: { stage?: string; action?: string; limit?: number }) => {
    const next = normalizeHistoryFilter(filter);
    setHistoryFilter(next);
    refreshHistory(next);
  };

  const handleExport = async () => {
    try {
      const result = await exportHistory();
      setHistoryLogs((current) => [...current, `历史已导出至 ${result.path}`].slice(-8));
    } catch (exportError) {
      setError(exportError instanceof Error ? exportError.message : 'export failed');
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
          <ValueTrendPanel current={trainingResult} baseline={fallbackTraining} />
          <VersionComparePanel current={trainingResult} baseline={fallbackTraining} />
        </section>
        <section className="content-grid two">
          <HistoryPanel history={history} liveSnapshots={historySnapshots} valueSummary={feedbackSummary} topActions={feedbackTopActions} onFilterChange={handleHistoryFilter} />
          <FeedbackPanel notes={feedbackNotes} onTrain={handleTrain} onFeedback={handleFeedback} summary={feedbackSummary} topActions={feedbackTopActions} />
        </section>
        <section className="content-grid two">
          <V4ObservabilityPanel snapshot={v4Observability} />
          <LogsPanel logs={logs} />
        </section>
        <section className="content-grid two">
          <section className="panel glass">
            <div className="panel-head">
              <div>
                <p className="label">归档 / 备份 / 迁移</p>
                <h3>历史导出工具</h3>
              </div>
              <span className="pill">archive-ready</span>
            </div>
            <ul className="note-list">
              <li>支持把训练日志和价值记录导出为 JSON。</li>
              <li>导出文件可用于离线分析和归档。</li>
              <li>可作为迁移到新存储后端的数据中转格式。</li>
            </ul>
            <div className="review-flag-row" style={{ marginTop: 16 }}>
              <button className="primary" type="button" onClick={handleExport}>导出历史</button>
            </div>
          </section>
        </section>
      </main>
    </div>
  );
}
