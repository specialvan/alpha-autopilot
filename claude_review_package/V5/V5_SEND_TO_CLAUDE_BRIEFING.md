# V5 Send-to-Claude Briefing (Full Review)

## 1. 使用说明

目标：对 `alpha-autopilot` V5 做全量功能需求评审（AA-01 ~ AA-08），按生产级工程标准验收，不按原型标准放行。

推荐投喂方式：

1. 将本文件内容整体发送给 Claude。
2. 同时附上以下文件作为评审输入。
3. 要求 Claude 严格按“输出格式”返回结论，不省略分级问题与 Go/No-Go 判定。

## 2. 必带输入文件

- `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`
- `claude_review_package/V5/v5-pr.md`
- `claude_review_package/V5/V5_CLAUDE_REVIEW_CHECKLIST.md`
- `claude_review_package/CODEX_DEVELOPMENT_GOVERNANCE.md`
- `claude_review_package/README_FOR_CODEX.md`

可选（建议一并提供，便于 Claude 对差异点复核）：

- `claude_review_package/V5/V5_CODEX_INTERNAL_PRE_ACCEPTANCE_2026_04_27.md`
- `claude_review_package/V5/V5_CONDITION_CLOSURE_TASK_BOARD.md`
- `claude_review_package/V5/V5_CANARY_EVIDENCE_2026_04_27.md`
- `artifacts/production_cycles/v5_live_canary/v5-live-llm-canary-20260427T101834Z.md`

## 3. Claude 评审主提示词（可直接复制）

You are reviewing `alpha-autopilot` V5 as a production-grade engineering delivery, not an MVP/prototype pass.

Please run a strict requirement-to-implementation audit for `PR-AA-01` to `PR-AA-08`, and decide whether each item is truly shippable under current governance.

Authoritative inputs:
- `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`
- `claude_review_package/V5/v5-pr.md` (source of truth for implementation/test evidence)
- `claude_review_package/V5/V5_CLAUDE_REVIEW_CHECKLIST.md`
- `claude_review_package/CODEX_DEVELOPMENT_GOVERNANCE.md`
- `claude_review_package/README_FOR_CODEX.md`

Scope:
- `PR-AA-01` Reader retention desire vector
- `PR-AA-02` Six-step plot unit scaffold
- `PR-AA-03` Emotion slider map
- `PR-AA-04` Character function type tags
- `PR-AA-05` Character validation loop
- `PR-AA-06` Relationship graph JSON input
- `PR-AA-07` Macro story structure selector
- `PR-AA-08` Prompt compression layered injection

Required review method:
1. Requirement mapping: map every AC item to concrete implementation evidence.
2. Code verification: verify constraints, fallback behavior, compatibility, and observability.
3. Test verification: verify coverage quality for AC branches, not only happy paths.
4. Governance verification: verify layer boundaries and rollback/disable readiness.
5. Production readiness: verify failure resilience, config defaults, and rollout monitoring value.

Return format (strict):
1. Overall Verdict (`PASS` / `PASS WITH CONDITIONS` / `FAIL`) with one-paragraph rationale.
2. PR-by-PR Acceptance Matrix with columns:
   - `PR`
   - `AC Coverage`
   - `Evidence`
   - `Risk Level (P0-P3)`
   - `Acceptance Decision`
3. Findings (ordered by severity `P0` -> `P3`), each with:
   - file path
   - line reference
   - impact
   - minimal fix recommendation
4. Residual Risks (non-blocking but must-track items)
5. Go/No-Go Recommendation (with mandatory pre-merge actions)

Focus points:
- Optional-field backward compatibility in V2/V3/V4 request flow.
- Character validation loop bypass behavior and mutation boundaries.
- Prompt compression fallback correctness and monitoring usability.
- Relationship graph hidden/chapter-range filtering correctness.

Known residual risks to re-check:
- Compression coverage metric supports pluggable judge and rollout telemetry (`coverage_source`, `coverage_mode_requested`, `coverage_mode_effective`), but production may still run heuristic path by default.
- Validation loop supports pluggable external inspector/fixer and rollout telemetry (`mode_requested`, `mode_effective`), but production may still run heuristic path by default.
- Relationship graph now exports JSON Schema artifact; confirm reviewer checks both schema artifact and runtime filtering behavior together.

Live remote canary utility:
- `python scripts/run_v5_live_llm_canary.py`

Optional verification commands:
- Backend:
  `pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Frontend:
  `cd ui-react && npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts`

If reruns are not possible, explicitly state this limitation.

## 4. 对照清单入口

- 详细逐条 AC 核对请使用：
  - `claude_review_package/V5/V5_CLAUDE_REVIEW_CHECKLIST.md`

## 5. 证据口径

实现与测试证据以以下文件为统一来源：

- `claude_review_package/V5/v5-pr.md`

若评审发现与源码或测试现状不一致，必须以源码与测试实际结果为准，并在 Findings 中明确指出差异。
