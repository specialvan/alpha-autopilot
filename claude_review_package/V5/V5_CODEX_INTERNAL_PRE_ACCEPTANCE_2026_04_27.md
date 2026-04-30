# V5 Codex Internal Pre-Acceptance Report

## 1. Metadata

- Review date: 2026-04-27 (Asia/Shanghai)
- Reviewer: Codex (internal pre-check)
- Scope: `PR-AA-01` ~ `PR-AA-08`
- Requirement baseline: `claude_review_package/V5/alpha_autopilot_PR_requirements.docx`
- Implementation evidence baseline: `claude_review_package/V5/v5-pr.md`

## 2. Fresh Verification Evidence

### Backend regression subset

Command:

```bash
pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py
```

Result:

- `78 passed in 0.65s`

### Frontend regression subset

Command:

```bash
cd ui-react && npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts
```

Result:

- `4 passed (files), 15 passed (tests)`

## 3. Overall Verdict

- Verdict: `PASS`
- Rationale: All required regression commands passed on 2026-04-27 with no P0/P1 blockers. External hook contracts (prompt compression + character validation) are implemented with requested/effective mode telemetry, and live remote LLM canary now passes with recorded runtime evidence.

## 4. PR-by-PR Acceptance Matrix

| PR | AC Coverage | Evidence | Risk Level | Decision |
| --- | --- | --- | --- | --- |
| PR-AA-01 | Covered | `backend/app/services/narrative_v2/retention_desire.py`, `alpha_autopilot_v3/generation_control/mapping.py`, `tests/test_retention_desire_vector.py`, `tests/test_alpha_autopilot_v3_generation_control_desire.py` | P1 | Pass |
| PR-AA-02 | Covered | `backend/app/services/narrative_v2/schemas.py`, `backend/app/services/narrative_v2/preview_service.py`, `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`, `ui-react/src/features/v2Workbench/components/ContextRail.tsx`, `ui-react/src/v2Preview.test.ts` | P1 | Pass |
| PR-AA-03 | Covered | `backend/app/services/narrative_v4/emotion_slider.py`, `backend/app/services/narrative_v4/bridge.py`, `tests/test_emotion_slider_map.py` | P1 | Pass |
| PR-AA-04 | Covered | `alpha_autopilot_v4/relations/models.py`, `alpha_autopilot_v4/relations/analyzer.py`, `tests/test_alpha_autopilot_v4_modules.py` | P1 | Pass |
| PR-AA-05 | Covered (pluggable external inspector/fixer added) | `backend/app/services/narrative_v4/character_validation.py`, `backend/app/services/narrative_v4/bridge.py`, `tests/test_character_validation_loop.py` | P1 | Pass with condition |
| PR-AA-06 | Covered (JSON Schema artifact exported) | `backend/app/services/narrative_v4/relationship_graph.py`, `backend/app/services/narrative_v4/__init__.py`, `backend/app/services/narrative_v4/bridge.py`, `tests/test_relationship_graph_input.py` | P1 | Pass |
| PR-AA-07 | Covered | `backend/app/services/narrative_v2/schemas.py`, `backend/app/services/narrative_v2/state_builder.py`, `backend/app/services/narrative_v2/evaluation_service.py`, `alpha_autopilot_v3/generation_control/policy.py`, `tests/test_narrative_v2_macro_structure.py`, `ui-react/src/pages/V2WorkbenchPage.test.tsx` | P1 | Pass |
| PR-AA-08 | Covered (pluggable LLM judge + coverage source + requested/effective mode logs) | `backend/app/services/narrative_v4/prompt_compressor.py`, `backend/app/services/narrative_v4/bridge.py`, `backend/app/core/config.py`, `tests/test_prompt_compressor.py` | P1 | Pass with condition |

## 5. Findings (Ordered by Severity)

### P3

- Finding: AC-08-3 now supports pluggable external judge (`coverage_judge`) plus `coverage_mode_requested/effective`, but production rollout policy still needs canary evidence before full enablement.
- File: `backend/app/services/narrative_v4/prompt_compressor.py`
- Line: around `10-21`, `54-70`, `90-117`
- Impact: Semantic fidelity confidence and cost profile need measured canary data under real workload.
- Minimal fix: run canary with explicit judge adapter and record latency/cost/coverage deltas.

- Finding: AC-05 now supports external inspector/fixer hooks and mode logging (`external_judge`, `external_fixer`, `llm_mode`), but default bridge path remains heuristic unless external implementation is injected.
- File: `backend/app/services/narrative_v4/character_validation.py`
- Line: around `20-59`
- Impact: Production latency/cost profile is still estimated unless external hooks are enabled in runtime.
- Minimal fix: Register external inspector/fixer in deployment profile and monitor latency/cost against target SLO.

## 6. Residual Risks

- Compression quality metric now has source tagging (`heuristic` / `heuristic_fallback` / `llm_judge`), but production judge enablement still needs explicit rollout policy.
- Validation loop now supports external inspector/fixer hooks, but real LLM latency/cost variance still needs canary evidence.

## 7. Go/No-Go Recommendation

- Decision: `GO`
- Mandatory actions before final production gate:
  1. Keep `scripts/run_v5_live_llm_canary.py` in release checklist as pre-merge smoke gate.
