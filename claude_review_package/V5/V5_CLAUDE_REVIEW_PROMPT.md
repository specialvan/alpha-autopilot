# V5 Claude Full Review Prompt (Copy-Paste Ready)

## 1. Review Goal

You are reviewing `alpha-autopilot` V5 as a production-grade engineering delivery, not an MVP/prototype pass.

Please run a strict requirement-to-implementation audit for `PR-AA-01` to `PR-AA-08`, and decide whether each item is truly shippable under current governance.

## 2. Authoritative Inputs

- Requirement source:
  - `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`
- Implementation + verification source of truth:
  - `claude_review_package/V5/v5-pr.md`
- Governance constraints:
  - `claude_review_package/CODEX_DEVELOPMENT_GOVERNANCE.md`
  - `claude_review_package/README_FOR_CODEX.md`

Do not treat summary claims as accepted facts. Validate them against code and tests.

## 3. Scope

Audit all 8 PR requirements end-to-end:

- `PR-AA-01` Reader retention desire vector
- `PR-AA-02` Six-step plot unit scaffold
- `PR-AA-03` Emotion slider map
- `PR-AA-04` Character function type tags
- `PR-AA-05` Character validation loop
- `PR-AA-06` Relationship graph JSON input
- `PR-AA-07` Macro story structure selector
- `PR-AA-08` Prompt compression layered injection

## 4. Review Method (Required)

1. Requirement mapping
   - For each PR, map every AC item from requirements doc to concrete implementation evidence.
2. Code-level verification
   - Verify schema/enum constraints, fallback logic, compatibility behavior, and observability fields.
3. Test-level verification
   - Confirm tests exist for each critical AC branch and verify they assert the intended behavior (not just happy paths).
4. Governance checks
   - Confirm layer boundaries (`Baseline` vs `Increment`) and rollback/disable paths for new V4/V5 behaviors.
5. Production readiness checks
   - Confirm failure-path resilience, config defaults, and monitoring signals are sufficient for staged rollout.

## 5. Output Format (Strict)

Please return exactly these sections:

1. `Overall Verdict`
   - `PASS` / `PASS WITH CONDITIONS` / `FAIL`
   - One-paragraph rationale.
2. `PR-by-PR Acceptance Matrix`
   - Table columns:
     - `PR`
     - `AC Coverage`
     - `Evidence`
     - `Risk Level (P0-P3)`
     - `Acceptance Decision`
3. `Findings (Ordered by Severity)`
   - Group by `P0`, `P1`, `P2`, `P3`.
   - Each finding must include:
     - file path
     - line reference
     - impact
     - minimal fix recommendation
4. `Residual Risks`
   - Include risks that are not hard blockers but should be tracked in next cycle.
5. `Go/No-Go Recommendation`
   - Recommend merge gate decision for V5 and list mandatory actions before next stage.

## 6. Additional Focus Points

- Backward compatibility:
  - Optional fields should not break existing V2/V3/V4 request flows.
- Character validation loop:
  - Must be bypassable when disabled.
  - Must not mutate non-issue fields during targeted fix.
- Prompt compression:
  - Must have safe fallback path when compression fails.
  - Metrics must be useful for canary/gray rollout monitoring.
- Relationship graph input:
  - Hidden/chapter-range filtering correctness is required.

## 7. Known Residual Risks to Re-check

- Compression quality coverage metric realism:
  - Current implementation may rely on deterministic heuristics rather than true semantic judge quality.
- Validation loop runtime realism:
  - Some LLM call-count and timing paths may still be simulated in tests and need real integration confidence.

## 8. Verification Commands (Optional but Recommended)

- Backend regression subset (from source of truth):
  - `pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Frontend regression subset:
  - `cd ui-react && npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts`

If command reruns are not possible in your environment, explicitly state that as a limitation.
