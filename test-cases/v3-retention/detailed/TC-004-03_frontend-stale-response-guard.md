# TC-004-03 Frontend Stale Response Guard

## Given

- Two preview requests are in flight, and the older request resolves after the newer one.
- Context fetch may fail and trigger fallback.

## When

- Render workbench page and resolve promises out of order.

## Then

- UI keeps newest decision output.
- UI shows backend-context fallback notice when context fetch fails.

## Command

```powershell
npm test -- --run src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/backendContexts.test.ts
```
