export function FeedbackPanel({
  notes,
  onTrain,
  onFeedback,
  summary,
  topActions,
}: {
  notes: string[];
  onTrain: () => void;
  onFeedback: () => void;
  summary: {
    sample_count: number;
    accept_rate: number;
    average_chapter_quality: number;
    average_followup_writeability: number;
    average_continuity_delta: number;
  } | null;
  topActions: Array<{ action: string; average_quality: number }> | null;
}) {
  return (
    <article className="panel glass" id="feedback">
      <div className="panel-head">
        <div>
          <p className="label">反馈闭环</p>
          <h3>训练结果与反馈趋势</h3>
        </div>
        <span className="pill">stable</span>
      </div>

      <div className="feedback-graph">
        <div className="bar-col"><span style={{ height: '42%' }} /><small>样本 A</small></div>
        <div className="bar-col"><span style={{ height: '58%' }} /><small>样本 B</small></div>
        <div className="bar-col"><span style={{ height: '66%' }} /><small>样本 C</small></div>
        <div className="bar-col active"><span style={{ height: '74%' }} /><small>当前轮次</small></div>
      </div>
      <ul className="note-list">
        {notes.map((note) => <li key={note}>{note}</li>)}
      </ul>

      {summary ? (
        <div className="matrix-list" style={{ marginTop: 16 }}>
          <div className="matrix-row"><span>采纳率</span><strong>{(summary.accept_rate * 100).toFixed(1)}%</strong></div>
          <div className="matrix-row"><span>章节质量</span><strong>{summary.average_chapter_quality.toFixed(3)}</strong></div>
          <div className="matrix-row"><span>后续可写性</span><strong>{summary.average_followup_writeability.toFixed(3)}</strong></div>
          <div className="matrix-row"><span>连续性变化</span><strong>{summary.average_continuity_delta.toFixed(3)}</strong></div>
        </div>
      ) : null}

      {topActions?.length ? (
        <>
          <p className="label" style={{ marginTop: 16 }}>高价值动作</p>
          <div className="matrix-list">
            {topActions.map((item) => (
              <div className="matrix-row" key={item.action}>
                <span>{item.action}</span>
                <strong>{item.average_quality.toFixed(3)}</strong>
              </div>
            ))}
          </div>
        </>
      ) : null}

      <div className="review-flag-row" style={{ marginTop: 16 }}>
        <button className="secondary" type="button" onClick={onTrain}>运行训练</button>
        <button className="primary" type="button" onClick={onFeedback}>提交反馈</button>
      </div>
    </article>
  );
}
