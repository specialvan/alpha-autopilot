# TC-002-01 Decision Contract Branches

## Given

- Rule checks and recommendation sets for:
  - `ready` path (high score, no blocked rules)
  - `review` path (valid but not ready)
  - `blocked` path (no legal action)

## When

- Build standardized decision payload.

## Then

- `quality_hint` must match the expected branch.
- `selected_action`, `selected_score`, and rule summary fields are coherent.

## Command

```powershell
pytest tests/test_narrative_v2_decision_contract.py -q
```
