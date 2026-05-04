# Claude Review Package v8

This package contains the review artifacts for the v8 villain feedback control core and the direct v8.1 tightening response materials.

## Files

- `V8_CLAUDE_REVIEW_SUMMARY.md`
  Claude review summary and findings.
- `V8_CLAUDE_REVIEW_EVIDENCE.md`
  Evidence-fixed structural decomposition from the initial source material.
- `V8_CODEX_REVIEW_REQUEST_PROMPT.md`
  Request prompt for the v8.1 revision pass.
- `V8_CODEX_REVIEW_TOTAL.md`
  Consolidated total review draft for Codex.
- `V8_1_ENGINEERING_TIGHTENING.md`
  Direct engineering-closeout answer to the keep/split/validate/helper/order/test questions.
- `V8_1_REVIEW_TRACEABILITY_MATRIX.md`
  Line-by-line mapping from Claude findings to v8.1 structures, validations, helpers, tests, and residual risks.

## Purpose

The goal of this package is to keep the review chain auditable and grounded:

1. the original review summary still defines what Claude rejected
2. the evidence file still proves the review was grounded
3. the total review still consolidates the fixed review logic
4. the engineering tightening file answers the actual v8.1 rewrite questions
5. the traceability matrix prevents future "sounds fixed but ownership is still floating" review gaps

This package remains the evidence-and-review source of truth.

The active next-step development-handoff package that consumes these materials now lives in:

- `codex-review/v8/2026-05-04-v8.2-development-master-outline.md`
- `codex-review/v8/2026-05-04-v8.2-execution-checklist.md`
- `codex-review/v8/2026-05-04-v8.2-claude-review-handoff.md`

## Recommended Read Order

1. `V8_CLAUDE_REVIEW_SUMMARY.md`
2. `V8_CLAUDE_REVIEW_EVIDENCE.md`
3. `V8_CODEX_REVIEW_TOTAL.md`
4. `V8_1_ENGINEERING_TIGHTENING.md`
5. `V8_1_REVIEW_TRACEABILITY_MATRIX.md`
6. `V8_CODEX_REVIEW_REQUEST_PROMPT.md`

## How This Feeds V8.2

The intended chain is now:

1. this folder proves what Claude originally rejected and why
2. `V8_1_ENGINEERING_TIGHTENING.md` proves how the major structural issues were tightened
3. `V8_1_REVIEW_TRACEABILITY_MATRIX.md` proves where each responsibility now lives
4. the `codex-review/v8` `V8.2` package turns that tightening into a real development outline plus execution checklist

## Review Use

If the next reviewer asks "what exactly was fixed and where does that responsibility now live?", the intended answer path is:

1. read the summary for the finding
2. read the tightening file for the v8.1 decision
3. read the traceability matrix for the exact structure/validation/helper/test owner

That is the main anti-churn addition in this package.
