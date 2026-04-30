import { useEffect, useMemo, useState } from 'react';
import {
  fetchNarrativeV6CharacterInterview,
  fetchNarrativeV7DecisionPreview,
  type NarrativeV6InterviewMode,
} from '../../../api';
import type { useV2WorkbenchController } from '../useV2WorkbenchController';

type Controller = ReturnType<typeof useV2WorkbenchController>;

const DEFAULT_PROFILE = {
  character_id: 'hero',
  name: 'Hero',
  aliases: [],
  emotion_slider_map: {
    stress_baseline: 2,
    impulsiveness: 1,
    empathy: 1,
    dominance: 2,
  },
  function_type: 'protagonist',
  mbti_suggestion: 'INTJ',
  enneagram_suggestion: '3w4',
  dialogue_style_summary: '短句、克制、带压迫感',
  desire_profile: {
    explicit_desire: '推进主线并守住阵线',
    hidden_desire: '证明判断正确',
    fear: '关键盟友倒戈',
    bottom_line: '不能牺牲核心伙伴',
    current_goal: '夺回叙事主动权',
  },
  behavior_triggers: [
    {
      pressure: '公开羞辱',
      action: '立即反击',
      rationale: '维护主导权',
    },
  ],
  confidence: 0.72,
  evidence: ['示例证据片段'],
  override_log: [],
};

export function CharacterInterviewPanel({ controller }: { controller: Controller }) {
  const selectedContext =
    controller.contexts.find((item) => item.id === controller.selectedChapter) ?? controller.contexts[0];
  const defaultCharacterId = useMemo(() => {
    const characterKeys = Object.keys(selectedContext?.state.characters ?? {});
    return characterKeys[0] ?? 'hero';
  }, [selectedContext]);

  const [characterId, setCharacterId] = useState(defaultCharacterId);
  const [mode, setMode] = useState<NarrativeV6InterviewMode>('voice_test');
  const [userMessage, setUserMessage] = useState('请用你的口吻回答：你为什么现在行动？');
  const [allowHiddenInfo, setAllowHiddenInfo] = useState(false);
  const [profileJson, setProfileJson] = useState(JSON.stringify(DEFAULT_PROFILE, null, 2));
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    reply: string;
    emotionShift: string;
    oocRiskFlags: string[];
    hiddenRiskFlags: string[];
  } | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [previewResult, setPreviewResult] = useState<{
    routeId: string;
    decisionType: string;
    riskLevel: string;
    composite: number;
    reasons: string[];
    defaultsApplied: string[];
  } | null>(null);

  useEffect(() => {
    setCharacterId(defaultCharacterId);
  }, [defaultCharacterId]);

  const runInterview = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const profile = JSON.parse(profileJson) as Record<string, unknown>;
      const response = await fetchNarrativeV6CharacterInterview(characterId.trim() || 'hero', {
        profile,
        chapter_memory: selectedContext
          ? [`Chapter ${selectedContext.chapterNumber}: ${selectedContext.summary}`]
          : [],
        user_message: userMessage,
        mode,
        allow_hidden_info: allowHiddenInfo,
      });
      setResult({
        reply: response.reply,
        emotionShift: response.emotion_state_shift,
        oocRiskFlags: response.ooc_risk_flags,
        hiddenRiskFlags: response.hidden_info_risk_flags,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Interview failed');
      setResult(null);
    } finally {
      setIsRunning(false);
    }
  };

  const runDecisionPreview = async () => {
    setIsPreviewing(true);
    setPreviewError(null);
    try {
      const state = selectedContext?.state ?? {};
      const chapterIndex = typeof state.chapter_index === 'number' ? state.chapter_index : 1;
      const conflictIntensity = typeof state.conflict_intensity === 'number' ? state.conflict_intensity : 0.5;
      const foreshadowingLoad = typeof state.foreshadowing_load === 'number' ? state.foreshadowing_load : 0.5;
      const payoffPressure = typeof state.payoff_pressure === 'number' ? state.payoff_pressure : 0.5;
      const stage = typeof state.stage === 'string' ? state.stage : 'opening';
      const tags = Array.isArray(state.tags) ? state.tags.filter((item) => typeof item === 'string') : [];
      const macroStructure =
        typeof state.macro_structure === 'string' ? state.macro_structure : 'progressive';

      const response = await fetchNarrativeV7DecisionPreview({
        text: selectedContext ? `${selectedContext.title}: ${selectedContext.summary}` : userMessage,
        story_state: {
          chapter_index: chapterIndex,
          stage,
          conflict_intensity: conflictIntensity,
          foreshadowing_load: foreshadowingLoad,
          payoff_pressure: payoffPressure,
          tags,
          macro_structure: macroStructure,
        },
        project_state: {
          project_id: selectedContext?.id ?? 'workbench-live',
          platform: 'workbench',
          genre_track: 'unknown',
          reader_profile: 'unknown',
          ip_flavor_tag: macroStructure,
          selling_point_contract: '',
        },
      });
      setPreviewResult({
        routeId: response.decision.route_id,
        decisionType: response.decision.decision_type,
        riskLevel: response.decision.risk_level,
        composite: response.vector.composite,
        reasons: response.decision.reasons,
        defaultsApplied: response.defaults_applied,
      });
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'V7 decision preview failed');
      setPreviewResult(null);
    } finally {
      setIsPreviewing(false);
    }
  };

  return (
    <section className="panel glass" aria-label="Character Interview Panel">
      <div className="panel-head">
        <div>
          <p className="label">V6</p>
          <h2>Character Interview</h2>
        </div>
      </div>

      <label className="field-card">
        <span className="label">Character ID</span>
        <input
          className="field-input"
          value={characterId}
          onChange={(event) => setCharacterId(event.target.value)}
        />
      </label>

      <label className="field-card">
        <span className="label">Mode</span>
        <select
          className="field-input"
          value={mode}
          onChange={(event) => setMode(event.target.value as NarrativeV6InterviewMode)}
        >
          <option value="voice_test">voice_test</option>
          <option value="scene_reaction">scene_reaction</option>
          <option value="secret_probe">secret_probe</option>
          <option value="free_chat">free_chat</option>
        </select>
      </label>

      <label className="field-card">
        <span className="label">User Message</span>
        <textarea
          className="field-input"
          value={userMessage}
          onChange={(event) => setUserMessage(event.target.value)}
        />
      </label>

      <label className="field-card">
        <span className="label">Profile JSON</span>
        <textarea
          className="field-input"
          value={profileJson}
          onChange={(event) => setProfileJson(event.target.value)}
          style={{ minHeight: 180 }}
        />
      </label>

      <label className="field-card" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <input
          type="checkbox"
          checked={allowHiddenInfo}
          onChange={(event) => setAllowHiddenInfo(event.target.checked)}
        />
        <span>Allow hidden info reveal</span>
      </label>

      <button className="run-btn" disabled={isRunning} onClick={() => void runInterview()} type="button">
        {isRunning ? 'Interviewing...' : 'Run Character Interview'}
      </button>

      {error ? <p className="muted">{error}</p> : null}
      {result ? (
        <div className="field-card">
          <span className="label">Interview Result</span>
          <p>{result.reply}</p>
          <div className="matrix-row">
            <span>Emotion Shift</span>
            <strong>{result.emotionShift}</strong>
          </div>
          <div className="matrix-row">
            <span>OOC Risk</span>
            <strong>{result.oocRiskFlags.length ? result.oocRiskFlags.join(', ') : 'none'}</strong>
          </div>
          <div className="matrix-row">
            <span>Hidden Risk</span>
            <strong>{result.hiddenRiskFlags.length ? result.hiddenRiskFlags.join(', ') : 'none'}</strong>
          </div>
        </div>
      ) : null}

      <div className="field-card">
        <span className="label">V6/V7 Orchestration</span>
        <button
          className="run-btn"
          disabled={isPreviewing}
          onClick={() => void runDecisionPreview()}
          type="button"
        >
          {isPreviewing ? 'Running V6-V7...' : 'Run V6/V7 Decision Preview'}
        </button>
        {previewError ? <p className="muted">{previewError}</p> : null}
        {previewResult ? (
          <div style={{ marginTop: 10, display: 'grid', gap: 6 }}>
            <div className="matrix-row">
              <span>Route ID</span>
              <strong>{previewResult.routeId}</strong>
            </div>
            <div className="matrix-row">
              <span>Decision</span>
              <strong>{previewResult.decisionType}</strong>
            </div>
            <div className="matrix-row">
              <span>Risk</span>
              <strong>{previewResult.riskLevel}</strong>
            </div>
            <div className="matrix-row">
              <span>Composite</span>
              <strong>{previewResult.composite.toFixed(3)}</strong>
            </div>
            <p className="muted">
              Reasons: {previewResult.reasons.length ? previewResult.reasons.join(' | ') : 'none'}
            </p>
            <p className="muted">
              Defaults:{' '}
              {previewResult.defaultsApplied.length ? previewResult.defaultsApplied.join(', ') : 'none'}
            </p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
