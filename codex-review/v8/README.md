# Codex Review Package v8.1

## Purpose

This folder is the corrected `v8.1` review package for the standalone "villain feedback control core" used by the novel content generation recommendation system.

The original `v8` direction remains valid, but one major engineering assumption has been corrected:

- the earlier thread accidentally inherited a host target from `D:\workspace\inkos\packages\core`
- that host assumption does **not** belong to `alpha-autopilot`
- the current package now targets the actual repository and a standalone Python increment module under `backend/app/services/narrative_v8/`

This package is therefore not a brand-new idea dump. It is a tightening pass that absorbs Claude's review findings and removes cross-thread path contamination.

## Core Boundary

The first build remains a **standalone control core**:

- no direct `writer` integration
- no direct UI wiring
- no direct CLI wiring
- no persistence coupling
- no default-path behavior change for existing baseline or v2/v6/v7 services

The immediate goal is to define a reviewable, testable increment-layer control surface with explicit constraints, layered state, and structured decision output.

## Files

1. `2026-05-04-knife-system-context-summary.md`
   Narrative and systems context for why the design is split into knife primitives, villain cognition, scene mapping, and long-line control. This file is conceptual context; the schema doc is the authoritative source for implementation shape.

2. `2026-05-04-villain-feedback-control-schema.md`
   The corrected `v8.1` schema draft. This is the main data-model document.

3. `2026-05-04-villain-feedback-control-engineering-plan.md`
   The corrected `v8.1` implementation plan, now aligned to the current Python repository structure.

4. `2026-05-04-claude-review-package.md`
   Review handoff instructions and a ready-to-send Claude prompt for re-reviewing the tightened `v8.1` package.

5. `2026-05-04-villainess-blackening-spiral-analysis.md`
   Creative-analysis source document tracing where the knife system came from.

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

## Recommended Review Order

1. `2026-05-04-knife-system-context-summary.md`
2. `2026-05-04-villain-feedback-control-schema.md`
3. `2026-05-04-villain-feedback-control-engineering-plan.md`
4. `2026-05-04-claude-review-package.md`
5. `2026-05-04-villainess-blackening-spiral-analysis.md` if deeper literary origin context is needed

## Minimal Send Set

If only the smallest useful set is sent for re-review, use:

1. `2026-05-04-villain-feedback-control-schema.md`
2. `2026-05-04-villain-feedback-control-engineering-plan.md`
3. `2026-05-04-knife-system-context-summary.md`

## Review Focus

Claude should mainly verify whether `v8.1` now resolves the previous structural issues:

1. layered ledger boundaries
2. explicit knife constraints and incompatibilities
3. structured decision output
4. observer topology and power structure
5. validation-first task order
6. host alignment with the real repository
7. selector behavior as a hard-filter control gate
8. structurally honest fallback behavior
9. controller-only orchestration without hidden helper rules
10. flavor impact on packet structure rather than prose alone

## Package Verdict

`v8.1` should be treated as the corrected planning baseline for the next review round:

- direction remains right
- boundary tightening is now explicit
- host-path contamination is removed
- first implementation target is now repository-realistic

It is still a planning package, not production code, but it should now be reviewable on its actual engineering merits rather than being blocked by the wrong host assumption.
