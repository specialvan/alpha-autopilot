import type { LogEntry } from '../api';

export function LogsPanel({ logs }: { logs: LogEntry[] }) {
  return (
    <article className="panel glass" id="logs">
      <div className="panel-head">
        <div>
          <p className="label">训练日志</p>
          <h3>版本与样本演进</h3>
        </div>
        <span className="pill">append-only</span>
      </div>

      <div className="log-list">
        {logs.map((log) => (
          <div className="log-item" key={log.time}>
            <span className="log-time">{log.time}</span>
            <p>{log.text}</p>
          </div>
        ))}
      </div>
    </article>
  );
}
