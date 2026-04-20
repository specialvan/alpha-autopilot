import type { StorySignal } from '../api';

export function StoryStatePanel({ signals }: { signals: StorySignal[] }) {
  return (
    <article className="panel glass" id="state">
      <div className="panel-head">
        <div>
          <p className="label">叙事状态</p>
          <h3>当前章节的上下文信号</h3>
        </div>
        <span className="pill">Chapter 18</span>
      </div>

      <div className="signal-stack">
        {signals.map((signal) => (
          <div className="signal" key={signal.label}>
            <div className="signal-row">
              <span>{signal.label}</span>
              <strong>{signal.value}%</strong>
            </div>
            <div className="bar">
              <span style={{ width: `${signal.value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}
