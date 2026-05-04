# Codex Review Package v8.2

## Purpose

This folder now carries two layers of material for the standalone "villain feedback control core" used by the novel content generation recommendation system:

1. the corrected `v8.1` tightening baseline
2. the `V8.2` development-requirements package that turns those tightening decisions into a real "master outline + execution checklist" handoff for the next Claude review

The original `v8` direction remains valid, but the active send set is now `V8.2`, not the older `v8.1` handoff.

## Core Boundary

The first build remains a **standalone control core**:

- no direct `writer` integration
- no direct UI wiring
- no direct CLI wiring
- no persistence coupling
- no default-path behavior change for existing baseline or v2/v6/v7 services

The immediate goal is to define a reviewable, testable increment-layer control surface with explicit constraints, layered state, structured decision output, and a non-handwavy ownership map for every major review finding.

`V8.2` adds one more hard requirement on top of that:

- the package must explicitly distinguish what is already tightened in docs, what is already landed in runtime, and what residual gaps still remain after that landing

## Files

### Active V8.2 send set

1. `2026-05-04-v8.2-development-master-outline.md`
   The top-level development contract for `V8.2`. This is the new authoritative outline.

2. `2026-05-04-v8.2-execution-checklist.md`
   The PR-slice execution checklist for bringing the current `narrative_v8` runtime into `V8.2` alignment.

3. `2026-05-04-v8.2-claude-review-handoff.md`
   The new Claude re-review handoff and ready-to-send review prompt for `V8.2`.

These are the three `V8.2` delivery docs.
For an actual Claude re-review, they should be sent together with the fixed evidence package listed below in the recommended review order.

### Supporting v8.1 baseline docs

1. `2026-05-04-knife-system-context-summary.md`
   Narrative and systems context for why the design is split into knife primitives, villain cognition, scene mapping, and long-line control.

2. `2026-05-04-villain-feedback-control-schema.md`
   The corrected `v8.1` schema draft. This is the main data-model document.

3. `2026-05-04-villain-feedback-control-engineering-plan.md`
   The corrected `v8.1` implementation plan, now explicitly reordered to frontload constraints, validation, and helpers before controller orchestration.

4. `2026-05-04-claude-review-package.md`
   Historical `v8.1` review handoff. Kept for audit trail only; `V8.2` handoff supersedes it as the active review entry.

5. `2026-05-04-villainess-blackening-spiral-analysis.md`
   Creative-analysis source document tracing where the knife system came from.

6. `../../claude_review_package/v8/V8_1_ENGINEERING_TIGHTENING.md`
   Direct engineering-closeout answer to the keep/split/validate/helper/order/test questions.

7. `../../claude_review_package/v8/V8_1_REVIEW_TRACEABILITY_MATRIX.md`
   Line-by-line mapping from Claude findings to v8.1 structures, validations, helper ownership, test proof, and residual risks.

## What Changed In v8.1

Compared with the earlier `v8` draft, `v8.1` explicitly fixes the following:

1. `StateLedger` is no longer a flat delta object and is now split into relationship, narrative, psychological, and hook layers.
2. Knife restrictions are no longer carried only by profile arrays and now require explicit constraint and compatibility modeling.
3. `VillainFeedbackPacket` is no longer a narrative-heavy flat output and is now split into decision, explanation, state-shift, and hook layers.
4. `SceneContext` now requires observer roles and power topology, not just a simple audience list.
5. Flavor is tightened so that stable flavor axes live in the profile, while runtime flavor rendering stays in the output layer.
6. The implementation host is corrected from the wrong TypeScript `packages/core` thread to the current Python repository.
7. The execution order now enforces validation and differential tests before controller assembly.
8. The selector is now explicitly defined as a hard-filter-first controller rather than a preference-only scorer.
9. No-fit selection now requires a structured fallback instead of a fake knife choice.
10. Controller orchestration is explicitly separated from helper-owned ledger and constraint rules.
11. `FlavorRender` now has to declare structural packet impact, not just wording differences.
12. Failure / recovery / upgrade / collapse now have explicit transition-state ownership instead of living only in prose.
13. The package now includes an explicit traceability matrix so review findings cannot drift away from responsible structures and tests.

## What V8.2 Adds

`V8.2` does not replace the `v8.1` tightening decisions. It wraps them into a stricter development package by adding:

1. a single top-level master outline instead of only answer-style tightening docs
2. a PR-slice execution checklist tied to the real runtime file layout under `backend/app/services/narrative_v8/`
3. explicit promotion of transition ownership into a first-class runtime-and-doc ownership boundary
4. an explicit split between:
   - what the docs already tightened
   - what the runtime already implements
   - what residual risks still remain after the latest runtime landing
5. a new Claude handoff that asks for review of the complete `V8.2` development package rather than only the older `v8.1` schema/plan pair
6. a runtime-synced transition ownership story:
   - `SceneContext.current_control_state`
   - `TransitionLayer`
   - `VillainFeedbackPacket.transition`
   - `BuildVillainFeedbackOutput.next_control_state`
   - `backend/app/services/narrative_v8/fallbacks.py`
   - `backend/app/services/narrative_v8/transition_policy.py`
   - `backend/app/services/narrative_v8/transitions.py`
   - `tests/test_narrative_v8_fallbacks.py`
   - `tests/test_narrative_v8_transition_policy.py`
   - `tests/test_narrative_v8_transitions.py`

## Recommended Review Order

1. `../../claude_review_package/v8/V8_CLAUDE_REVIEW_SUMMARY.md`
2. `../../claude_review_package/v8/V8_CLAUDE_REVIEW_EVIDENCE.md`
3. `../../claude_review_package/v8/V8_CODEX_REVIEW_TOTAL.md`
4. `../../claude_review_package/v8/V8_1_ENGINEERING_TIGHTENING.md`
5. `../../claude_review_package/v8/V8_1_REVIEW_TRACEABILITY_MATRIX.md`
6. `2026-05-04-v8.2-development-master-outline.md`
7. `2026-05-04-v8.2-execution-checklist.md`
8. `2026-05-04-v8.2-claude-review-handoff.md`
9. `2026-05-04-villain-feedback-control-schema.md` if the reviewer wants the deeper v8.1 schema baseline
10. `2026-05-04-villain-feedback-control-engineering-plan.md` if the reviewer wants the deeper v8.1 engineering baseline

## Minimal Send Set

If only the smallest useful set is sent for re-review, use:

1. `../../claude_review_package/v8/V8_CLAUDE_REVIEW_SUMMARY.md`
2. `../../claude_review_package/v8/V8_CLAUDE_REVIEW_EVIDENCE.md`
3. `../../claude_review_package/v8/V8_CODEX_REVIEW_TOTAL.md`
4. `2026-05-04-v8.2-development-master-outline.md`
5. `2026-05-04-v8.2-execution-checklist.md`
6. `2026-05-04-v8.2-claude-review-handoff.md`

## Review Focus

Claude should mainly verify whether `V8.2` now turns the earlier structural tightening into a real development package:

1. layered ledger boundaries
2. explicit knife constraints and incompatibilities
3. structured decision output
4. observer topology and power structure
5. explicit transition ownership instead of prose-only state logic
6. validation-first task order
7. host alignment with the real repository
8. selector behavior as a hard-filter control gate
9. structurally honest fallback behavior
10. controller-only orchestration without hidden helper rules
11. flavor impact on packet structure rather than prose alone
12. an honest split between current runtime reality and the remaining residual risks after transition runtime has landed

## Package Verdict

`v8.1` should still be treated as the corrected planning baseline.

`V8.2` should now be treated as the active review package for the next round because it adds the missing development-handoff layer:

- direction remains right
- boundary tightening is now explicit
- review ownership is now explicit
- host-path contamination is removed
- first implementation target is repository-realistic
- transition-state ownership is elevated into a first-class landed structure instead of a prose-only requirement
- runtime-vs-doc reality is now called out explicitly instead of being left implicit
- the remaining review focus is no longer “is transition missing”, but “are the topology-gated transition thresholds broad enough, is the first workbench consumer wiring honest and rollback-safe enough, and are the controller boundaries tight enough”

It is still a planning and review package, not a claim that production runtime is already complete.
