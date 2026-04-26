import { describe, expect, it } from 'vitest';
import { normalizeWorkbenchContexts } from './backendContexts';

describe('backendContexts', () => {
  it('normalizes backend workbench contexts into chapter mapped contexts with quality metadata', () => {
    const contexts = normalizeWorkbenchContexts({
      contexts: [
        {
          id: 'live-chapter-18',
          chapterNumber: 18,
          title: 'Current Live Chapter',
          stage: 'middle',
          summary: 'History-backed live context',
          state: {
            chapter_index: 18,
            stage: 'middle',
            mainline_progress: 0.61,
            sideplot_progress: 0.37,
            conflict_intensity: 0.64,
            emotional_temperature: 0.53,
            pacing_speed: 0.49,
            foreshadowing_load: 0.36,
            payoff_pressure: 0.31,
            characters: {},
            tags: ['power', 'middle'],
          },
          compare_baseline: {
            baseline_context_id: 'live-chapter-17',
            baseline_chapter_number: 17,
            delta: {
              mainline_progress: 0.03,
              payoff_pressure: 0.07,
            },
          },
          v4_preview: {
            enabled: true,
            candidate_count: 2,
            retention_sort_key: 'retention_score',
            relationship_graph: {
              node_count: 2,
              edge_count: 1,
              displacement_count: 1,
            },
            relationship_displacements: [
              {
                source_character: 'live-chapter-18-hero',
                target_character: 'live-chapter-18-rival',
                delta_tension: 0.22,
              },
            ],
            retention_writeback: {
              feedback_count: 2,
              feedback_signal: -0.3,
              adaptation_mode: 'feedback-driven-multi-window',
              aggregation_strategy: 'multi-window-decay-denoise',
              feedback_denoised_count: 1,
              window_signals: [
                {
                  window_size: 3,
                  signal: -0.18,
                  count: 3,
                  weight: 0.5,
                },
              ],
            },
            memory_summary: {
              context_id: 'live-chapter-18',
              history_window: 50,
              relationship_history_count: 6,
              feedback_history_count: 4,
              relationship_timeline_displacement_count: 1,
              memory_strategy: 'append-window-decay-denoise-v2',
              relationship_decay_dropped_count: 1,
              feedback_decay_dropped_count: 1,
              candidate_timeline_count: 1,
              genre_auto_learning_mode: 'feedback-adaptive-v1',
              genre_auto_learning_applied: true,
              genre_auto_learning_sample_count: 5,
              genre_auto_learning_denoised_count: 0,
              genre_auto_learning_feedback_signal: 0.27,
              genre_auto_learning_bias_count: 5,
              genre_auto_learning_guard_triggered: false,
              genre_auto_learning_fallback_mode: 'bias-update-applied',
            },
            genre_calibration: {
              genre: 'power_fantasy',
              learning_mode: 'feedback-adaptive-v1',
              applied: true,
              feedback_signal: 0.27,
              sample_count: 5,
              denoised_count: 0,
              guard_triggered: false,
              fallback_mode: 'bias-update-applied',
              accept_rate: 0.8,
              signal_recent: 0.31,
              signal_long: 0.27,
              signal_volatility: 0.18,
              signal_divergence: 0.04,
              bias_updates: {
                risk_appetite_bias: 0.024,
                avoidance_bias: -0.018,
              },
            },
            relationship_timeline: [
              {
                chapter_index: 18,
                average_tension: 0.71,
                dominant_gap: 'status',
                sample_count: 2,
                displacement_count: 1,
                peak_delta_tension: 0.22,
              },
            ],
            candidate_timeline: [
              {
                chapter_index: 18,
                feedback_signal: -0.15,
                accept_rate: 0.5,
                sample_count: 2,
              },
            ],
            selected_candidate: {
              candidate_id: 'candidate-1',
              predicted_action: 'break-the-balance',
              predicted_turning_point: 'relationship-shift',
              predicted_conflict_type: 'status-clash',
              predicted_payoff_type: 'relationship-reversal',
              retention_score: 0.73,
              tension_score: 0.71,
              explanation: 'Relationship tension escalates into a direct confrontation.',
              risk_flags: ['template-risk'],
            },
            top_candidates: [
              {
                candidate_id: 'candidate-1',
                predicted_action: 'break-the-balance',
                predicted_turning_point: 'relationship-shift',
                predicted_conflict_type: 'status-clash',
                predicted_payoff_type: 'relationship-reversal',
                retention_score: 0.73,
                tension_score: 0.71,
                explanation: 'Relationship tension escalates into a direct confrontation.',
                risk_flags: ['template-risk'],
              },
            ],
            qc_summary: {
              warnings: ['template-risk'],
            },
          },
          admission: 'approved',
          primary_function: 'conflict-escalation',
          style_dna: {
            pace: 'brisk',
            dialogue_reliance: 'medium',
          },
          checkpoints: [
            {
              name: 'chapter-function-fit',
              status: 'pass',
              evidence: 'Primary function resolved.',
              implication: 'Function label is stable.',
            },
            {
              name: 'continuity-stability',
              status: 'mixed',
              evidence: 'Identity is mostly stable.',
              implication: 'Manual review may be useful.',
            },
          ],
          quality_notes: 'Derived from imported quality pipeline.',
        },
      ],
    });

    expect(contexts[0].chapterNumber).toBe(18);
    expect(contexts[0].summary).toContain('History-backed');
    expect(contexts[0].compareBaseline).toEqual({
      baselineContextId: 'live-chapter-17',
      baselineChapterNumber: 17,
      delta: {
        mainline_progress: 0.03,
        payoff_pressure: 0.07,
      },
    });
    expect(contexts[0].quality).toEqual({
      admission: 'approved',
      primaryFunction: 'conflict-escalation',
      styleDna: {
        pace: 'brisk',
        dialogue_reliance: 'medium',
      },
      checkpoints: [
        {
          name: 'chapter-function-fit',
          status: 'pass',
          evidence: 'Primary function resolved.',
          implication: 'Function label is stable.',
        },
        {
          name: 'continuity-stability',
          status: 'mixed',
          evidence: 'Identity is mostly stable.',
          implication: 'Manual review may be useful.',
        },
      ],
      checkpointSummary: {
        total: 2,
        pass: 1,
        mixed: 1,
        fail: 0,
      },
      qualityNotes: 'Derived from imported quality pipeline.',
    });
    expect(contexts[0].v4Preview).toEqual({
      enabled: true,
      candidateCount: 2,
      retentionSortKey: 'retention_score',
      relationshipGraph: {
        nodeCount: 2,
        edgeCount: 1,
        displacementCount: 1,
      },
      relationshipDisplacements: [
        {
          sourceCharacter: 'live-chapter-18-hero',
          targetCharacter: 'live-chapter-18-rival',
          deltaTension: 0.22,
        },
      ],
      retentionWriteback: {
        feedbackCount: 2,
        feedbackSignal: -0.3,
        adaptationMode: 'feedback-driven-multi-window',
        aggregationStrategy: 'multi-window-decay-denoise',
        feedbackDenoisedCount: 1,
        windowSignals: [
          {
            windowSize: 3,
            signal: -0.18,
            count: 3,
            weight: 0.5,
          },
        ],
      },
      memorySummary: {
        contextId: 'live-chapter-18',
        historyWindow: 50,
        relationshipHistoryCount: 6,
        feedbackHistoryCount: 4,
        relationshipTimelineDisplacementCount: 1,
        memoryStrategy: 'append-window-decay-denoise-v2',
        relationshipDecayDroppedCount: 1,
        feedbackDecayDroppedCount: 1,
        candidateTimelineCount: 1,
        genreAutoLearningMode: 'feedback-adaptive-v1',
        genreAutoLearningApplied: true,
        genreAutoLearningSampleCount: 5,
        genreAutoLearningDenoisedCount: 0,
        genreAutoLearningFeedbackSignal: 0.27,
        genreAutoLearningBiasCount: 5,
        genreAutoLearningGuardTriggered: false,
        genreAutoLearningFallbackMode: 'bias-update-applied',
      },
      genreCalibration: {
        genre: 'power_fantasy',
        learningMode: 'feedback-adaptive-v1',
        applied: true,
        feedbackSignal: 0.27,
        sampleCount: 5,
        denoisedCount: 0,
        guardTriggered: false,
        fallbackMode: 'bias-update-applied',
        acceptRate: 0.8,
        signalRecent: 0.31,
        signalLong: 0.27,
        signalVolatility: 0.18,
        signalDivergence: 0.04,
        biasUpdates: {
          risk_appetite_bias: 0.024,
          avoidance_bias: -0.018,
        },
      },
      relationshipTimeline: [
        {
          chapterIndex: 18,
          averageTension: 0.71,
          dominantGap: 'status',
          sampleCount: 2,
          displacementCount: 1,
          peakDeltaTension: 0.22,
        },
      ],
      candidateTimeline: [
        {
          chapterIndex: 18,
          feedbackSignal: -0.15,
          acceptRate: 0.5,
          sampleCount: 2,
        },
      ],
      selectedCandidate: {
        candidateId: 'candidate-1',
        predictedAction: 'break-the-balance',
        predictedTurningPoint: 'relationship-shift',
        predictedConflictType: 'status-clash',
        predictedPayoffType: 'relationship-reversal',
        retentionScore: 0.73,
        tensionScore: 0.71,
        explanation: 'Relationship tension escalates into a direct confrontation.',
        riskFlags: ['template-risk'],
      },
      topCandidates: [
        {
          candidateId: 'candidate-1',
          predictedAction: 'break-the-balance',
          predictedTurningPoint: 'relationship-shift',
          predictedConflictType: 'status-clash',
          predictedPayoffType: 'relationship-reversal',
          retentionScore: 0.73,
          tensionScore: 0.71,
          explanation: 'Relationship tension escalates into a direct confrontation.',
          riskFlags: ['template-risk'],
        },
      ],
      qcSummary: {
        warnings: ['template-risk'],
      },
    });
  });

  it('keeps quality metadata undefined when the backend does not provide it', () => {
    const contexts = normalizeWorkbenchContexts({
      contexts: [
        {
          id: 'live-chapter-04',
          chapterNumber: 4,
          title: 'Live Context',
          stage: 'middle',
          summary: 'No quality metadata attached',
          state: {
            chapter_index: 4,
            stage: 'middle',
            mainline_progress: 0.38,
            sideplot_progress: 0.28,
            conflict_intensity: 0.55,
            emotional_temperature: 0.47,
            pacing_speed: 0.46,
            foreshadowing_load: 0.33,
            payoff_pressure: 0.29,
            characters: {},
            tags: ['middle'],
          },
        },
      ],
    });

    expect(contexts[0].quality).toBeUndefined();
    expect(contexts[0].v4Preview).toBeUndefined();
  });
});
