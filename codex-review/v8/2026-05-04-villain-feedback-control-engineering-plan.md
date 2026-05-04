# Villain Feedback Control Core v8.1 Implementation Plan

**Goal:** Build a standalone Python control core under `backend/app/services/narrative_v8/` that models villain knife primitives, differentiates villain cognition and flavor, tracks layered long-line state, and emits structured recommendation packets for downstream narrative systems.

**Architecture:** Keep the first version fully detached from `writer`, UI, CLI, storage, and existing default paths. Build from the inside out with hard gates in front of orchestration: schema definition first, constraint vocabulary and compatibility rules second, validation gates third, knife library population fourth, helper layers next, and controller assembly only after the business rules are already explicit and test-locked.

**Tech Stack:** Python 3.10+, Pydantic, pytest, repository-native `backend/app/services/narrative_v*` service patterns.

---

## 1. Implementation Boundary

`v8.1` is a planning baseline for an increment-layer control core. The first implementation should:

1. live only under `backend/app/services/narrative_v8/`
2. add focused pytest coverage under `tests/`
3. avoid new API routes
4. avoid persistence coupling
5. avoid `writer`/LLM invocation
6. avoid touching baseline `alpha_autopilot` domain files unless a later review explicitly approves that move

This directly corrects the earlier mistaken `packages/core` TypeScript host assumption.

## 2. File Map

Recommended first-pass file layout:

1. `backend/app/services/narrative_v8/__init__.py`
2. `backend/app/services/narrative_v8/schemas.py`
3. `backend/app/services/narrative_v8/constraints.py`
4. `backend/app/services/narrative_v8/knife_library.py`
5. `backend/app/services/narrative_v8/selection.py`
6. `backend/app/services/narrative_v8/flavor.py`
7. `backend/app/services/narrative_v8/ledger.py`
8. `backend/app/services/narrative_v8/transitions.py`
9. `backend/app/services/narrative_v8/controller.py`
10. `tests/test_narrative_v8_schemas.py`
11. `tests/test_narrative_v8_knife_library.py`
12. `tests/test_narrative_v8_selection.py`
13. `tests/test_narrative_v8_flavor.py`
14. `tests/test_narrative_v8_ledger.py`
15. `tests/test_narrative_v8_transitions.py`
16. `tests/test_narrative_v8_controller.py`
17. `tests/test_narrative_v8_integration.py`

Responsibility split:

1. `schemas.py`
   Owns all Pydantic models and schema-level shape validation.

2. `constraints.py`
   Owns reusable filtering helpers and the vocabulary for scene/target/observer/anti-condition rejection.

3. `knife_library.py`
   Owns built-in primitives and the compatibility graph data.

4. `selection.py`
   Owns hard filtering, scored fit, fallback, and structured selection output.

5. `flavor.py`
   Owns stable-profile-to-runtime-render conversion and packet-surface flavor impact.

6. `ledger.py`
   Owns layered state application and boundary-safe update logic.

7. `transitions.py`
   Owns helper-owned failure/recovery/upgrade/collapse state-machine rules.

8. `controller.py`
   Only orchestrates already-defined rules. It must not become the place where hidden business rules are discovered.

## 3. Revised Execution Order

This plan intentionally follows the tightened v8.1 sequence:

1. schema definition
2. constraint and compatibility rules
3. validation gates
4. knife library population
5. selection helpers
6. flavor rendering
7. layered ledger and transition application
8. controller orchestration
9. focused integration and differential verification

The controller is last on purpose.

## 4. Validation Gates Before Controller

The system is not ready for controller work until all of the following are independently green:

1. schema validation
2. knife compatibility validation
3. scene compatibility validation
4. state boundary validation
5. transition policy validation
6. same knife / different villain differential tests
7. same villain / different scene differential tests
8. structured fallback validation

If any of those gates fail, the fix belongs in schemas, constraints, library data, selection helpers, flavor helpers, or ledger helpers, not in controller-local branches.

## 5. Task 1: Define schemas and validation contracts

**Files**

1. Create `backend/app/services/narrative_v8/schemas.py`
2. Create `tests/test_narrative_v8_schemas.py`

**Scope**

Add the core data contracts:

1. `KnifePrimitive`
2. `KnifeConstraintSet`
3. `KnifeCompatibilityEdge`
4. `VillainProfile`
5. `FlavorAxisProfile`
6. `TargetProfile`
7. `SceneObserver`
8. `PowerEdge`
9. `SceneContext`
10. `RelationshipLedgerState`
11. `NarrativeLedgerState`
12. `PsychologicalLedgerState`
13. `HookLedgerState`
14. `LedgerSnapshot`
15. `RelationshipLedgerShift`
16. `NarrativeLedgerShift`
17. `PsychologicalLedgerShift`
18. `HookLedgerShift`
19. `StateLedgerShift`
20. `SelectedKnifeSignal`
21. `RejectedKnifeReason`
22. `DecisionLayer`
23. `ExplanationLayer`
24. `TransitionLayer`
25. `FlavorRender`
26. `FutureHook`
27. `VillainFeedbackPacket`
28. `BuildVillainFeedbackInput`
29. `BuildVillainFeedbackOutput`

**Required validation rules**

1. `preferred_knives` length must be `1..3`
2. `secondary_knives` length must be `0..2`
3. `forbidden_moves` must not be empty
4. `preferred_knives` must not overlap `forbidden_moves`
5. public scene contexts must not use empty observer sets
6. `FlavorRender` must not be used as profile input
7. layered ledger models must stay nested and not collapse back into a flat delta map
8. `DecisionLayer` fallback mode must allow no knife ids and must require both `fallback_action` and `fallback_reason`
9. `DecisionLayer` scored-fit mode must require a primary knife id plus non-empty `selected_signals`
10. `FlavorRender.structural_targets` must declare at least two packet surfaces
11. `TransitionLayer` must always carry `prior_state`, `next_state`, and `transition_reason`
12. `upgrade_path` must not appear without `upgrade_trigger`
13. `collapsed` transitions must not also claim an active `recovery_mode`

**Required tests**

1. accepts a minimally valid villain profile
2. rejects preferred/forbidden overlap
3. rejects public scene with no observers
4. accepts a layered `StateLedgerShift`
5. accepts a structured `VillainFeedbackPacket`
6. rejects a flat old-style packet payload
7. rejects fallback packets that still pretend to have a selected knife
8. rejects `FlavorRender` payloads that do not declare enough structural targets
9. rejects transition payloads that mix collapse semantics with active recovery semantics

**Exit gate**

```bash
pytest tests/test_narrative_v8_schemas.py -q
```

Expected:

1. all schema tests pass
2. no controller code exists yet

## 6. Task 2: Define constraint vocabulary and compatibility behavior

**Files**

1. Create `backend/app/services/narrative_v8/constraints.py`
2. Extend `tests/test_narrative_v8_selection.py` with rejection-category fixture coverage

**Scope**

Add reusable helpers that:

1. normalize candidate knife ids from profile preference data
2. evaluate scene restrictions
3. evaluate target restrictions
4. evaluate observer requirements
5. evaluate anti-conditions
6. evaluate backfire and ineffective conditions
7. evaluate flavor conflicts
8. evaluate knife-to-knife compatibility conflicts

**Required behaviors**

1. every rejection has a category and detail
2. `forbidden_moves`, `anti_conditions`, missing `observer_requirements`, and incompatible knife edges are hard filters, not score penalties
3. explicit modeled rejection causes must not be collapsed into generic `low_fit_score`

**Exit gate**

```bash
pytest tests/test_narrative_v8_schemas.py tests/test_narrative_v8_selection.py -q
```

Expected:

1. rejection categories are stable before the default library is fully populated
2. controller work is still blocked

## 7. Task 3: Frontload validation gates

**Files**

1. Extend `tests/test_narrative_v8_selection.py`
2. Create `tests/test_narrative_v8_ledger.py`

**Scope**

Before library and controller assembly, lock down:

1. scene compatibility validation
2. observer-topology rejection behavior
3. state boundary validation
4. transition policy validation
5. fallback shape validation

**Required tests**

1. missing observer requirement yields `observer_requirement_missing`, not just a lower score
2. anti-condition failure yields `anti_condition`, not just a lower score
3. relationship shifts do not mutate psychological fields
4. hook recovery does not overwrite relationship or narrative state
5. invalid transition payloads are rejected before controller orchestration
6. no-fit fallback leaves `primary_knife_id`, `secondary_knife_id`, and `selected_signals` empty

**Exit gate**

```bash
pytest tests/test_narrative_v8_selection.py tests/test_narrative_v8_ledger.py -q
```

Expected:

1. validation-first behavior is test-locked before controller work

## 8. Task 4: Populate the knife library and compatibility graph

**Files**

1. Create `backend/app/services/narrative_v8/knife_library.py`
2. Create `tests/test_narrative_v8_knife_library.py`

**Scope**

Add:

1. the first built-in library of 10 knife primitives
2. explicit `KnifeConstraintSet` content for each primitive
3. a compatibility graph export
4. lookup helpers by knife id

**Minimum primitive coverage**

The built-in library should cover:

1. `self_image_feeding`
2. `high_ground_pity`
3. `fake_vulnerability`
4. `delayed_asking`
5. `relationship_withdrawal`
6. `old_wound_trigger`
7. `memory_reframing`
8. `courteous_humiliation`
9. `gentle_absorption`
10. `baited_concession`

**Required tests**

1. library contains all baseline primitives
2. compatibility graph exposes incompatible pairs
3. primitives with public-pressure mechanics declare observer requirements
4. primitives with high exposure risk declare backfire conditions

**Exit gate**

```bash
pytest tests/test_narrative_v8_knife_library.py -q
```

Expected:

1. library tests pass
2. compatibility logic is explicit data, not selector-only hidden rules

## 9. Task 5: Build reusable selection helpers

**Files**

1. Create `backend/app/services/narrative_v8/selection.py`
2. Extend `tests/test_narrative_v8_selection.py`

**Scope**

The selector must be a two-stage controller, not a preference sorter. It must:

1. enforce `forbidden_moves`
2. enforce scene restrictions
3. enforce target restrictions
4. enforce observer requirements
5. enforce anti-conditions
6. enforce knife-to-knife compatibility
7. emit structured `RejectedKnifeReason` objects
8. emit fit-score-bearing `SelectedKnifeSignal` objects

**Required differential tests**

1. same knife, different villain -> different fit scores and explanation seeds
2. same villain, different scene -> different selection outcome
3. forbidden knife always appears in the rejected list
4. hard-filtered knives never appear inside the scored candidate set
5. observer-topology changes alter public-pressure knife fit
6. no-fit path yields an explainable fallback

**Exit gate**

```bash
pytest tests/test_narrative_v8_selection.py -q
```

Expected:

1. selection logic is deterministic
2. the selector behaves as a control gate, not as a simple ranker

## 10. Task 6: Build flavor rendering

**Files**

1. Create `backend/app/services/narrative_v8/flavor.py`
2. Create `tests/test_narrative_v8_flavor.py`

**Scope**

Add a runtime renderer that turns:

1. `VillainProfile.flavor_profile`
2. `public_mask`
3. `private_drive`
4. chosen knife
5. scene arena
6. visibility

into a scene-specific `FlavorRender`.

**Critical rule**

Flavor rendering is an output transform. It must not become a second hidden source of character definition, and it must not degrade into wording-only garnish.

`FlavorRender` must materially shape packet structure by influencing at least:

1. how `external_move` is packaged
2. what `risk_if_exposed` looks like
3. what `future_hooks` are planted
4. which `state_shift` layer gets emphasized

**Required tests**

1. same knife + different villain -> different `FlavorRender`
2. same villain + different arena -> different `FlavorRender`
3. `FlavorRender` remains structurally separate from `FlavorAxisProfile`
4. same knife + different villain changes at least one structural packet field besides wording
5. flavor changes can alter hook style or exposure profile without changing the chosen knife
6. `FlavorRender.structural_targets` always names at least two changed packet surfaces
7. `FlavorRender.state_shift_focus` matches the packet's emphasized ledger layer

**Exit gate**

```bash
pytest tests/test_narrative_v8_flavor.py -q
```

Expected:

1. flavor tests pass
2. flavor differences are generated from stable profile axes plus scene conditions

## 11. Task 7: Implement the layered ledger

**Files**

1. Create `backend/app/services/narrative_v8/ledger.py`
2. Create `backend/app/services/narrative_v8/transitions.py`
3. Extend `tests/test_narrative_v8_ledger.py`
4. Create `tests/test_narrative_v8_transitions.py`

**Scope**

Add helpers that:

1. apply `StateLedgerShift` to `LedgerSnapshot`
2. clamp numeric deltas into the allowed range
3. keep relationship/narrative/psychological/hook layers isolated
4. append and recover hooks without mutating unrelated layers
5. derive `TransitionLayer` from `current_control_state`, fallback/exposure signals, and upgrade triggers
6. keep all per-layer mutation logic and state-machine branching out of the controller

**Required tests**

1. applies bounded deltas per layer
2. relationship shifts do not mutate psychological fields
3. hook recovery does not overwrite relationship or narrative state
4. at most two high-magnitude deltas are accepted per scene
5. public exposure or shell-loss signals change transition outcome before controller
6. upgrade and recovery cannot both be primary outcomes in the same transition result
7. controller-level recomputation of ledger transitions is unnecessary after helper use

**Exit gate**

```bash
pytest tests/test_narrative_v8_ledger.py tests/test_narrative_v8_transitions.py -q
```

Expected:

1. ledger and transition tests pass
2. the ledger remains a structured state model, not a flat event log

## 12. Task 8: Assemble the controller last

**Files**

1. Create `backend/app/services/narrative_v8/controller.py`
2. Create `backend/app/services/narrative_v8/__init__.py`
3. Create `tests/test_narrative_v8_controller.py`

**Scope**

The controller should only orchestrate the already-tested helper layers:

1. validate input models
2. load primitive library and compatibility data
3. filter and select knives
4. render flavor
5. compute `ExplanationLayer`
6. compute `TransitionLayer`
7. compute `StateLedgerShift`
8. apply shift to get `next_snapshot`
9. return `BuildVillainFeedbackOutput`

**Strict rule**

Do not bury new business rules in the controller.

The controller must not directly implement any branch for:

1. `forbidden_moves`
2. `observer_requirements`
3. `anti_conditions`
4. compatibility conflicts
5. delta clamping
6. hook merge/recovery semantics
7. failure/recovery/upgrade/collapse transition branching

If any of those appear as controller-local rule branches, that is a design failure and the logic belongs in helpers.

**Required tests**

1. returns a structured packet plus `next_snapshot`
2. emits `decision`, `explanation`, `transition`, `state_shift`, and `future_hooks` as separate layers
3. carries rejected-knife reasons forward from the selection layer
4. produces stable outputs for the same deterministic input
5. controller delegates hard filtering to selection helpers rather than re-implementing it
6. controller delegates transition derivation to transition helpers rather than mutating states inline
7. controller delegates state application to ledger helpers rather than mutating layers inline

**Exit gate**

```bash
pytest tests/test_narrative_v8_controller.py -q
```

Expected:

1. controller tests pass
2. no missing business-rule gaps are discovered at orchestration time
3. controller remains an orchestrator, not a hidden rule engine

## 13. Task 9: Focused integration and review gates

**Files**

1. Create `tests/test_narrative_v8_integration.py`

**Scope**

The integration suite should prove that `v8.1` solved the exact issues that caused the previous review rejection.

**Required integration cases**

1. same knife / different villain
2. same villain / different scene
3. public observer topology change
4. anti-condition rejection
5. no-fit fallback without fake knife selection
6. failure-mode behavior when visibility, audience, or pressure conditions change
7. layered ledger update with future-hook carry-forward
8. flavor changes alter structural packet fields, not only prose wording
9. `state_shift_focus` matches actual packet emphasis

**Focused verification command**

```bash
pytest \
  tests/test_narrative_v8_schemas.py \
  tests/test_narrative_v8_knife_library.py \
  tests/test_narrative_v8_selection.py \
  tests/test_narrative_v8_flavor.py \
  tests/test_narrative_v8_ledger.py \
  tests/test_narrative_v8_transitions.py \
  tests/test_narrative_v8_controller.py \
  tests/test_narrative_v8_integration.py \
  -q
```

Expected:

1. all focused v8 tests pass
2. the package is review-ready as a standalone increment core

## 14. Test Order Revision

The test stack should be read in this order:

1. schema tests
2. compatibility tests
3. state transition tests
4. differential tests
5. fallback tests
6. controller integration tests

This ordering is part of the design. If controller tests are the first place where a rule is discovered, the helper layers are still too soft.

## 15. Non-Goals For This Plan

This plan deliberately does **not** include:

1. API route registration
2. UI workbench visualization
3. `writer` prompt assembly
4. storage adapters
5. benchmark loop integration
6. large-scale scene generation

Those are later-phase consumers. `v8.1` first has to prove that the control core itself is structurally sound.

## 16. Review Checklist

Before this plan is considered acceptable for implementation, a reviewer should be able to answer `yes` to all of these:

1. Is the host now aligned to the current repository rather than the wrong `packages/core` thread?
2. Is the ledger now layered rather than flat?
3. Are knife constraints explicit rather than implied by string lists?
4. Is packet output structured rather than only narrative text?
5. Does the scene model now include observer roles and power topology?
6. Does the task order force validation before controller wiring?
7. Is the selector clearly a control gate rather than a preference scorer?
8. Does the controller stay free of helper-owned rule branches?
9. Is fallback represented structurally rather than as a fake knife choice?
10. Does flavor declare explicit structural targets rather than only wording?
11. Are failure / recovery / upgrade / collapse transitions explicit and helper-owned?
12. Can the test suite prove anti-collapse behavior instead of only happy-path output?

If any answer is `no`, `v8.1` is still not tight enough.
