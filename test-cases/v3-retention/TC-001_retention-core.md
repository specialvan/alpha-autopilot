# TC-001 Retention Core

## Objective

Validate retention target and metric computation are stable, bounded, and robust for sparse input.

## Preconditions

- V3 retention modules available:
  - `alpha_autopilot_v3/retention/models.py`
  - `alpha_autopilot_v3/retention/metrics.py`
  - `alpha_autopilot_v3/retention/target_function.py`

## Test Inputs

1. Normal chapter record with populated checkpoints.
2. Sparse record with empty checkpoints and minimal structure/style.

## Assertions

1. Scores are bounded in `[0, 1]`.
2. `chapter_attraction_score`, `continue_reading_intent`, `template_risk` are always computable.
3. Sparse record does not raise exception.
4. Evidence fields return `"unknown"` when checkpoints are absent.

## Automated Coverage

- `tests/test_alpha_autopilot_v3_retention_metrics.py`
- `tests/test_alpha_autopilot_v3_pipeline.py`
