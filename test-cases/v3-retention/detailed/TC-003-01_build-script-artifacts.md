# TC-003-01 Build Script Artifacts

## Given

- A minimal PlotPilot report fixture.

## When

- Execute V3 build script.

## Then

- `reverse_outline_records.jsonl`, `matrix_projection.json`, and `qc_report.json` are emitted.
- QC report contains expected schema and counts.

## Command

```powershell
pytest tests/test_alpha_autopilot_v3_build_script.py tests/test_alpha_autopilot_v3_qc_report.py -q
```
