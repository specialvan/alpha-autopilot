# V5 Canary Evidence (2026-04-27)

## 1. Purpose

Record canary-like evidence for newly added external hook contracts in V5:

- Prompt compression external coverage judge path
- Character validation external inspector/fixer path

## 2. Profiles Validated

### Profile A: Default (Heuristic)

- Prompt compression:
  - `coverage_mode_requested`: `heuristic`
  - `coverage_mode_effective`: `heuristic`
- Character validation:
  - `character_validation_mode_requested`: `heuristic`
  - `character_validation_mode_effective`: `heuristic`

### Profile B: Canary (External Hook Injected)

- Prompt compression:
  - `coverage_mode_requested`: `llm_judge`
  - with injected `_prompt_compression_coverage_judge`
  - expected `coverage_mode_effective`: `llm_judge`
- Character validation:
  - `character_validation_mode_requested`: `external`
  - with injected `_character_validation_inspector` / `_character_validation_fixer`
  - expected `character_validation_mode_effective`: `external`

## 3. Evidence Commands

### Live remote LLM canary runner (real traffic)

```bash
python scripts/run_v5_live_llm_canary.py
```

Observed result:

- `PASS`
- report:
  - `artifacts/production_cycles/v5_live_canary/v5-live-llm-canary-20260427T101654Z.md` (pass sample)
  - `artifacts/production_cycles/v5_live_canary/v5-live-llm-canary-20260427T101834Z.md` (pass after retry-hardening)

### Prompt compression contract + bridge observability

```bash
pytest -q tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py
```

Observed result:

- `45 passed`

### Character validation contract + bridge observability

```bash
pytest -q tests/test_character_validation_loop.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py
```

Observed result:

- `44 passed`

### Full regression subset after canary-contract changes

```bash
pytest -q tests/test_retention_desire_vector.py tests/test_alpha_autopilot_v3_generation_control_desire.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py tests/test_narrative_v2_macro_structure.py tests/test_emotion_slider_map.py tests/test_character_validation_loop.py tests/test_relationship_graph_input.py tests/test_prompt_compressor.py tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py
```

Observed result:

- `78 passed`

Frontend regression subset:

```bash
cd ui-react && npm run test -- src/v2Preview.test.ts src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/contextMapping.test.ts
```

Observed result:

- `4 files passed, 15 tests passed`

## 4. Canary Assertions Confirmed

- Prompt compression logs include:
  - `coverage_source`
  - `coverage_mode_requested`
  - `coverage_mode_effective`
- Character validation logs include:
  - `inspector_mode`
  - `fixer_mode`
  - `llm_mode`
  - `mode_requested`
  - `mode_effective`
- Default path remains backward-compatible when no external hook is injected.

## 5. Remaining Limitations

- Current canary evidence validates runtime contracts and observability with injected hook functions in tests.
- Live remote-LLM traffic is now validated through the canary runner and recorded in markdown reports.
- Throughput-scale and long-window stability under sustained production load are not covered by this single-run canary.
