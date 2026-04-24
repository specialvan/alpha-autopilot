# TC-001-02 Sparse Metrics Safety

## Given

- A chapter record with empty checkpoints and minimal structure/style fields.

## When

- Build retention metrics from sparse record.

## Then

- No exception is raised.
- Evidence statuses are `unknown`.
- Numeric outputs stay within `[0, 1]`.

## Command

```powershell
pytest tests/test_alpha_autopilot_v3_retention_metrics.py -q
```
