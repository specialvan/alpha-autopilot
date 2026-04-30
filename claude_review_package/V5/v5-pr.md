# alpha-autopilot V5 PR Execution Log

## Progress Snapshot

- Date: 2026-04-27
- Branch target: `codex/history-review`
- Source spec: `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`

## Requirement Status

- [x] PR-AA-01 (P0) Reader retention desire vector extension
- [x] PR-AA-02 (P0) Six-step plot unit scaffold
- [x] PR-AA-03 (P0) Emotion slider map
- [x] PR-AA-04 (P1) Character function type tags
- [x] PR-AA-05 (P1) Character validation loop
- [x] PR-AA-06 (P1) Relationship graph JSON input
- [x] PR-AA-07 (P2) Macro story structure selector
- [x] PR-AA-08 (P2) Prompt compression layered injection

## Completed: PR-AA-01

### What was implemented

- Added `RetentionDesireVector` domain model in V3 retention module with dominant auto-resolution and override support.
- Added backend Pydantic contract model `RetentionDesireVector` with validation range `[0.0, 1.0]`.
- Extended V3 generation control mapping to read `dominant` and map it to hook strategies.
- Exposed desire-driven strategy via `decision_tags` and `suggestions`.
- Added optional request compatibility in V2 story payload/state builder (`retention_desire` optional).

### Changed files

- `alpha_autopilot_v3/retention/models.py`
- `alpha_autopilot_v3/retention/__init__.py`
- `alpha_autopilot_v3/generation_control/mapping.py`
- `alpha_autopilot_v3/generation_control/policy.py`
- `alpha_autopilot_v3/decomposition/pipeline.py`
- `alpha_autopilot_v3/__init__.py`
- `backend/app/services/narrative_v2/retention_desire.py`
- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/services/narrative_v2/state_builder.py`
- `alpha_autopilot_v2/domain/story.py`
- `tests/test_retention_desire_vector.py`
- `tests/test_alpha_autopilot_v3_generation_control_desire.py`

### Verification evidence

- `pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_alpha_autopilot_v3_pipeline.py tests/test_narrative_v2_preview_service.py`
- Result: `12 passed`

## Completed: PR-AA-02

### What was implemented

- Added `PlotUnitScaffold` contract to V2 preview request, including six-step fields and `action_climax.turn_type` enum with three values.
- Added backend prompt-constraint injection: scaffold transforms into a structured system prompt paragraph (`system_prompt_constraints`).
- Added V2 Workbench UI panel with six-step inputs and turn type selector.
- Added request serialization path so scaffold is sent only when all six steps are filled (backward compatible when empty).

### Changed files

- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/services/narrative_v2/preview_service.py`
- `ui-react/src/api.ts`
- `ui-react/src/v2Preview.ts`
- `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`
- `ui-react/src/features/v2Workbench/components/ContextRail.tsx`
- `tests/test_narrative_v2_preview_service.py`
- `ui-react/src/v2Preview.test.ts`

### Verification evidence

- `pytest -q tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_decision_contract.py`
- Result: `10 passed`
- `npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx` (cwd=`ui-react`)
- Result: `2 files passed, 9 tests passed`

## Completed: PR-AA-03

### What was implemented

- Added `EmotionSliderMap` model with Pydantic validation for `baseline` and `scene_overrides` in range `[-10, 10]`.
- Added scene-level merge logic (`baseline + scene_overrides`) with fallback to baseline when override missing.
- Added optional `mbti` and `enneagram` anchors (non-breaking optional fields).
- Added character behavior prompt-constraint injection in V4 bridge payload, including explicit high-stress behavior text when `stress_baseline > 5`.
- Added behavior constraint metadata into V4 workbench preview and memory summary counters.

### Changed files

- `backend/app/services/narrative_v4/emotion_slider.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/services/narrative_v4/__init__.py`
- `backend/app/services/narrative_v2/schemas.py`
- `ui-react/src/api.ts`
- `tests/test_emotion_slider_map.py`
- `tests/test_alpha_autopilot_v4_modules.py`
- `backend/tests/test_narrative_v4_api.py`

### Verification evidence

- `pytest -q tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `35 passed`
- `pytest -q tests/test_emotion_slider_map.py`
- Result: `5 passed` (covered via full run + focused model tests)

## Completed: PR-AA-04

### What was implemented

- Added `CharacterFunctionType` enum with 8 function categories in the V4 relation model.
- Added dual-layer relation handling for disguise roles:
  - `surface_relation`
  - `actual_relation`
- Extended relation analysis API to accept `reveal_disguise: bool`.
- Added relation layer and relation hint metadata into relation profiles, displacement events, and bridge payload exports.
- Preserved backward compatibility: when `function_type` is missing, relation analysis behavior remains unchanged.

### Changed files

- `alpha_autopilot_v4/relations/models.py`
- `alpha_autopilot_v4/relations/analyzer.py`
- `alpha_autopilot_v4/relations/__init__.py`
- `alpha_autopilot_v4/plot_generation/generator.py`
- `alpha_autopilot_v4/integration/bridge.py`
- `tests/test_alpha_autopilot_v4_modules.py`

### Verification evidence

- `pytest -q tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `37 passed`

## Completed: PR-AA-05

### What was implemented

- Added V4 `CharacterValidationLoop` with explicit three-step flow:
  1. Generate (normalize generated character payload)
  2. Self-Inspect (produce structured `IssueList`)
  3. Targeted-Fix (apply only issue-specific field updates)
- Made validation loop optional with runtime switch:
  - defaults enabled when `v4_enabled=true`
  - bypassed when `v4_enabled=false` or explicit disable flag
- Added runtime observability fields:
  - issue count
  - per-step simulated LLM call counts
  - elapsed milliseconds
- Injected validation logs into V4 bridge payload and memory summary for T05 monitoring.

### Changed files

- `backend/app/services/narrative_v4/character_validation.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/services/narrative_v2/schemas.py`
- `ui-react/src/api.ts`
- `tests/test_character_validation_loop.py`

### Verification evidence

- `pytest -q tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `41 passed`

## Completed: PR-AA-06

### What was implemented

- Added structured relationship graph input contract with schema validation:
  - `characters`
  - `edges[]` with `from/to/relation_type/intensity/bidirectional/hidden/chapter_range`
- Added hidden edge filtering (`hidden=true` excluded unless reveal mode enabled).
- Added chapter range filtering (`chapter_range` outside current chapter auto-excluded).
- Wired filtered graph edges into V4 relationship context as relationship history rows.
- Added bridge payload + memory summary observability for graph filtering counts.
- Added util to export relationship graph JSON from existing triple-like records.

### Changed files

- `backend/app/services/narrative_v4/relationship_graph.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/services/narrative_v4/__init__.py`
- `backend/app/services/narrative_v2/schemas.py`
- `ui-react/src/api.ts`
- `tests/test_relationship_graph_input.py`
- `backend/tests/test_narrative_v4_api.py`

### Verification evidence

- `pytest -q tests/test_relationship_graph_input.py tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `46 passed`

## Completed: PR-AA-07

### What was implemented

- Added `macro_structure` enum (`progressive` / `hub_and_spoke` / `anthology`) into V2 story state contracts and builder flow.
- Added Workbench UI selector for macro structure using existing preview route payload (no new API).
- Persisted `macro_structure` through state objects and preview payloads.
- Added macro-structure weighting logic in recommendation evaluation priority weights.
- Added V3 generation control hook-weight adaptation tags (`macro_hook_weight`) for macro structure.

### Changed files

- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/services/narrative_v2/state_builder.py`
- `backend/app/services/narrative_v2/evaluation_service.py`
- `alpha_autopilot_v3/generation_control/policy.py`
- `alpha_autopilot_v3/decomposition/pipeline.py`
- `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`
- `ui-react/src/features/v2Workbench/components/ContextRail.tsx`
- `ui-react/src/pages/V2WorkbenchPage.test.tsx`
- `tests/test_narrative_v2_macro_structure.py`
- `tests/test_alpha_autopilot_v3_generation_control_desire.py`

### Verification evidence

- `pytest -q tests/test_narrative_v2_macro_structure.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py`
- Result: `13 passed`
- `npm run test -- src/pages/V2WorkbenchPage.test.tsx src/v2Preview.test.ts` (cwd=`ui-react`)
- Result: `2 files passed, 10 tests passed`

## Completed: PR-AA-08

### What was implemented

- Added `PromptCompressor` utility with:
  - auto-trigger threshold (`2000` token default)
  - compression modes (`bullet` / `headline`)
  - compression ratio target (default `<= 30%`)
  - fallback behavior on compression failure
  - per-document coverage signal logging
- Integrated prompt compression into V4 bridge for long prompt documents:
  - `style_document`
  - `character_profile_document`
  - `world_setting_document`
  - `core_instruction_document` passthrough (no compression)
- Added runtime logs and summary metrics:
  - original/compressed token counts
  - mode
  - triggered/fallback flags
  - per-document compression enable switch
- Added `compress_prompt_docs` toggle and configurable settings via `Settings`.

### Changed files

- `backend/app/services/narrative_v4/prompt_compressor.py`
- `backend/app/services/narrative_v4/bridge.py`
- `backend/app/core/config.py`
- `backend/app/services/narrative_v2/schemas.py`
- `ui-react/src/api.ts`
- `tests/test_prompt_compressor.py`

### Verification evidence

- `pytest -q tests/test_prompt_compressor.py tests/test_relationship_graph_input.py tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `50 passed`
- `npm run test -- src/pages/V2WorkbenchPage.test.tsx src/v2Preview.test.ts` (cwd=`ui-react`)
- Result: `2 files passed, 10 tests passed`

## Final Verification Bundle

- Backend/Domain regression subset:
  - `pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
  - Result: `72 passed`
- Frontend regression subset:
  - `npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts`
  - Result: `4 files passed, 15 tests passed`

## Post-Review Hardening (2026-04-27)

### Hardening A: Prompt compression coverage source + pluggable judge

#### What was implemented

- Added `coverage_judge` injection point in `PromptCompressor` for external judge integration.
- Added explicit `coverage_source` in compression output:
  - `llm_judge`
  - `heuristic`
  - `heuristic_fallback`
  - `passthrough`
  - `fallback_passthrough`
- Added `coverage_source` propagation into V4 bridge compression logs for rollout observability.

#### Changed files

- `backend/app/services/narrative_v4/prompt_compressor.py`
- `backend/app/services/narrative_v4/bridge.py`
- `tests/test_prompt_compressor.py`

#### Verification evidence

- `pytest -q tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `44 passed`

### Hardening B: Character validation loop pluggable inspector/fixer

#### What was implemented

- Added `inspector` and `fixer` hook injection points in `run_character_validation_loop`.
- Added runtime mode observability fields:
  - `inspector_mode` (`heuristic` / `external_judge`)
  - `fixer_mode` (`deterministic_patch` / `external_fixer` / `skipped`)
  - `llm_mode` (`simulated` / `external`)
- Kept backward compatibility of existing flow and call accounting.

#### Changed files

- `backend/app/services/narrative_v4/character_validation.py`
- `tests/test_character_validation_loop.py`

#### Verification evidence

- `pytest -q tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `43 passed`

### Refreshed final verification (after hardening)

- Backend/Domain regression subset:
  - `pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
  - Result: `78 passed`
- Frontend regression subset:
  - `npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts`
  - Result: `4 files passed, 15 tests passed`

### Hardening C: Relationship graph JSON schema artifact

#### What was implemented

- Added exported JSON Schema generator:
  - `relationship_graph_json_schema()`
  - backed by `RelationshipGraphInput.model_json_schema(by_alias=True)`
- Exposed schema helper in V4 service package exports.
- Added test coverage to assert JSON Schema artifact contains key contract fields (`relation_type`, `chapter_range`) and allowed relation enum content.

#### Changed files

- `backend/app/services/narrative_v4/relationship_graph.py`
- `backend/app/services/narrative_v4/__init__.py`
- `tests/test_relationship_graph_input.py`

#### Verification evidence

- `pytest -q tests/test_relationship_graph_input.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `43 passed`

### Hardening D: Coverage mode rollout contract for prompt compression

#### What was implemented

- Added config contract:
  - `v4_prompt_compress_coverage_mode` (default `heuristic`)
- Added bridge-level requested/effective mode telemetry:
  - `coverage_mode_requested`
  - `coverage_mode_effective`
- Added canary injection path for explicit coverage judge during controlled rollout:
  - context key `_prompt_compression_coverage_judge` (callable hook)
- Preserved backward compatibility: default path remains heuristic without external dependency.

#### Changed files

- `backend/app/core/config.py`
- `backend/app/services/narrative_v4/bridge.py`
- `tests/test_prompt_compressor.py`

#### Verification evidence

- `pytest -q tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `45 passed`

### Hardening E: Character validation mode rollout contract

#### What was implemented

- Added config contract:
  - `v4_character_validation_mode` (default `heuristic`)
- Added bridge-level requested/effective mode telemetry:
  - `character_validation_mode_requested`
  - `character_validation_mode_effective`
- Added canary injection path for explicit external validation hooks:
  - context key `_character_validation_inspector` (callable hook)
  - context key `_character_validation_fixer` (callable hook)
- Added `mode_requested` and `mode_effective` into validation log payload.

#### Changed files

- `backend/app/core/config.py`
- `backend/app/services/narrative_v4/bridge.py`
- `tests/test_character_validation_loop.py`

#### Verification evidence

- `pytest -q tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py`
- Result: `44 passed`

### Canary Evidence Artifact

- Added contract-level canary evidence package:
  - `claude_review_package/V5/V5_CANARY_EVIDENCE_2026_04_27.md`
- Captures default vs external-hook mode behavior and refreshed regression outcomes.

### Hardening F: Live remote LLM canary runner

#### What was implemented

- Added executable live canary runner:
  - `scripts/run_v5_live_llm_canary.py`
- Canary runner validates real remote calls for:
  - prompt compression coverage judge (`coverage_source=llm_judge`)
  - character validation external inspector path (`inspector_mode=external_judge`)
- Added endpoint retry hardening for transient network errors.
- Added markdown evidence output under:
  - `artifacts/production_cycles/v5_live_canary/`

#### Changed files

- `scripts/run_v5_live_llm_canary.py`
- `backend/app/core/config.py` (added `benchmark_base_url`)

#### Verification evidence

- `python scripts/run_v5_live_llm_canary.py`
- Result: `PASS`
- Report examples:
  - `artifacts/production_cycles/v5_live_canary/v5-live-llm-canary-20260427T101654Z.md`
  - `artifacts/production_cycles/v5_live_canary/v5-live-llm-canary-20260427T101834Z.md`
