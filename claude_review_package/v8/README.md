# Claude Review Package v8

## Purpose

This folder packages Claude's review result for the v8 "villain feedback control core" proposal so Codex can read the findings before issuing any new implementation plan.

The review outcome is **not approval**. The current v8 design is directionally correct, but it needs structural tightening before implementation:

1. state ledger must be split into meaningful layers
2. knife compatibility and anti-conditions must be made explicit
3. selection reasons must become structured, not only narrative text
4. scene context must include observer structure and power topology
5. the implementation plan must add validation and differential tests before controller wiring

## Files

1. `V8_CLAUDE_REVIEW_SUMMARY.md`
   The actual review result, including overall judgment, P0/P1/P2 findings, model suggestions, execution-order changes, and risk notes.

2. `V8_CODEX_REVIEW_REQUEST_PROMPT.md`
   A ready-to-send prompt telling Codex to study Claude's review result and revise the engineering plan accordingly.

## Recommended Read Order

1. `V8_CLAUDE_REVIEW_SUMMARY.md`
2. `V8_CODEX_REVIEW_REQUEST_PROMPT.md`

## Package Verdict

Claude's verdict is:

- **direction is right**
- **current design is not yet sufficiently sealed for implementation**
- **the next revision should be v8.1, not direct execution**

## What Codex Should Do Next

Codex should treat this package as a corrective review package and use it to:

1. tighten schema boundaries
2. add explicit constraint and compatibility modeling
3. split ledger state into relationship / narrative / psychological / hook layers
4. improve implementation sequencing and test coverage
5. revise any plan section that still assumes a single flat control surface
