# Train Data Dataset

This directory contains a structured dataset for three downstream uses:

1. **RL training knowledge base**
2. **Personal wiki / reference base**
3. **LoRA style / analysis tuning**

The dataset is organized as a reusable knowledge base for analysis, retrieval, synthetic training, held-out evaluation, and thinking-trace preservation.

---

## 1. Dataset layout

### Core structure layer

- `persona_cards.jsonl` — persona-level structure records
- `shell_library.jsonl` — legitimacy shell records
- `gap_library.jsonl` — target gap records
- `primitive_library.jsonl` — primitive / knife records
- `scene_matrix.jsonl` — scene-to-knife fit records

### Evolution and control layer

- `failure_recovery.jsonl` — failure, recovery, upgrade, and transition records
- `transition_matrix.jsonl` — explicit state transition records
- `compatibility_edges.jsonl` — primitive compatibility graph edges

### Thinking and reasoning layer

- `thinking_trace.jsonl` — decision order, intermediate judgments, and recovery / upgrade traces

### Training and evaluation layer

- `training_prompts.jsonl` — prompt templates for synthetic sample generation
- `synthetic_samples.jsonl` — synthetic training samples
- `evaluation_set.jsonl` — held-out evaluation records

### Index and schema layer

- `dataset_schema.md` — schema reference for all records
- `manifest.json` — index with file roles and record counts
- `usage_matrix.md` — quick chooser for RL / Wiki / LoRA consumers
- `ROADMAP.md` — recommended expansion order and priorities

### Downstream view folders

- `rl/README.md` — RL-oriented usage view
- `wiki/README.md` — wiki-oriented usage view
- `lora/README.md` — LoRA-oriented usage view

---

## 2. Recommended usage by downstream goal

### A. RL training knowledge base

Use this layer when training a reasoning-oriented model that should understand persona, shell, gap, primitive, scene, failure, recovery, upgrade, transition, and decision-trace structure.

Recommended files:

- `persona_cards.jsonl`
- `shell_library.jsonl`
- `gap_library.jsonl`
- `primitive_library.jsonl`
- `scene_matrix.jsonl`
- `failure_recovery.jsonl`
- `transition_matrix.jsonl`
- `compatibility_edges.jsonl`
- `thinking_trace.jsonl`
- `evaluation_set.jsonl`

Recommended workflow:

1. Read `dataset_schema.md`
2. Read `manifest.json`
3. Pull the relevant record family
4. Use `synthetic_samples.jsonl` for training augmentation
5. Use `evaluation_set.jsonl` for held-out validation
6. Use `thinking_trace.jsonl` if reasoning cadence matters

### B. Personal wiki / reference base

Use this layer when you want a navigable, human-readable reference for recurring analysis patterns.

Recommended files:

- `README.md`
- `manifest.json`
- `usage_matrix.md`
- `ROADMAP.md`
- `dataset_schema.md`
- `persona_cards.jsonl`
- `shell_library.jsonl`
- `gap_library.jsonl`
- `primitive_library.jsonl`
- `scene_matrix.jsonl`
- `failure_recovery.jsonl`
- `transition_matrix.jsonl`
- `thinking_trace.jsonl`

Suggested wiki structure:

- Persona cards
- Shell library
- Gap library
- Primitive library
- Scene matrix
- Failure / recovery / upgrade
- Transition matrix
- Thinking trace
- Compatibility graph
- Prompt patterns
- Evaluation set

### C. LoRA style / analysis tuning

Use this layer when fine-tuning a model to adopt a stable structural analysis view.

Recommended files:

- `thinking_trace.jsonl`
- `training_prompts.jsonl`
- `synthetic_samples.jsonl`
- `evaluation_set.jsonl`
- selected high-quality slices from `persona_cards.jsonl`, `scene_matrix.jsonl`, and `failure_recovery.jsonl`

Recommended emphasis:

- structure-first analysis
- differential reasoning
- scene-dependent choice
- failure / repair / upgrade distinctions
- state transition reasoning
- decision-trace fidelity

---

## 3. File count snapshot

Current `manifest.json` is the source of truth for file counts and roles.

At the time of the latest manifest update, the dataset contains:

- 16 persona cards
- 15 shell records
- 21 gap records
- 14 primitive records
- 10 scene records
- 14 failure / recovery records
- 13 transition records
- 49 compatibility edges
- 20 thinking trace records
- 9 training prompt templates
- 50 synthetic samples
- 50 evaluation records

---

## 4. Maintenance notes

- Keep persona, shell, gap, primitive, scene, failure, transition, compatibility, and thinking-trace layers separate in downstream use.
- Keep `synthetic_samples.jsonl` and `evaluation_set.jsonl` aligned with the same schema family.
- Update `manifest.json` whenever record counts change.
- Update `dataset_schema.md` whenever a record family gains or loses fields.
- Update `usage_matrix.md` when the preferred consumer routing changes.
- Update `ROADMAP.md` when the expansion priorities change.

---

## 5. Suggested read order

1. `dataset_schema.md`
2. `manifest.json`
3. `usage_matrix.md`
4. `ROADMAP.md`
5. `persona_cards.jsonl`
6. `shell_library.jsonl`
7. `gap_library.jsonl`
8. `primitive_library.jsonl`
9. `scene_matrix.jsonl`
10. `failure_recovery.jsonl`
11. `transition_matrix.jsonl`
12. `compatibility_edges.jsonl`
13. `thinking_trace.jsonl`
14. `training_prompts.jsonl`
15. `synthetic_samples.jsonl`
16. `evaluation_set.jsonl`

---

## 6. One-line summary

This dataset is a structure-first role reasoning package that can be shared across RL training, wiki reference, and LoRA tuning as long as each consumer keeps the layers separate.
