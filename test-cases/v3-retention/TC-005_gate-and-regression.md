# TC-005 Gate And Regression

## Objective

Lock governance gate behavior so required test suites cannot silently drop from layered execution.

## Preconditions

- Layer script present: `scripts/run_layered_tests.py`.
- Layer script tests present: `tests/test_run_layered_tests.py`.

## Test Inputs

1. Layer selection: `quality`, `api`, `import`.
2. Unknown layer name.
3. Windows npm execution path.

## Assertions

1. Layer command lists include required V3 gate tests:
   - `tests/test_alpha_autopilot_v3_build_script.py`
   - `tests/test_alpha_autopilot_v3_qc_report.py`
   - `tests/test_alpha_autopilot_v3_retention_metrics.py`
   - `tests/test_narrative_v2_decision_contract.py`
   - `tests/test_narrative_v2_workbench_quality_enrichment.py`
2. Unknown layer fails fast with explicit error.
3. Frontend layer uses `npm.cmd` on Windows.
4. Script exits non-zero when any layer fails.

## Automated Coverage

- `tests/test_run_layered_tests.py`
- `scripts/run_layered_tests.py`
