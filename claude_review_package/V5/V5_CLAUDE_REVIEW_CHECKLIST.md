# V5 Full Acceptance Checklist (AA-01 ~ AA-08)

## 0. Usage

- This checklist is for full-cycle requirement acceptance review.
- Requirement baseline: `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`
- Implementation/test evidence source of truth: `claude_review_package/V5/v5-pr.md`
- Review result must be requirement-driven, not implementation-claim-driven.

## 1. Global Gates (Must Pass)

- [ ] Layer boundary is compliant (`Baseline` unchanged; changes remain in `Increment` scope).
- [ ] New behavior has explicit disable/bypass path where required.
- [ ] Failure paths do not block core generation flow.
- [ ] Required tests exist and meaningfully cover AC branches.
- [ ] Documentation and status evidence remain consistent with implementation.
- [ ] Live remote canary evidence is present and traceable (or limitation is explicitly justified).

## 2. PR-AA-01 Reader Retention Desire Vector (P0)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-01`.

- [ ] AC-01-1: `RetentionDesireVector` validates each dimension in `[0.0, 1.0]`; dimensions are independent (sum not forced to 1).
- [ ] AC-01-2: `dominant` auto-resolves from max dimension and supports override.
- [ ] AC-01-3: V3 generation control reads `dominant` and maps to hook strategy tags.
- [ ] AC-01-4: Tests cover all four dominant branches.
- [ ] AC-01-5: V3 extension scope is explicitly documented and does not break baseline contract.

Key files to inspect:

- `alpha_autopilot_v3/retention/models.py`
- `alpha_autopilot_v3/generation_control/mapping.py`
- `alpha_autopilot_v3/generation_control/policy.py`
- `backend/app/services/narrative_v2/retention_desire.py`
- `tests/test_retention_desire_vector.py`
- `tests/test_alpha_autopilot_v3_generation_control_desire.py`

## 3. PR-AA-02 Six-Step Plot Unit Scaffold (P0)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-02`.

- [ ] AC-02-1: Frontend supports complete six-step input and serializes to request body.
- [ ] AC-02-2: Backend receives scaffold and injects structured prompt constraints without breaking existing flow.
- [ ] AC-02-3: Scaffold remains optional; empty state is backward-compatible.
- [ ] AC-02-4: `action_climax.turn_type` enum covers all three turn types.
- [ ] AC-02-5: Frontend serialization and backend prompt-injection tests are present.

Key files to inspect:

- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/services/narrative_v2/preview_service.py`
- `ui-react/src/features/v2Workbench/components/ContextRail.tsx`
- `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`
- `ui-react/src/v2Preview.ts`
- `ui-react/src/v2Preview.test.ts`
- `tests/test_narrative_v2_preview_service.py`

## 4. PR-AA-03 Emotion Slider Map (P0)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-03`.

- [ ] AC-03-1: `EmotionSliderMap` is serializable/deserializable with strict value validation.
- [ ] AC-03-2: Missing scene override falls back to baseline values.
- [ ] AC-03-3: Out-of-range slider values (`<-10` or `>10`) raise validation error.
- [ ] AC-03-4: High `stress_baseline` prompt behavior constraints are explicitly injected.
- [ ] AC-03-5: Optional `mbti`/`enneagram` fields do not break existing state logic.
- [ ] AC-03-6: Tests cover baseline/override/boundary scenarios.

Key files to inspect:

- `backend/app/services/narrative_v4/emotion_slider.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/services/narrative_v2/schemas.py`
- `tests/test_emotion_slider_map.py`

## 5. PR-AA-04 Character Function Type Tags (P1)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-04`.

- [ ] AC-04-1: All eight function types are defined and documented.
- [ ] AC-04-2: `DISGUISE` supports dual-layer relation (`surface_relation`, `actual_relation`).
- [ ] AC-04-3: Relation analysis supports `reveal_disguise: bool`.
- [ ] AC-04-4: Existing relation behavior remains unchanged when `function_type` is absent.

Key files to inspect:

- `alpha_autopilot_v4/relations/models.py`
- `alpha_autopilot_v4/relations/analyzer.py`
- `alpha_autopilot_v4/plot_generation/generator.py`
- `alpha_autopilot_v4/integration/bridge.py`
- `tests/test_alpha_autopilot_v4_modules.py`

## 6. PR-AA-05 Character Three-Step Validation Loop (P1)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-05`.

- [ ] AC-05-1: Validation loop is optional and defaults on when `v4_enabled=true`.
- [ ] AC-05-2: Self-inspect emits structured and serializable `IssueList`.
- [ ] AC-05-3: Targeted-fix only mutates issue-listed fields (non-issue fields remain stable).
- [ ] AC-05-4: Empty issue list skips fix stage and avoids extra LLM call path.
- [ ] AC-05-5: End-to-end loop timing/step metrics are logged for rollout observability.

Key files to inspect:

- `backend/app/services/narrative_v4/character_validation.py`
- `backend/app/services/narrative_v4/bridge.py`
- `tests/test_character_validation_loop.py`

## 7. PR-AA-06 Relationship Graph JSON Input (P1)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-06`.

- [ ] AC-06-1: Relationship graph schema is complete and validated (runtime validation + exported JSON Schema artifact).
- [ ] AC-06-2: Backend accepts graph input as optional request field.
- [ ] AC-06-3: `hidden=true` edges are excluded in non-reveal mode.
- [ ] AC-06-4: `chapter_range` filtering excludes out-of-window edges.
- [ ] AC-06-5: Export util exists to generate graph JSON from triple-like storage records.

Key files to inspect:

- `backend/app/services/narrative_v4/relationship_graph.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/services/narrative_v2/schemas.py`
- `tests/test_relationship_graph_input.py`
- `backend/tests/test_narrative_v4_api.py`

## 8. PR-AA-07 Macro Story Structure Selector (P2)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-07`.

- [ ] AC-07-1: `macro_structure` enum has three values and default is `progressive`.
- [ ] AC-07-2: `StoryState` persistence/read path carries `macro_structure`.
- [ ] AC-07-3: V3 generation control adjusts hook weighting by `macro_structure`.
- [ ] AC-07-4: Frontend uses existing context route payload (no new API).

Key files to inspect:

- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/services/narrative_v2/state_builder.py`
- `backend/app/services/narrative_v2/evaluation_service.py`
- `alpha_autopilot_v3/generation_control/policy.py`
- `ui-react/src/features/v2Workbench/components/ContextRail.tsx`
- `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`
- `tests/test_narrative_v2_macro_structure.py`

## 9. PR-AA-08 Prompt Compression Layered Injection (P2)

Evidence anchor: `v5-pr.md` section `Completed: PR-AA-08`.

- [ ] AC-08-1: Auto compression triggers for docs above threshold (`2000` default).
- [ ] AC-08-2: Compression ratio target is configurable and enforced (`<=30%` default).
- [ ] AC-08-3: Core-constraint coverage metric is implemented and testable.
- [ ] AC-08-4: Compression logs include original/compressed token counts and mode.
- [ ] AC-08-5: Per-document disable switch (`compress=false` equivalent) works.

Key files to inspect:

- `backend/app/services/narrative_v4/prompt_compressor.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/core/config.py`
- `tests/test_prompt_compressor.py`

## 10. Cross-Item Risk Review

- [ ] FR-001 alignment: V3/V4 expansion reflected in roadmap/status docs and not treated as baseline mutation.
- [ ] FR-003 observability: Validation/compression runtime metrics are sufficient for gray release gate.
- [ ] FR-004 mitigation: Relationship graph input path provides stable interim context source.
- [ ] FR-005 consistency: Frontend test evidence matches documented status claims.

## 11. Known Residual Risks (Track Explicitly)

- [ ] Compression coverage metric currently approximates semantic fidelity; real-model judge calibration may still be needed.
- [ ] Validation loop metrics and call accounting may be partially simulated in tests; production latency/cost variance needs canary confirmation.

## 12. Final Decision Block

- [ ] `GO` (all P0/P1 pass, no blocking regression)
- [ ] `GO WITH CONDITIONS` (non-blocking P2/P3 debt, tracked with owner and ETA)
- [ ] `NO-GO` (any blocker in P0/P1, rollback path unclear, or observability insufficient)

Reviewer note template:

- Decision:
- Blocking findings:
- Conditional follow-ups:
- Re-test commands executed:
- Evidence links:
