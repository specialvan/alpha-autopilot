# TC-005-01 Layer Gate Integrity

## Given

- Layered test runner with quality/api/import groups.

## When

- Resolve and execute layered commands.

## Then

- Required V3 and workbench gate tests are present in layer definitions.
- Unknown layer names fail fast.
- Windows frontend invocation uses `npm.cmd`.

## Command

```powershell
pytest tests/test_run_layered_tests.py -q
python scripts/run_layered_tests.py quality api import
```
