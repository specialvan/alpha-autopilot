# TC-004-01 Imported Context Corruption Fallback

## Given

- Corrupted `workbench_contexts.json` or corrupted sibling quality JSONL.

## When

- Call workbench contexts API.

## Then

- API returns live fallback context instead of raising exception.
- Corrupted quality enrichment does not break imported context listing.

## Command

```powershell
pytest tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_workbench_quality_enrichment.py -q
```
