# V5 Condition Closure Task Board

## Objective

Close remaining `GO WITH CONDITIONS` items from internal pre-acceptance and prepare a clean `GO` gate.

Source:

- `claude_review_package/V5/V5_CODEX_INTERNAL_PRE_ACCEPTANCE_2026_04_27.md`

## Task T09 - External Coverage Judge Rollout Contract

- Status: `completed` (2026-04-27)
- Scope:
  - Define runtime policy for `PromptCompressor.coverage_judge` enablement:
    - off by default
    - canary-on config
    - full-on config
  - Add explicit config key(s) and decision log field(s) in compression metrics.
- Acceptance:
  - [x] `coverage_source` reports expected value under default and canary profiles.
  - [x] No regression in existing prompt compression tests.
  - [x] Updated docs explain default and override behavior.

## Task T10 - External Validation Inspector/Fixer Rollout Contract

- Status: `completed` (2026-04-27)
- Scope:
  - Define runtime injection policy for character validation `inspector` / `fixer`.
  - Add operational switches and guardrails for latency/cost fallback.
  - Ensure bridge observability clearly marks `llm_mode`.
- Acceptance:
  - [x] Default profile remains backward-compatible.
  - [x] Canary profile can enable external hooks without breaking fallback path.
  - [x] Validation logs support production diagnostics.

## Task T11 - Canary Evidence and Gate Update

- Status: `completed` (2026-04-27, includes live remote LLM canary)
- Scope:
  - Run canary-like validation for T09/T10 profile toggles.
  - Run live remote LLM traffic canary through production runner.
  - Record latency/cost/quality observations.
  - Update V5 review package decision from conditionally-ready to gate-ready (if criteria met).
- Acceptance:
  - [x] Evidence file includes command outputs and observed metrics.
  - [x] Any residual risks are explicitly tracked with owner + ETA.
  - [x] Final gate recommendation is traceable to evidence.
