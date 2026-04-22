import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

const NUMERIC_FIELDS: Array<{
  key:
    | 'mainline_progress'
    | 'sideplot_progress'
    | 'conflict_intensity'
    | 'emotional_temperature'
    | 'pacing_speed'
    | 'foreshadowing_load'
    | 'payoff_pressure';
  label: string;
}> = [
  { key: 'mainline_progress', label: 'Mainline' },
  { key: 'sideplot_progress', label: 'Sideplot' },
  { key: 'conflict_intensity', label: 'Conflict' },
  { key: 'emotional_temperature', label: 'Emotion' },
  { key: 'pacing_speed', label: 'Pacing' },
  { key: 'foreshadowing_load', label: 'Foreshadow' },
  { key: 'payoff_pressure', label: 'Payoff' },
];

export function ContextRail({ controller }: { controller: Controller }) {
  const selectedContext =
    controller.contexts.find((item) => item.id === controller.selectedChapter) ?? controller.contexts[0];

  return (
    <aside className="panel glass workbench-rail">
      <div className="panel-head">
        <div>
          <p className="label">Context Rail</p>
          <h2>Chapter Context</h2>
        </div>
      </div>

      <label className="field-card">
        <span className="label">Source</span>
        <select
          className="field-input"
          value={controller.contextSource}
          onChange={(event) =>
            controller.setContextSource(
              event.target.value as 'demo' | 'mapped_chapter' | 'manual_override',
            )
          }
        >
          <option value="demo">demo</option>
          <option value="mapped_chapter">mapped_chapter</option>
          <option value="manual_override">manual_override</option>
        </select>
      </label>

      <label className="field-card">
        <span className="label">Chapter Context</span>
        <select
          aria-label="Chapter Context"
          className="field-input"
          value={controller.selectedChapter}
          onChange={(event) => controller.setSelectedChapter(event.target.value)}
        >
          {controller.contexts.map((item) => (
            <option key={item.id} value={item.id}>
              {item.chapterNumber}: {item.title}
            </option>
          ))}
        </select>
      </label>

      <div className="field-card">
        <span className="label">Mapped Summary</span>
        <strong>{selectedContext.title}</strong>
        <p className="muted">{selectedContext.summary}</p>
      </div>

      <div className="workbench-stack">
        {NUMERIC_FIELDS.map((field) => (
          <label className="field-card" key={field.key}>
            <div className="signal-row">
              <span>{field.label}</span>
              <strong>{Math.round(controller.workingState[field.key] * 100)}%</strong>
            </div>
            <input
              className="range-input"
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={controller.workingState[field.key]}
              onChange={(event) =>
                controller.setNumericOverride(field.key, Number(event.target.value))
              }
            />
          </label>
        ))}
      </div>

      <div className="field-card">
        <span className="label">State Diff</span>
        {controller.stateDiff.length ? (
          controller.stateDiff.map((entry) => (
            <div className="matrix-row" key={String(entry.field)}>
              <span>{String(entry.field)}</span>
              <strong>
                {String(entry.previous)} → {String(entry.current)}
              </strong>
            </div>
          ))
        ) : (
          <p className="muted">No overrides applied.</p>
        )}
      </div>
    </aside>
  );
}
