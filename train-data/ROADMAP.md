# Train Data Roadmap

This document describes the recommended expansion order for the `train-data` package.

The goal is to preserve structure-first reasoning while improving training quality, evaluation strength, and wiki usability.

---

## Priority levels

- **P0** — highest priority, directly improves usefulness
- **P1** — recommended next, clearly valuable
- **P2** — optional enhancement, useful but not urgent

---

## P0 — Must do first

### 1. Expand `thinking_trace.jsonl`

Why this matters:

- preserves decision cadence and reasoning style
- helps LoRA learn analysis order, not just final labels
- gives RL a richer trace of intermediate judgments

Recommended additions:

- same persona, different scene
- same scene, different persona
- same conclusion, different reasoning path
- incorrect judgment followed by correction
- recovery and upgrade decision traces

---

### 2. Add harder cases to `evaluation_set.jsonl`

Why this matters:

- held-out evaluation should test real generalization
- difficult cases reveal whether the model actually learned structure

Recommended additions:

- close persona pairs
- close shell pairs
- close primitive pairs
- failure / recovery boundary cases
- transition boundary cases

---

### 3. Expand `compatibility_edges.jsonl`

Why this matters:

- selector reliability depends on a more complete compatibility graph
- hard constraints reduce false positives in knife selection

Recommended additions:

- more conditional relations
- three-step combination conflicts
- scene-dependent compatibility
- shell-dependent compatibility

---

## P1 — Strongly recommended

### 4. Add more `synthetic_samples.jsonl`

Why this matters:

- increases training coverage
- fills gaps in task diversity

Recommended additions:

- error -> correction
- structure extraction -> second-stage judgment
- scene judgment -> follow-up inference
- transition inference -> recovery analysis

---

### 5. Add example-index documents for each layer

Why this matters:

- improves wiki usability
- makes quick browsing easier

Possible files:

- `persona_examples.md`
- `shell_examples.md`
- `gap_examples.md`
- `primitive_examples.md`
- `scene_examples.md`

---

### 6. Add concept-contrast notes

Why this matters:

- clarifies boundaries between similar concepts
- reduces semantic drift over time

Possible files:

- `persona_vs_shell.md`
- `gap_vs_primitive.md`
- `failure_vs_transition.md`

---

## P2 — Optional enhancement

### 7. Preserve more raw decision texture

If you want to keep the flavor of the original reasoning, add more traces that capture:

- hesitation
- test moves
- rollback
- shell swapping
- second-pass judgment

This deepens the `thinking_trace` layer.

---

### 8. Make the scene matrix more granular

Possible additions:

- more detailed public-scene authority structures
- more detailed semi-public circle dynamics
- more detailed private dependence patterns

---

### 9. Expand persona families further

If you want broader coverage later, add more:

- persona cards
- shell / gap mappings
- upgrade paths

---

## Recommended expansion order

1. `thinking_trace.jsonl`
2. `evaluation_set.jsonl`
3. `compatibility_edges.jsonl`
4. `synthetic_samples.jsonl`
5. example-index documents
6. concept-contrast documents
7. deeper scene / persona expansion

---

## Summary

Start with thinking traces and hard evaluation cases, then strengthen the compatibility graph and synthetic samples, and only after that add wiki-style indices and contrast notes.
