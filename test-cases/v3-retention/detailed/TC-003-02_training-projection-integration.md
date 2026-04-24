# TC-003-02 Training Projection Integration

## Given

- Projection records exist and training service is configured with projection paths.
- File-only repository scenario is available.

## When

- Execute training service.

## Then

- Projection samples are included in training count.
- Projection source is reported.
- Training log is not duplicated by dual writers.

## Command

```powershell
pytest tests/test_narrative_training_service_projection.py tests/test_narrative_v3_projection_bridge.py -q
```
