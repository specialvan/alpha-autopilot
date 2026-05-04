# V8 Claude Review Summary

## Overall Judgment

The v8 proposal is directionally correct and materially stronger than a simple "model a villain" approach. The three-layer abstraction is sound:

- knife primitive layer
- villain cognition layer
- scene mapping layer

However, the current package is **not yet implementation-tight**. It is conceptually complete, but several boundaries are still too soft for a reliable first implementation.

The most important gap is that the design still risks collapsing back into a single shared villain voice unless constraint modeling, state layering, and selection reasoning are made more explicit.

## P0 Findings

### P0-1 State ledger is too flat for long-line control

The current `StateLedger` tracks useful deltas, but it does not yet distinguish between:

- relationship state
- narrative state
- psychological echo state
- hook / deferred payoff state

Without this separation, the system will have trouble supporting memory rewrite, long-line payoff, and hook recovery.

**Recommendation:** split the ledger into layered sub-structures instead of one flat delta object.

---

### P0-2 Knife constraints are not explicit enough

`preferredKnives`, `secondaryKnives`, and `forbiddenMoves` are useful, but they are not sufficient by themselves. The system also needs explicit modeling for:

- scene restrictions
- target restrictions
- flavor incompatibilities
- knife-to-knife incompatibilities
- conditions under which a knife is ineffective or backfires

**Recommendation:** add a dedicated constraint / compatibility model rather than relying only on arrays of strings.

---

### P0-3 `VillainFeedbackPacket` is too narrative-heavy and not structured enough

The packet is a good start, but it currently reads like a result summary rather than a fully consumable control packet.

Missing or underdefined elements include:

- structured selection signals
- rejected knife reasons
- explicit fit scores
- multiple future hooks as first-class output

**Recommendation:** split the output into a decision layer and an explanation layer.

## P1 Findings

### P1-1 Flavor concepts are scattered across too many places

Flavor is currently represented in multiple places:

- `VillainProfile.flavorAxes`
- `FlavorRender`
- `publicMask`
- `privateDrive`

This creates a risk that flavor becomes a diffuse concern rather than a single source of truth.

**Recommendation:** define a stable flavor axis in the profile, and reserve `FlavorRender` for the output instance only.

---

### P1-2 `TargetProfile` needs stronger computational detail

The target model is good but still too coarse for precise knife selection.

Useful additions:

- defense style
- witness sensitivity
- identity anchor

These help distinguish whether a target breaks under privacy, public pressure, praise, humiliation, or old-wound activation.

---

### P1-3 `SceneContext` needs observer topology and power structure detail

A simple `audience` list is not enough.

The scene needs to know whether observers are:

- witnesses
- judges
- transmitters
- buffers
- future recovery nodes

**Recommendation:** enrich the scene model with observer roles and power topology.

---

### P1-4 Implementation plan is missing validation gates between schema and controller

The plan currently moves too directly from structure into controller composition.

Missing intermediate steps:

- schema constraint validation
- knife compatibility testing
- state delta boundary checks
- differential tests for same knife / different villain
- differential tests for same villain / different scene

**Recommendation:** add explicit validation and differential testing before controller assembly.

## P2 Findings

### P2-1 Naming can be unified further

The naming is good overall, but the abstraction level of some terms is uneven.

**Recommendation:** keep stable entities as `Profile` / `Context`, behavioral units as `Primitive`, results as `Packet`, and evolving state as `Ledger` or `Snapshot`.

---

### P2-2 A negative-style layer may be useful later

Some villains are differentiated not by what they do, but by what they refuse to do.

Potential future extension:

- avoidance primitives
- negative style markers

This is not required for v8, but it will help later with high-contrast villain voices.

---

### P2-3 Current testing is too happy-path oriented

Single scene tests are not enough.

Add coverage for:

- same knife, different villain
- same villain, different scene
- fallback behavior when no knife fits
- failure-mode behavior when visibility, audience, or pressure conditions change

## Recommended Schema Revisions

### Keep

- `KnifePrimitive`
- `VillainProfile`
- `TargetProfile`
- `SceneContext`
- `VillainFeedbackPacket`

### Add or strengthen

- explicit knife constraint / compatibility model
- layered state ledger
- structured selection reasons
- observer topology in scene context
- multiple future hooks as first-class output

## Recommended Execution-Order Revision

Use this order:

1. schema + validation rules
2. knife library + compatibility graph
3. scoring / selection helpers
4. flavor rendering
5. state ledger application
6. controller orchestration

Do not treat the controller as the place to discover missing business rules.

## Risk Summary

The dominant risks are:

1. all villains collapsing into the same smart-bad-person voice
2. flavor becoming cosmetic instead of behavioral
3. state ledger degrading into a flat event log
4. scene mapping being too coarse to preserve nuanced knife behavior

## Bottom Line

v8 is a good direction, but it needs one more engineering tightening pass before implementation.

The right next step is **v8.1 revision**, not direct build-out from the current draft.
