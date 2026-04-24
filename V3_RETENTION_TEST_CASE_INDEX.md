# V3 Retention Test Case Index

This file decomposes `V3_RETENTION_IMPLEMENTATION_TEST_PLAN.md` into executable test case documents.

## Case Files

1. `test-cases/v3-retention/TC-001_retention-core.md`
2. `test-cases/v3-retention/TC-002_generation-control.md`
3. `test-cases/v3-retention/TC-003_pipeline-and-bridge.md`
4. `test-cases/v3-retention/TC-004_workbench-and-api-resilience.md`
5. `test-cases/v3-retention/TC-005_gate-and-regression.md`

## Detailed Case Files (Given/When/Then)

1. `test-cases/v3-retention/detailed/TC-001-01_target-function-object.md`
2. `test-cases/v3-retention/detailed/TC-001-02_sparse-metrics-safety.md`
3. `test-cases/v3-retention/detailed/TC-002-01_decision-contract-branches.md`
4. `test-cases/v3-retention/detailed/TC-002-02_ui-decision-fallback.md`
5. `test-cases/v3-retention/detailed/TC-003-01_build-script-artifacts.md`
6. `test-cases/v3-retention/detailed/TC-003-02_training-projection-integration.md`
7. `test-cases/v3-retention/detailed/TC-004-01_imported-context-corruption-fallback.md`
8. `test-cases/v3-retention/detailed/TC-004-02_preview-ledger-best-effort.md`
9. `test-cases/v3-retention/detailed/TC-004-03_frontend-stale-response-guard.md`
10. `test-cases/v3-retention/detailed/TC-005-01_layer-gate-integrity.md`

## Automation Mapping

- `TC-001`:
  - `tests/test_alpha_autopilot_v3_retention_metrics.py`
  - `tests/test_alpha_autopilot_v3_pipeline.py`
- `TC-002`:
  - `tests/test_alpha_autopilot_v3_pipeline.py`
  - `tests/test_narrative_v2_decision_contract.py`
- `TC-003`:
  - `tests/test_alpha_autopilot_v3_build_script.py`
  - `tests/test_narrative_training_service_projection.py`
  - `tests/test_narrative_v3_projection_bridge.py`
- `TC-004`:
  - `tests/test_narrative_v2_preview_service.py`
  - `tests/test_narrative_v2_api.py`
  - `tests/test_narrative_v2_imported_contexts.py`
  - `tests/test_narrative_v2_workbench_context_api.py`
  - `tests/test_narrative_v2_workbench_quality_enrichment.py`
  - `ui-react/src/pages/V2WorkbenchPage.test.tsx`
  - `ui-react/src/features/v2Workbench/backendContexts.test.ts`
- `TC-005`:
  - `tests/test_run_layered_tests.py`
  - `scripts/run_layered_tests.py`
  - `tests/test_alpha_autopilot_v2_validation_ledger.py`

## Detailed Mapping

- `TC-001-01`:
  - `tests/test_alpha_autopilot_v3_pipeline.py`
  - `tests/test_alpha_autopilot_v3_retention_metrics.py`
- `TC-001-02`:
  - `tests/test_alpha_autopilot_v3_retention_metrics.py`
- `TC-002-01`:
  - `tests/test_narrative_v2_decision_contract.py`
- `TC-002-02`:
  - `ui-react/src/pages/V2WorkbenchPage.test.tsx`
- `TC-003-01`:
  - `tests/test_alpha_autopilot_v3_build_script.py`
  - `tests/test_alpha_autopilot_v3_qc_report.py`
- `TC-003-02`:
  - `tests/test_narrative_training_service_projection.py`
  - `tests/test_narrative_v3_projection_bridge.py`
- `TC-004-01`:
  - `tests/test_narrative_v2_imported_contexts.py`
  - `tests/test_narrative_v2_workbench_context_api.py`
  - `tests/test_narrative_v2_workbench_quality_enrichment.py`
- `TC-004-02`:
  - `tests/test_narrative_v2_preview_service.py`
  - `tests/test_narrative_v2_api.py`
- `TC-004-03`:
  - `ui-react/src/pages/V2WorkbenchPage.test.tsx`
  - `ui-react/src/features/v2Workbench/backendContexts.test.ts`
- `TC-005-01`:
  - `tests/test_run_layered_tests.py`
  - `scripts/run_layered_tests.py`

## Execution Order

1. `python scripts/run_layered_tests.py quality api import`
2. `pytest tests/test_alpha_autopilot_v3_pipeline.py tests/test_alpha_autopilot_v3_retention_metrics.py tests/test_narrative_training_service_projection.py -q`
3. `npm test -- --run src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts`
