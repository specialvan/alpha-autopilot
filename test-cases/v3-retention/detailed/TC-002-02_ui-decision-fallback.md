# TC-002-02 UI Decision Fallback

## Given

- Backend response without rich `decision.explanation/details`.
- Legacy recommendation explanation/details still present.

## When

- Render `V2WorkbenchPage`.

## Then

- Decision surface falls back to recommendation explanation/details.
- Validation rail prefers decision arrays when present.

## Command

```powershell
npm test -- --run src/pages/V2WorkbenchPage.test.tsx
```
