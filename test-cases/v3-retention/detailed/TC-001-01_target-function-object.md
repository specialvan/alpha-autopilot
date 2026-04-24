# TC-001-01 Target Function Object

## Given

- Retention module is importable.

## When

- Build target function through public constructor.

## Then

- Target object includes stable name, primary objective, priority order, and guardrails.
- Object fields are non-empty and deterministic for repeated calls.

## Command

```powershell
pytest tests/test_alpha_autopilot_v3_pipeline.py tests/test_alpha_autopilot_v3_retention_metrics.py -q
```
