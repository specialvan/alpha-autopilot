# V8.1 Review Traceability Matrix

> Purpose: map every fixed Claude finding and every user-mandated v8.1 tightening requirement to a concrete v8.1 structure, validation gate, helper owner, test proof, and residual risk.
>
> This file exists to prevent a repeat of the previous failure mode:
> "the wording sounds tightened, but the engineering responsibility is still floating."

## 1. How To Read This File

Each row answers six questions:

1. Which Claude finding or requirement is being addressed?
2. Which v8.1 structure owns the boundary?
3. Which validation gate must catch violations before controller?
4. Which helper owns the rule in implementation?
5. Which test category proves the rule is real?
6. What risk still remains even after v8.1 tightening?

If any row cannot answer all six, then the package is still too soft.

## 2. P0 Findings

| Finding | v8.1 structure owner | Validation gate | Helper owner | Test proof | Residual risk |
|---|---|---|---|---|---|
| `P0-1 State ledger is too flat for long-line control` | `LedgerSnapshot`, `StateLedgerShift`, plus four explicit sublayers: `relationship`, `narrative`, `psychological`, `hook` | `state boundary validation` | `build_state_shift`, `apply_state_shift` | `state transition tests`, `layered ledger update with future-hook carry-forward` | later features may still re-flatten ledger by pushing cross-layer side effects back into controller |
| `P0-2 Knife constraints are not explicit enough` | `KnifeConstraintSet`, `KnifeCompatibilityEdge`, retained `preferred_knives / secondary_knives / forbidden_moves` | `knife compatibility validation`, `scene compatibility validation` | `evaluate_knife_rejection`, `evaluate_compatibility_conflict`, `select_knives` | `compatibility tests`, `anti-condition rejection`, `observer requirement hard rejection` | tokenized restriction strings can still drift unless future expansion keeps a stable vocabulary |
| `P0-3 VillainFeedbackPacket is too narrative-heavy` | `DecisionLayer`, `ExplanationLayer`, `StateLedgerShift`, `FutureHook`, `FlavorRender`, `VillainFeedbackPacket` | `schema validation`, `fallback validation` | `select_knives`, `render_flavor`, `build_external_move_envelope`, `build_risk_if_exposed`, `build_hook_seed` | `schema tests`, `fallback tests`, `controller integration tests` | explanation prose can still dominate if downstream consumers ignore structured layers |

## 3. P1 Findings

| Finding | v8.1 structure owner | Validation gate | Helper owner | Test proof | Residual risk |
|---|---|---|---|---|---|
| `P1-1 Flavor concepts are scattered across too many places` | `FlavorAxisProfile` as stable source, `public_mask` as shell input, `private_drive` as motive input, `FlavorRender` as runtime output only | `schema validation` for profile/output separation, `differential validation` for structural packet impact | `render_flavor` | `same knife + different villain`, `same villain + different arena`, `FlavorRender remains structurally separate from FlavorAxisProfile` | flavor may still degrade into wording-only differences if structural targets are not enforced in future consumers |
| `P1-2 TargetProfile needs stronger computational detail` | `TargetProfile.defense_style`, `witness_sensitivity`, `identity_anchor`, retained `core_need / weak_points` | `scene compatibility validation`, `knife compatibility validation` | `evaluate_knife_rejection`, `_score_candidate` | `same villain / different scene`, `same knife / different villain`, target-sensitive rejection tests | target descriptors can still become too loose if later additions avoid stable enumerations |
| `P1-3 SceneContext needs observer topology and power structure detail` | `SceneObserver`, `PowerEdge`, `SceneContext.observers`, `SceneContext.power_topology` | `scene compatibility validation` | `evaluate_knife_rejection`, `_observer_support_bonus` | `observer-topology changes alter public-pressure knife fit`, `public observer topology change` | topology may still be too coarse if future scenes do not standardize role usage |
| `P1-4 Plan is missing validation gates between schema and controller` | revised execution order in the engineering plan, plus explicit `Validation Gates Before Controller` section | all pre-controller gates | N/A as policy; implementation responsibility distributed across helpers | `schema tests -> compatibility tests -> state transition tests -> differential tests -> fallback tests -> controller integration tests` | teams can still violate order in practice unless review enforces the gate sequence |

## 4. P2 Findings

| Finding | v8.1 structure owner | Validation gate | Helper owner | Test proof | Residual risk |
|---|---|---|---|---|---|
| `P2-1 Naming can be unified further` | stable use of `Profile`, `Context`, `Primitive`, `Packet`, `Ledger`, `Snapshot`, `Shift` | `schema validation` via explicit model boundaries | N/A naming policy | schema and plan consistency review | terminology can drift again when new subsystems are added |
| `P2-2 A negative-style layer may be useful later` | currently deferred; partially covered by retained `forbidden_moves` | none in v8.1 beyond existing forbidden-move enforcement | `evaluate_knife_rejection` for current negative boundary | forbidden-move rejection tests | future high-contrast villains may still need dedicated `avoidance primitives` or `negative style markers` |
| `P2-3 Current testing is too happy-path oriented` | revised test order and expanded differential/fallback coverage | `differential validation`, `fallback validation` | `select_knives`, `apply_state_shift`, controller orchestration only | `same knife / different villain`, `same villain / different scene`, `no-fit fallback`, `failure-mode behavior` | failure-mode coverage is still only first-pass and not yet a broad benchmark corpus |

## 5. User-Mandated Structure Questions

### 5.1 Which fields remain stable?

| Requirement | v8.1 answer | Evidence owner |
|---|---|---|
| Keep main structure, do not overturn it | keep `KnifePrimitive`, `VillainProfile`, `TargetProfile`, `SceneContext`, `VillainFeedbackPacket`, `LedgerSnapshot`, `StateLedgerShift` | `V8_1_ENGINEERING_TIGHTENING.md` keep section |
| Keep stable villain core | keep `core_wound`, `core_belief`, `psychology_literacy`, `preferred_knives`, `secondary_knives`, `forbidden_moves`, `public_mask`, `private_drive`, `time_horizon`, `blind_spot`, `escalation_rule`, `shame_relation`, `witness_need`, `flavor_profile` | `schemas.py`, tightening doc |
| Keep stable target and scene core | keep target-side need/fear/weak points and scene-side arena/stake/visibility/time-pressure/current-phase | `schemas.py`, tightening doc |

### 5.2 Which fields must be split or added?

| Requirement | v8.1 answer | Structure owner |
|---|---|---|
| Split state ledger | four-layer ledger | `LedgerSnapshot`, `StateLedgerShift` |
| Make knife constraints explicit | separate constraints and compatibility graph | `KnifeConstraintSet`, `KnifeCompatibilityEdge` |
| Enhance scene model | observer roles + power topology | `SceneObserver`, `PowerEdge`, `SceneContext` |
| Explicitize failure / recovery / upgrade / transition | separate control-state input plus transition layer output | `SceneContext.current_control_state`, `TransitionLayer`, `FailureMode`, `RecoveryMode`, `UpgradeTrigger`, `UpgradePath` |
| Split output packet | decision / explanation / transition / state shift / hook / flavor | `VillainFeedbackPacket` sublayers |
| Close flavor boundary | stable source vs runtime output split | `FlavorAxisProfile` + `FlavorRender` |

## 6. User-Mandated Pre-Controller Rules

| Requirement | Validation gate | Helper owner | Proof |
|---|---|---|---|
| schema validation | `schema tests` | model validators in `schemas.py` | packet shape, public scene, fallback shape |
| knife compatibility validation | `compatibility tests` | `evaluate_compatibility_conflict` | incompatible edge rejection |
| scene compatibility validation | `compatibility tests` | `evaluate_knife_rejection` | observer requirement / scene restriction rejection |
| state boundary validation | `state transition tests` | `build_state_shift`, `apply_state_shift` | no cross-layer mutation |
| transition policy validation | `state transition tests` | `derive_transition_outcome` | no mixed collapse/recovery semantics, no triggerless upgrade path |
| same knife / different villain | `differential tests` | `select_knives`, `render_flavor` | fit score and structural flavor divergence |
| same villain / different scene | `differential tests` | `select_knives`, `render_flavor`, ledger helpers | selection outcome divergence |

## 7. Required Helper-First Ownership

| Rule family | Must live in | Must not live in |
|---|---|---|
| forbidden moves | `evaluate_knife_rejection` | controller |
| scene restrictions | `evaluate_knife_rejection` | controller |
| target restrictions | `evaluate_knife_rejection` | controller |
| observer requirements | `evaluate_knife_rejection` | controller |
| anti-conditions / backfire / ineffective conditions | `evaluate_knife_rejection` | controller |
| knife-to-knife incompatibility | `evaluate_compatibility_conflict` | controller |
| fit scoring and fallback | `select_knives` | controller |
| flavor projection | `render_flavor` | controller |
| state shift application | `apply_state_shift` | controller |
| failure / recovery / upgrade / collapse transitions | `derive_transition_outcome` | controller |

## 8. Required Order Locks

### 8.1 Implementation order

1. `schema definition`
2. `constraint and compatibility rules`
3. `validation layer`
4. `knife library`
5. `selection helpers`
6. `flavor rendering`
7. `layered ledger and transition application`
8. `controller orchestration`

### 8.2 Test order

1. `schema tests`
2. `compatibility tests`
3. `state transition tests`
4. `differential tests`
5. `fallback tests`
6. `controller integration tests`

## 9. Remaining Risks That v8.1 Does Not Pretend To Solve

| Risk | Why it remains | Current mitigation |
|---|---|---|
| all villains collapse into one smart-bad voice | differentiation is still only as good as the comparison suite | differential tests plus retained forbidden-move boundaries |
| flavor degrades into pure copywriting | downstream consumers may ignore `structural_targets` and `state_shift_focus` | explicit structural flavor fields and flavor-focused tests |
| ledger degrades back into flat event logging | future contributors may bypass layered helpers | helper-first ownership rules and ledger boundary tests |
| scene stays too coarse | role vocabulary can still be underused | observer-topology and power-topology tests |
| recovery / upgrade / collapse stays soft | v8.1 now has explicit transition ownership, but thresholds and benchmark breadth are still not fully closed | transition helper ownership plus state-transition tests |

## 10. Audit Conclusion

The package should now be reviewable in a line-by-line way:

1. every major Claude finding has a structure owner
2. every structure owner has a validation gate
3. every validation gate has a helper owner
4. every helper owner has a test proof
5. every solved point has an explicit residual risk statement

If Claude still finds a gap after this, the next step should no longer be "argue about intent" but "point to the missing row and tighten that exact owner."
