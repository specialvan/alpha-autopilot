# TC-002 Generation Control

## Objective

Verify generation-control output is deterministic and can represent both legacy and retention-oriented decision contracts.

## Preconditions

- `alpha_autopilot_v3/generation_control/*` wired by decomposition pipeline.
- Preview decision contract available in `backend/app/services/narrative_v2/decision_contract.py`.

## Test Inputs

1. High-attraction recommendation scenario.
2. Blocked/no-recommendation scenario.
3. Legacy recommendation-only response without explicit decision details.

## Assertions

1. Decision object contains stable `selected_action`, `selected_score`, `quality_hint`.
2. Ready/review/blocked branches are all test-covered.
3. UI fallback path still renders recommendation explanation/details when decision payload is partial.

## Automated Coverage

- `tests/test_narrative_v2_decision_contract.py`
- `ui-react/src/pages/V2WorkbenchPage.test.tsx`
