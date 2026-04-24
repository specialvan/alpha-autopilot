# TC-004-02 Preview Ledger Best Effort

## Given

- Preview endpoint with an invalid ledger write target.

## When

- Submit preview request.

## Then

- API still returns `200` with decision payload.
- Response includes `ledger_warning`.

## Command

```powershell
pytest tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_api.py -q
```
