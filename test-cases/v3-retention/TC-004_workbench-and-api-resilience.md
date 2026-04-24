# TC-004 Workbench And API Resilience

## Objective

Ensure corrupted artifacts, ledger write failures, and stale network responses do not break core preview/workbench flow.

## Preconditions

- Workbench context import path enabled.
- V2 preview endpoint enabled.

## Test Inputs

1. Corrupted `workbench_contexts.json`.
2. Corrupted `reverse_outline_records.jsonl`.
3. Invalid ledger path (directory instead of file).
4. Two preview requests where older response arrives last.

## Assertions

1. Workbench route falls back to live context when imported JSON is invalid.
2. Quality enrichment corruption does not crash context listing.
3. Preview endpoint returns `200` and includes `ledger_warning` when ledger append fails.
4. UI ignores stale preview response and keeps latest decision visible.
5. Quality metadata (`quality_notes`) is preserved through API normalization and rendered in rail.

## Automated Coverage

- `tests/test_narrative_v2_imported_contexts.py`
- `tests/test_narrative_v2_workbench_context_api.py`
- `tests/test_narrative_v2_workbench_quality_enrichment.py`
- `tests/test_narrative_v2_preview_service.py`
- `tests/test_narrative_v2_api.py`
- `ui-react/src/pages/V2WorkbenchPage.test.tsx`
- `ui-react/src/features/v2Workbench/backendContexts.test.ts`
