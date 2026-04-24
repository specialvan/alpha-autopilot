# TC-003 Pipeline And Bridge

## Objective

Validate decomposition output, projection artifacts, and training bridge integration are consistent and non-duplicative.

## Preconditions

- Build script available: `scripts/build_v3_reverse_decomposition_records.py`.
- Projection bridge available: `backend/app/services/narrative/v3_projection_bridge.py`.
- Training service available: `backend/app/services/narrative/training_service.py`.

## Test Inputs

1. PlotPilot report fixture with one valid chapter.
2. Matrix projection fixture with approved/provisional records.
3. File-only repository mode for training log persistence.

## Assertions

1. Build script emits `reverse_outline_records.jsonl`, `matrix_projection.json`, and `qc_report.json`.
2. Projection bridge maps records into training samples with expected stage/action/signals.
3. Training service loads projection samples and reports projection source.
4. Training log persistence has no duplicate write amplification.
5. Version registry is created in the configured store root.

## Automated Coverage

- `tests/test_alpha_autopilot_v3_build_script.py`
- `tests/test_narrative_v3_projection_bridge.py`
- `tests/test_narrative_training_service_projection.py`
