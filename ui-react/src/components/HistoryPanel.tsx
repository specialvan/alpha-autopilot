import { useMemo, useState } from 'react';
import type { HistoryResponse, TrainingResponse } from '../api';

export function HistoryPanel({
  history,
  liveSnapshots,
  valueSummary,
  topActions,
  onFilterChange,
}: {
  history: HistoryResponse | null;
  liveSnapshots: TrainingResponse[];
  valueSummary: HistoryResponse['valueSummary'] | null;
  topActions: HistoryResponse['topActions'] | null;
  onFilterChange?: (filter: { stage?: string; action?: string; limit?: number }) => void;
}) {
  const [expandedVersion, setExpandedVersion] = useState<string | null>(null);
  const [expandedStage, setExpandedStage] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const logs = history?.historyLogs ?? [];
  const snapshots = history?.historySnapshots ?? [];
  const summary = history?.valueSummary ?? valueSummary;
  const actions = history?.topActions ?? topActions;
  const versions = history?.versionTimeline ?? [];
  const stages = history?.stageTimeline ?? [];
  const filters = history?.filters;

  const filteredVersions = useMemo(() => {
    if (!searchQuery.trim()) return versions;
    const q = searchQuery.trim().toLowerCase();
    return versions.filter((item) => item.version.toLowerCase().includes(q) || item.actions.some((action) => action.toLowerCase().includes(q)));
  }, [versions, searchQuery]);

  const filteredStages = useMemo(() => {
    if (!searchQuery.trim()) return stages;
    const q = searchQuery.trim().toLowerCase();
    return stages.filter((item) => item.stage.toLowerCase().includes(q) || item.versions.some((version) => version.toLowerCase().includes(q)));
  }, [stages, searchQuery]);

  const visibleAction = filters?.action || 'all';
  const quickActions = actions?.slice(0, 6) ?? [];

  const applyAction = (action: string) => {
    setSearchQuery(action);
    onFilterChange?.({ stage: filters?.stage ?? undefined, action, limit: filters?.limit ?? 20 });
  };

  const resetFilters = () => {
    setSearchQuery('');
    onFilterChange?.({ stage: undefined, action: undefined, limit: 20 });
  };

  return (
    <article className="panel glass" id="history">
      <div className="panel-head">
        <div>
          <p className="label">历史轨迹</p>
          <h3>训练 / 反馈 / 价值演化</h3>
        </div>
        <span className="pill success">persisted</span>
      </div>

      <div className="review-flag-row" style={{ marginBottom: 12, gap: 8 }}>
        <input
          value={searchQuery}
          onChange={(event) => {
            setSearchQuery(event.target.value);
          }}
          placeholder="按版本或动作名搜索"
          className="search-input"
          aria-label="搜索历史版本或动作"
        />
        {onFilterChange ? (
          <>
            <button className="secondary" type="button" onClick={resetFilters}>全部</button>
            <button className="secondary" type="button" onClick={() => { setSearchQuery(''); onFilterChange({ stage: 'train', action: undefined, limit: 20 }); }}>训练</button>
            <button className="secondary" type="button" onClick={() => { setSearchQuery(''); onFilterChange({ stage: 'feedback', action: undefined, limit: 20 }); }}>反馈</button>
          </>
        ) : null}
      </div>

      {quickActions.length ? (
        <div className="chip-row" style={{ marginBottom: 12 }}>
          {quickActions.map((item) => (
            <button key={item.action} className="chip-button" type="button" onClick={() => applyAction(item.action)}>
              {item.action}
            </button>
          ))}
        </div>
      ) : null}

      <section className="history-board">
        <div className="history-column">
          <div className="history-column-head">
            <p className="label">Stage Timeline</p>
            <strong>按阶段分组</strong>
          </div>
          <div className="version-card-grid stage-grid">
            {filteredStages.map((stageItem) => {
              const stageExpanded = expandedStage === stageItem.stage;
              const stageVersions = filteredVersions.filter((item) => item.stage === stageItem.stage);
              return (
                <div className={`recommendation-card timeline-card ${stageExpanded ? 'top' : ''}`} key={stageItem.stage}>
                  <button
                    type="button"
                    onClick={() => setExpandedStage(stageExpanded ? null : stageItem.stage)}
                    style={{ all: 'unset', cursor: 'pointer', display: 'block', width: '100%' }}
                  >
                    <div className="rec-head">
                      <strong>{stageItem.stage}</strong>
                      <span>{stageItem.count} 条</span>
                    </div>
                    <p className="muted">最近更新时间 {stageItem.latest_time || 'unknown'}</p>
                    <div className="matrix-list" style={{ marginTop: 12 }}>
                      <div className="matrix-row"><span>平均反馈</span><strong>{stageItem.average_feedback.toFixed(3)}</strong></div>
                      <div className="matrix-row"><span>版本数</span><strong>{stageItem.versions.length}</strong></div>
                    </div>
                    {stageItem.versions.length ? <p className="muted" style={{ marginTop: 8 }}>版本：{stageItem.versions.join(' / ')}</p> : null}
                  </button>

                  {stageExpanded ? (
                    <div className="matrix-list" style={{ marginTop: 12 }}>
                      {stageVersions.map((version) => (
                        <div className="matrix-row" key={version.version}>
                          <span>{version.version} / {version.count} 条</span>
                          <strong>{version.average_feedback.toFixed(3)}</strong>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              );
            })}
            {!filteredStages.length ? <p className="muted">暂无阶段时间线。</p> : null}
          </div>
        </div>

        <div className="history-column">
          <div className="history-column-head">
            <p className="label">Version Timeline</p>
            <strong>按版本展开</strong>
          </div>
          <div className="version-card-grid version-grid" style={{ marginTop: 0 }}>
            {filteredVersions.map((item) => {
              const expanded = expandedVersion === item.version;
              return (
                <div className={`recommendation-card timeline-card ${expanded ? 'top' : ''}`} key={`${item.version}-${item.latest_time}`}>
                  <button
                    type="button"
                    onClick={() => setExpandedVersion(expanded ? null : item.version)}
                    style={{ all: 'unset', cursor: 'pointer', display: 'block', width: '100%' }}
                  >
                    <div className="rec-head">
                      <strong>{item.version}</strong>
                      <span>{item.count} 条</span>
                    </div>
                    <p className="muted">最近更新时间 {item.latest_time || 'unknown'}</p>
                    <div className="matrix-list" style={{ marginTop: 12 }}>
                      <div className="matrix-row"><span>平均反馈</span><strong>{item.average_feedback.toFixed(3)}</strong></div>
                      <div className="matrix-row"><span>动作数</span><strong>{item.actions.length}</strong></div>
                    </div>
                    {item.actions.length ? <p className="muted" style={{ marginTop: 8 }}>动作：{item.actions.join(' / ')}</p> : null}
                  </button>

                  {expanded ? (
                    <div className="matrix-list" style={{ marginTop: 12 }}>
                      <div className="matrix-row"><span>阶段</span><strong>{item.stage || 'all'}</strong></div>
                      <div className="matrix-row"><span>采纳率</span><strong>{(item.accept_rate * 100).toFixed(1)}%</strong></div>
                      <div className="matrix-row"><span>章节质量</span><strong>{item.average_chapter_quality.toFixed(3)}</strong></div>
                      <div className="matrix-row"><span>后续可写性</span><strong>{item.average_followup_writeability.toFixed(3)}</strong></div>
                      <div className="matrix-row"><span>连续性变化</span><strong>{item.average_continuity_delta.toFixed(3)}</strong></div>
                    </div>
                  ) : null}
                </div>
              );
            })}
            {!filteredVersions.length ? <p className="muted">暂无版本时间线。</p> : null}
          </div>
        </div>
      </section>

      <div className="note-list" style={{ marginTop: 16 }}>
        {logs.slice(-4).map((item) => (
          <div className="recommendation-card" key={item.time + item.text}>
            <p className="label">{item.time}</p>
            <p>{item.text}</p>
          </div>
        ))}
        {!logs.length ? <p className="muted">暂无历史日志。</p> : null}
      </div>

      {summary ? (
        <div className="matrix-list" style={{ marginTop: 16 }}>
          <div className="matrix-row"><span>采纳率</span><strong>{(summary.accept_rate * 100).toFixed(1)}%</strong></div>
          <div className="matrix-row"><span>章节质量</span><strong>{summary.average_chapter_quality.toFixed(3)}</strong></div>
          <div className="matrix-row"><span>后续可写性</span><strong>{summary.average_followup_writeability.toFixed(3)}</strong></div>
          <div className="matrix-row"><span>连续性变化</span><strong>{summary.average_continuity_delta.toFixed(3)}</strong></div>
        </div>
      ) : null}

      {actions?.length ? (
        <>
          <p className="label" style={{ marginTop: 16 }}>高价值动作</p>
          <div className="matrix-list">
            {actions.map((item) => (
              <div className="matrix-row" key={item.action}>
                <span>{item.action}</span>
                <strong>{item.average_quality.toFixed(3)}</strong>
              </div>
            ))}
          </div>
        </>
      ) : null}

      {snapshots.length || liveSnapshots.length ? (
        <>
          <p className="label" style={{ marginTop: 16 }}>近期快照</p>
          <div className="matrix-list">
            {snapshots.slice(-2).map((item) => (
              <div className="matrix-row" key={`${item.timestamp}-${item.action}`}>
                <span>{item.stage} / {item.action}</span>
                <strong>{item.feedback.toFixed(3)}</strong>
              </div>
            ))}
            {liveSnapshots.slice(-2).map((item) => (
              <div className="matrix-row" key={item.version}>
                <span>{item.version} / {item.summary.avg_feedback.toFixed(3)}</span>
                <strong>{item.summary.avg_predicted.toFixed(3)}</strong>
              </div>
            ))}
          </div>
        </>
      ) : null}

      {filters ? (
        <p className="muted" style={{ marginTop: 16 }}>
          当前过滤：{filters.stage ?? 'all'} / {visibleAction} / limit {filters.limit}
          {searchQuery.trim() ? ` / search ${searchQuery.trim()}` : ''}
        </p>
      ) : null}
    </article>
  );
}
