export function FeedbackPanel({ notes, onTrain, onFeedback }: { notes: string[]; onTrain: () => void; onFeedback: () => void }) {
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

      <div className="review-flag-row" style={{ marginTop: 16 }}>
        <button className="secondary" type="button" onClick={onTrain}>运行训练</button>
        <button className="primary" type="button" onClick={onFeedback}>提交反馈</button>
      </div>
    </article>
  );
}
