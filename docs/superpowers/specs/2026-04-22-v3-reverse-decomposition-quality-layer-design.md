# V3 Reverse Decomposition Quality Layer Design

**Date**: 2026-04-22

## 1. Goal

Add a `V3` quality layer in front of feature-matrix training and recommendation prompting so that chapter reverse-decomposition data becomes evidence-anchored, taxonomy-stable, quality-gated, and reusable across training and runtime guidance.

This layer is not a prose beautifier. It is a structured decomposition pipeline that converts raw chapter text into reliable machine-consumable assets.

## 2. Why This Exists

`alpha-autopilot` currently benefits from clearer `v2` recommendation abstractions, but the upstream decomposition quality is still weakly governed. If reverse-decomposition outputs are inconsistent, subjective, or weakly evidenced, the downstream feature matrix will learn unstable patterns and produce unreliable explanations.

The reverse-engineering of the `huashu-bookwriter` workflow revealed a repeatable production system built from:

1. trust anchors
2. structured progression paths
3. style DNA
4. TDD-like quality gates
5. strict agent execution discipline

Those ideas should not be copied literally from technical-book writing into fiction, but they do directly inspire a stronger chapter decomposition system for `V3`.

## 3. Product Positioning

This `V3` layer should be treated as:

**a decomposition quality system**

not as:

- a replacement for `v2`
- a literary commentary engine
- a generic summarizer
- a writing-style mimic system

Its job is to produce reliable decomposition records that can improve:

- feature matrix training inputs
- prompt-time recommendation hints
- validation and audit quality

## 4. Non-Goals

Out of scope for this phase:

- direct chapter generation
- live multi-agent book writing
- full authoring workflow replacement
- exporting books or presentation formats
- style imitation for output prose

This phase only concerns decomposition quality and dataset integrity.

## 5. V3 Architectural Role

The new layer sits between raw story text and downstream learning or prompting.

Pipeline:

`raw chapter text -> reverse decomposition -> QC -> graded approval -> training/prompt assets`

The important change is that raw chapter text should no longer flow directly into training-oriented interpretation without a governed decomposition pass.

## 6. Core Design Principles

### 6.1 Evidence Before Assertion

Every non-trivial decomposition judgment must point back to evidence in the chapter text.

Evidence should be represented as:

- quoted span or range reference
- structural location
- confidence or certainty indicator when needed

This prevents high-level labels from drifting into unsupported opinion.

### 6.2 Taxonomy Before Freeform Labels

The system must freeze a finite taxonomy for chapter functions, structure beats, style axes, and quality checkpoints before scaling dataset collection.

Freeform descriptors can be retained in notes, but training-grade labels must come from the frozen taxonomy.

### 6.3 Quality Gates Before Dataset Admission

A decomposition record is not automatically training-worthy just because an agent produced it.

Records must pass quality checks first.

### 6.4 Separate Human Readability from Machine Utility

The system should emit:

1. human-readable decomposition reports
2. machine-consumable structured records

The structured record is primary for dataset value.

### 6.5 Anti-Rationalization by Design

The system must explicitly guard against common agent shortcuts and “close enough” justifications.

This is a first-class requirement, not a documentation extra.

## 7. Decomposition Workflow

The `V3` decomposition workflow is a fixed six-stage pipeline:

### 7.1 Ingest

Parse and segment chapter input into:

- chapter identity
- paragraph blocks
- dialogue-heavy regions
- event-like segments
- candidate scene boundaries

### 7.2 Classify

Assign a primary narrative function and optional secondary functions.

Example primary function categories:

- hook-opening
- conflict-escalation
- information-reveal
- payoff-delivery
- transition-breathing
- pre-climax-loading
- climax-execution
- closing-consolidation

### 7.3 Decompose

Extract chapter structure into explicit fields:

- chapter goal
- opening hook
- escalation beats
- reversal or reveal
- emotional return
- ending hook
- adjacency to previous and next chapter

### 7.4 Extract Style DNA

Summarize along controlled style axes rather than vague aesthetic praise.

Candidate axes:

- pace
- exposition density
- dialogue reliance
- emotional directness
- sensory density
- conflict sharpness
- hook aggression
- payoff explicitness

### 7.5 Run Quality Checkpoints

Evaluate decomposition quality using fiction-specific checkpoints, not generic prose criteria.

### 7.6 Emit Structured Output

Emit both:

- a readable reverse-outline report
- a structured decomposition record

## 8. Required V3 Assets

This layer should freeze four new asset families.

### 8.1 Reverse Outline Records

Per chapter, store:

- chapter metadata
- narrative function labels
- structure decomposition
- style DNA
- checkpoint results
- downstream workbench context

### 8.2 Evidence Span Records

Per judgment, store:

- referenced span or segment id
- label being justified
- confidence level when inference is not explicit

### 8.3 Checkpoint Reports

Per chapter, store:

- chapter QC result
- failed or mixed checkpoints
- remediation notes

### 8.4 Corpus Quality Reports

Per dataset batch, store:

- distribution of taxonomy labels
- agent disagreement or drift flags
- style-axis skew
- low-confidence concentration
- admission status

## 9. Taxonomy Requirements

`V3` must freeze taxonomies before large-scale ingestion.

At minimum, freeze:

### 9.1 Chapter Function Taxonomy

The core chapter role in the story system.

### 9.2 Structure Beat Taxonomy

The kinds of beats extracted within a chapter.

### 9.3 Style DNA Axis Set

The bounded set of style attributes that may appear in decomposition records.

### 9.4 Quality Checkpoint Taxonomy

The stable names and meanings of all decomposition QC rules.

## 10. Trust Anchors for Fiction Decomposition

The technical-book insight of “time-line anchors” should be adapted into fiction as:

- chapter-function anchors
- scene anchors
- evidence anchors

In this project, trust should not come from “the analyst sounds confident.” It should come from traceable alignment between decomposition claims and chapter evidence.

Examples:

- “This chapter is classified as conflict-escalation because scenes 2 and 4 each raise stakes and narrow available exits.”
- “The ending hook is anchored by the unresolved threat in the final exchange.”

## 11. Style DNA Requirements

The style DNA layer must be:

- bounded
- discriminative
- evidence-aware
- useful for downstream recommendation and prompting

It must not collapse into generic praise such as:

- “good pacing”
- “strong characterization”
- “well written”

Instead, it should produce usable distinctions such as:

- fast pace with low exposition
- medium dialogue reliance with hard conflict edges
- explicit emotional release with high payoff signaling

## 12. Chapter-Level Quality Gates

Each chapter decomposition must pass a chapter QC checklist before entering the approved training pool.

Recommended chapter QC domains:

1. chapter identity completeness
2. primary function clarity
3. structure decomposition completeness
4. evidence span sufficiency
5. style DNA specificity
6. continuity stability assessment
7. conflict progression assessment
8. emotional reward assessment
9. foreshadow / payoff balance assessment
10. function-stage fit assessment
11. read-through drive assessment
12. machine-output schema validity

Each checkpoint should resolve to:

- pass
- mixed
- fail

with explicit reason text.

## 13. Corpus-Level Quality Gates

Dataset-level QC must exist in addition to chapter QC.

Recommended corpus QC domains:

1. taxonomy coverage balance
2. overuse of generic labels
3. evidence span coverage rate
4. low-confidence record concentration
5. style axis drift
6. chapter-function / stage mismatch frequency
7. agent disagreement rate
8. repeated-output template collapse
9. schema validity rate
10. approved / provisional / rejected distribution

## 14. Admission States

Decomposition outputs must be graded before use.

Use three states:

- `approved`
- `provisional`
- `rejected`

Policy:

- `approved` may enter the main training pool
- `provisional` may be retained for analysis or review but not main training
- `rejected` must not enter learning pipelines

## 15. Rationalization Table Requirement

The system must contain a maintained rationalization table to prevent agent shortcut behavior.

Its role is to explicitly reject common justifications such as:

- “This chapter is too mixed to classify”
- “The evidence is obvious from the whole chapter”
- “Style DNA is inherently subjective”
- “The checkpoint does not matter if the summary looks good”
- “This is close enough for training”

For each rationalization, the system must define:

- the shortcut claim
- why it is invalid
- the required corrective action

This table should be referenced by:

- the decomposition skill
- reviewer prompts
- batch validation logic

## 16. Agent Protocol

The decomposition process must be executed with a constrained protocol.

Required order:

1. read and segment source text
2. identify evidence anchors
3. classify chapter function
4. decompose structure
5. extract style DNA
6. run chapter QC
7. emit structured output

Agents must not skip directly to final JSON output.

## 17. Downstream Effects on Feature Matrix Quality

This layer should improve feature matrix quality in three concrete ways.

### 17.1 More Stable Labels

Frozen taxonomy plus QC should reduce category drift.

### 17.2 More Reliable Feature Signals

Evidence-anchored decomposition should reduce hallucinated or vague upstream labels.

### 17.3 Better Runtime Guidance

Style DNA and checkpoint outcomes can improve prompt-time recommendation hints, not just training records.

## 18. V2 / V3 Boundary

This work belongs to `V3`, not `V2`.

Reason:

- `v2` is the calibration baseline and should remain focused on recommendation abstractions and minimal validation
- this new quality layer expands upstream decomposition rigor, dataset governance, and feature quality
- it is a future capability that strengthens learning and prompt quality rather than the `v2` baseline itself

`V2` may consume the resulting better contexts, but it should not be redefined around this system.

## 19. V3 Requirement Statement

Add the following explicit requirement to `V3`:

> Build a Reverse Decomposition Quality Layer that converts raw chapter text into evidence-anchored, taxonomy-frozen, QC-gated decomposition records before those records are admitted into feature-matrix training or prompt-time context generation.

## 20. Recommended Implementation Order

1. Freeze the decomposition taxonomy
2. Define the structured record schema
3. Implement evidence-span extraction rules
4. Implement chapter QC
5. Implement corpus QC
6. Add admission-state logic
7. Integrate style DNA into training and prompt pipelines
8. Add rationalization-table-backed review enforcement

## 21. Final Recommendation

The reverse-decomposition quality layer should be accepted as a formal `V3` development requirement.

Without it, upstream decomposition remains too weakly governed for consistent high-quality feature-matrix learning. With it, the project gains an auditable bridge between raw chapter text and reliable training-grade narrative signals.
