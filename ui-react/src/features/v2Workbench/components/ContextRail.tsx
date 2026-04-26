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
  const quality = selectedContext?.quality;
  const compareBaseline = selectedContext?.compareBaseline;
  const baselineDeltaEntries = Object.entries(compareBaseline?.delta ?? {})
    .filter((entry): entry is [string, number] => typeof entry[1] === 'number')
    .sort((left, right) => Math.abs(right[1]) - Math.abs(left[1]));
  const v4Preview = controller.currentV4Preview ?? selectedContext?.v4Preview;
  const selectedV4Candidate = v4Preview?.selectedCandidate ?? null;
  const timelineDisplacementCount = v4Preview?.relationshipTimeline
    ? v4Preview.relationshipTimeline.reduce((total, item) => total + item.displacementCount, 0)
    : (v4Preview?.memorySummary?.relationshipTimelineDisplacementCount ?? 0);
  const relationshipTimeline = v4Preview?.relationshipTimeline ?? [];
  const relationshipTimelineMax = relationshipTimeline.length
    ? Math.max(...relationshipTimeline.map((item) => item.averageTension), 0.01)
    : 0.01;
  const candidateTimeline = v4Preview?.candidateTimeline ?? [];
  const candidateTimelineMaxSignal = candidateTimeline.length
    ? Math.max(...candidateTimeline.map((item) => Math.abs(item.feedbackSignal)), 0.1)
    : 0.1;
  const genreCalibration = v4Preview?.genreCalibration;
  const genreBiasCount = genreCalibration?.biasUpdates
    ? Object.keys(genreCalibration.biasUpdates).length
    : (v4Preview?.memorySummary?.genreAutoLearningBiasCount ?? 0);
  const v4WarningsRaw = v4Preview?.qcSummary?.warnings;
  const v4Warnings = Array.isArray(v4WarningsRaw)
    ? v4WarningsRaw.filter((item): item is string => typeof item === 'string')
    : [];
  const styleDnaEntries = Object.entries(quality?.styleDna ?? {});
  const checkpointSummary = quality?.checkpointSummary;
  const hasQualityMetadata =
    Boolean(quality?.admission)
    || Boolean(quality?.primaryFunction)
    || Boolean(checkpointSummary)
    || Boolean(quality?.qualityNotes)
    || Boolean(quality?.checkpoints?.length)
    || styleDnaEntries.length > 0;

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
        <strong>{selectedContext?.title ?? 'No context loaded'}</strong>
        <p className="muted">{selectedContext?.summary ?? 'No backend context loaded yet.'}</p>
      </div>

      <div className="field-card">
        <span className="label">Compare Baseline</span>
        {compareBaseline ? (
          <>
            <div className="matrix-row">
              <span>Baseline Chapter</span>
              <strong>{compareBaseline.baselineChapterNumber ?? 'n/a'}</strong>
            </div>
            {compareBaseline.baselineContextId ? (
              <div className="matrix-row">
                <span>Baseline Context</span>
                <strong>{compareBaseline.baselineContextId}</strong>
              </div>
            ) : null}
            {baselineDeltaEntries.slice(0, 3).map(([field, value]) => (
              <div className="matrix-row" key={field}>
                <span>{field}</span>
                <strong>{value >= 0 ? `+${value.toFixed(2)}` : value.toFixed(2)}</strong>
              </div>
            ))}
          </>
        ) : (
          <p className="muted">No baseline comparison loaded.</p>
        )}
      </div>

      <div className="field-card">
        <span className="label">Context Quality</span>
        {hasQualityMetadata ? (
          <>
            {quality?.admission ? (
              <div className="matrix-row">
                <span>Admission</span>
                <strong>{quality.admission}</strong>
              </div>
            ) : null}
            {quality?.primaryFunction ? (
              <div className="matrix-row">
                <span>Primary Function</span>
                <strong>{quality.primaryFunction}</strong>
              </div>
            ) : null}
            {checkpointSummary ? (
              <div className="matrix-row">
                <span>Checkpoint Summary</span>
                <strong>
                  {checkpointSummary.pass} pass / {checkpointSummary.mixed} mixed / {checkpointSummary.fail} fail
                </strong>
              </div>
            ) : null}
            {quality?.qualityNotes ? (
              <p className="muted">{quality.qualityNotes}</p>
            ) : null}
            {quality?.checkpoints?.slice(0, 3).map((checkpoint, index) => (
              <div className="matrix-row" key={`${checkpoint.name}-${checkpoint.status}-${index}`}>
                <span>{checkpoint.name}</span>
                <strong>{checkpoint.status}</strong>
              </div>
            ))}
            {styleDnaEntries.map(([key, value]) => (
              <div className="matrix-row" key={key}>
                <span>{key}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </>
        ) : (
          <p className="muted">No quality metadata loaded.</p>
        )}
      </div>

      <div className="field-card">
        <span className="label">V4 Candidate Preview</span>
        {v4Preview ? (
          <>
            <div className="matrix-row">
              <span>Status</span>
              <strong>{v4Preview.enabled ? 'enabled' : v4Preview.fallbackReason ?? 'fallback'}</strong>
            </div>
            <div className="matrix-row">
              <span>Candidate Count</span>
              <strong>{v4Preview.candidateCount}</strong>
            </div>
            {v4Preview.relationshipGraph ? (
              <>
                <div className="matrix-row">
                  <span>Graph Nodes / Edges</span>
                  <strong>
                    {v4Preview.relationshipGraph.nodeCount}
                    {' / '}
                    {v4Preview.relationshipGraph.edgeCount}
                  </strong>
                </div>
                <div className="matrix-row">
                  <span>Displacements</span>
                  <strong>{v4Preview.relationshipGraph.displacementCount}</strong>
                </div>
              </>
            ) : null}
            {v4Preview.retentionWriteback ? (
              <>
                <div className="matrix-row">
                  <span>Retention Feedback</span>
                  <strong>
                    {v4Preview.retentionWriteback.feedbackCount}
                    {' @ '}
                    {v4Preview.retentionWriteback.feedbackSignal.toFixed(2)}
                  </strong>
                </div>
                {v4Preview.retentionWriteback.aggregationStrategy ? (
                  <div className="matrix-row">
                    <span>Feedback Strategy</span>
                    <strong>{v4Preview.retentionWriteback.aggregationStrategy}</strong>
                  </div>
                ) : null}
                {typeof v4Preview.retentionWriteback.feedbackDenoisedCount === 'number' ? (
                  <div className="matrix-row">
                    <span>Denoised Items</span>
                    <strong>{v4Preview.retentionWriteback.feedbackDenoisedCount}</strong>
                  </div>
                ) : null}
                {v4Preview.retentionWriteback.windowSignals?.slice(0, 2).map((windowSignal) => (
                  <div className="matrix-row" key={`${windowSignal.windowSize}-${windowSignal.count}`}>
                    <span>
                      Win {windowSignal.windowSize}
                      {' / '}
                      w={windowSignal.weight.toFixed(2)}
                    </span>
                    <strong>{windowSignal.signal.toFixed(2)}</strong>
                  </div>
                ))}
              </>
            ) : null}
            {v4Preview.memorySummary ? (
              <>
                <div className="matrix-row">
                  <span>Memory Histories</span>
                  <strong>
                    rel {v4Preview.memorySummary.relationshipHistoryCount}
                    {' / '}fb {v4Preview.memorySummary.feedbackHistoryCount}
                  </strong>
                </div>
                {v4Preview.memorySummary.historyWindow ? (
                  <div className="matrix-row">
                    <span>Memory Window</span>
                    <strong>{v4Preview.memorySummary.historyWindow}</strong>
                  </div>
                ) : null}
                {v4Preview.memorySummary.memoryStrategy ? (
                  <div className="matrix-row">
                    <span>Memory Strategy</span>
                    <strong>{v4Preview.memorySummary.memoryStrategy}</strong>
                  </div>
                ) : null}
                {v4Preview.memorySummary.genreAutoLearningMode ? (
                  <div className="matrix-row">
                    <span>Genre Learning</span>
                    <strong>{v4Preview.memorySummary.genreAutoLearningMode}</strong>
                  </div>
                ) : null}
                {typeof v4Preview.memorySummary.genreAutoLearningFeedbackSignal === 'number' ? (
                  <div className="matrix-row">
                    <span>Genre Feedback Signal</span>
                    <strong>{v4Preview.memorySummary.genreAutoLearningFeedbackSignal.toFixed(2)}</strong>
                  </div>
                ) : null}
                {(v4Preview.memorySummary.genreAutoLearningSampleCount ?? 0) > 0 ? (
                  <div className="matrix-row">
                    <span>Genre Samples</span>
                    <strong>
                      {v4Preview.memorySummary.genreAutoLearningSampleCount}
                      {' / denoise '}
                      {v4Preview.memorySummary.genreAutoLearningDenoisedCount ?? 0}
                    </strong>
                  </div>
                ) : null}
                {genreBiasCount > 0 ? (
                  <div className="matrix-row">
                    <span>Genre Bias Updates</span>
                    <strong>{genreBiasCount}</strong>
                  </div>
                ) : null}
                {v4Preview.memorySummary.genreAutoLearningGuardTriggered ? (
                  <div className="matrix-row">
                    <span>Genre Guard</span>
                    <strong>{v4Preview.memorySummary.genreAutoLearningGuardReason ?? 'triggered'}</strong>
                  </div>
                ) : null}
                {v4Preview.memorySummary.genreAutoLearningFallbackMode ? (
                  <div className="matrix-row">
                    <span>Genre Fallback</span>
                    <strong>{v4Preview.memorySummary.genreAutoLearningFallbackMode}</strong>
                  </div>
                ) : null}
                {v4Preview.memorySummary.genreAutoLearningGuardProfile ? (
                  <div className="matrix-row">
                    <span>Genre Guard Profile</span>
                    <strong>
                      min {v4Preview.memorySummary.genreAutoLearningGuardProfile.minSamples ?? 0}
                      {' / vol '}
                      {(v4Preview.memorySummary.genreAutoLearningGuardProfile.maxVolatility ?? 0).toFixed(2)}
                    </strong>
                  </div>
                ) : null}
                {timelineDisplacementCount > 0 ? (
                  <div className="matrix-row">
                    <span>Timeline Displacements</span>
                    <strong>{timelineDisplacementCount}</strong>
                  </div>
                ) : null}
                {(v4Preview.memorySummary.feedbackDecayDroppedCount ?? 0) > 0 ? (
                  <div className="matrix-row">
                    <span>Feedback Decay Drops</span>
                    <strong>{v4Preview.memorySummary.feedbackDecayDroppedCount}</strong>
                  </div>
                ) : null}
                {(v4Preview.memorySummary.relationshipDecayDroppedCount ?? 0) > 0 ? (
                  <div className="matrix-row">
                    <span>Relationship Decay Drops</span>
                    <strong>{v4Preview.memorySummary.relationshipDecayDroppedCount}</strong>
                  </div>
                ) : null}
              </>
            ) : null}
            {relationshipTimeline.length ? (
              <>
                <div className="matrix-row">
                  <span>Relationship Timeline</span>
                  <strong>{relationshipTimeline.length}</strong>
                </div>
                {relationshipTimeline.slice(0, 2).map((item) => (
                  <div className="matrix-row" key={`${item.chapterIndex}-${item.dominantGap}`}>
                    <span>
                      Ch{item.chapterIndex}
                      {' / '}
                      {item.dominantGap}
                    </span>
                    <strong>
                      {item.averageTension.toFixed(2)}
                      {' x '}
                      {item.sampleCount}
                      {' / d'}
                      {item.displacementCount}
                      {' / peak '}
                      {item.peakDeltaTension.toFixed(2)}
                    </strong>
                  </div>
                ))}
                <div className="workbench-timeline-chart" aria-label="Relationship Timeline Chart">
                  {relationshipTimeline.slice(-6).map((item) => (
                    <div className="workbench-timeline-row" key={`rel-${item.chapterIndex}-${item.dominantGap}`}>
                      <span className="workbench-timeline-label">
                        Ch{item.chapterIndex}
                        {' '}
                        {item.dominantGap}
                      </span>
                      <div className="workbench-timeline-bar">
                        <span
                          className="workbench-timeline-fill"
                          style={{
                            width: `${Math.max(
                              8,
                              Math.round((item.averageTension / relationshipTimelineMax) * 100),
                            )}%`,
                          }}
                        />
                      </div>
                      <strong>{item.averageTension.toFixed(2)}</strong>
                    </div>
                  ))}
                </div>
              </>
            ) : null}
            {candidateTimeline.length ? (
              <>
                <div className="matrix-row">
                  <span>Candidate Timeline</span>
                  <strong>{candidateTimeline.length}</strong>
                </div>
                <div className="workbench-timeline-chart" aria-label="Candidate Timeline Chart">
                  {candidateTimeline.slice(-6).map((item) => (
                    <div className="workbench-timeline-row" key={`cand-${item.chapterIndex}-${item.sampleCount}`}>
                      <span className="workbench-timeline-label">
                        Ch{item.chapterIndex}
                        {' '}
                        {Math.round(item.acceptRate * 100)}%
                      </span>
                      <div className="workbench-timeline-bar">
                        <span
                          className={
                            item.feedbackSignal >= 0
                              ? 'workbench-timeline-fill workbench-timeline-fill--positive'
                              : 'workbench-timeline-fill workbench-timeline-fill--negative'
                          }
                          style={{
                            width: `${Math.max(
                              8,
                              Math.round((Math.abs(item.feedbackSignal) / candidateTimelineMaxSignal) * 100),
                            )}%`,
                          }}
                        />
                      </div>
                      <strong>{item.feedbackSignal.toFixed(2)}</strong>
                    </div>
                  ))}
                </div>
              </>
            ) : null}
            {genreCalibration?.genre ? (
              <div className="matrix-row">
                <span>Genre Profile</span>
                <strong>{genreCalibration.genre}</strong>
              </div>
            ) : null}
            {typeof genreCalibration?.signalVolatility === 'number' ? (
              <div className="matrix-row">
                <span>Genre Volatility</span>
                <strong>{genreCalibration.signalVolatility.toFixed(2)}</strong>
              </div>
            ) : null}
            {typeof genreCalibration?.signalDivergence === 'number' ? (
              <div className="matrix-row">
                <span>Recent/Long Divergence</span>
                <strong>{genreCalibration.signalDivergence.toFixed(2)}</strong>
              </div>
            ) : null}
            {selectedV4Candidate ? (
              <>
                <div className="matrix-row">
                  <span>Selected Action</span>
                  <strong>{selectedV4Candidate.predictedAction}</strong>
                </div>
                <div className="matrix-row">
                  <span>Conflict / Payoff</span>
                  <strong>
                    {selectedV4Candidate.predictedConflictType}
                    {' / '}
                    {selectedV4Candidate.predictedPayoffType}
                  </strong>
                </div>
                <div className="matrix-row">
                  <span>Retention / Tension</span>
                  <strong>
                    {selectedV4Candidate.retentionScore.toFixed(2)}
                    {' / '}
                    {selectedV4Candidate.tensionScore.toFixed(2)}
                  </strong>
                </div>
                {selectedV4Candidate.explanation ? (
                  <p className="muted">{selectedV4Candidate.explanation}</p>
                ) : null}
              </>
            ) : null}
            {v4Warnings.map((warning) => (
              <div className="matrix-row" key={warning}>
                <span>QC Warning</span>
                <strong>{warning}</strong>
              </div>
            ))}
            {v4Preview.relationshipDisplacements.slice(0, 2).map((item) => (
              <div className="matrix-row" key={`${item.sourceCharacter}-${item.targetCharacter}`}>
                <span>
                  {item.sourceCharacter}
                  {' -> '}
                  {item.targetCharacter}
                </span>
                <strong>{item.deltaTension.toFixed(2)}</strong>
              </div>
            ))}
            {v4Preview.topCandidates.slice(0, 2).map((candidate) => (
              <div className="matrix-row" key={candidate.candidateId}>
                <span>{candidate.candidateId}</span>
                <strong>{candidate.predictedAction}</strong>
              </div>
            ))}
          </>
        ) : (
          <p className="muted">No V4 preview loaded.</p>
        )}
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
              <strong>{String(entry.previous)} -&gt; {String(entry.current)}</strong>
            </div>
          ))
        ) : (
          <p className="muted">No overrides applied.</p>
        )}
      </div>
    </aside>
  );
}
