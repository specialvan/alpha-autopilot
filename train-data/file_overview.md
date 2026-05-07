# Train Data File Overview

This file gives a concise, task-oriented view of every file in the `train-data` package.

## Read this first

- `dataset_schema.md`
- `manifest.json`
- `usage_matrix.md`
- `README.md`

---

## Core structure files

### `persona_cards.jsonl`
- Purpose: persona-level reasoning units
- Best for: RL, Wiki, LoRA
- Must-read when: classifying or comparing persona types
- Notes: contains the stable bedrock of the role model

### `shell_library.jsonl`
- Purpose: legitimacy shell records
- Best for: RL, Wiki, LoRA
- Must-read when: matching surface behavior to persona and scene
- Notes: helps preserve the difference between appearance and function

### `gap_library.jsonl`
- Purpose: target gap records
- Best for: RL, Wiki, LoRA
- Must-read when: mapping target vulnerabilities to primitive choices
- Notes: useful for hard rejection and selector reasoning

### `primitive_library.jsonl`
- Purpose: primitive / knife records
- Best for: RL, Wiki, LoRA
- Must-read when: selecting and combining primitives
- Notes: includes compatibility hints and transition effects

### `scene_matrix.jsonl`
- Purpose: scene-to-knife fit records
- Best for: RL, Wiki, LoRA
- Must-read when: judging whether a move is scene-appropriate
- Notes: includes observer topology and power topology signals

---

## Evolution and control files

### `failure_recovery.jsonl`
- Purpose: failure, recovery, upgrade, and transition records
- Best for: RL, Wiki, LoRA
- Must-read when: diagnosing failure or planning repair
- Notes: distinguishes recovery, upgrade, and collapse paths

### `transition_matrix.jsonl`
- Purpose: explicit state transition records
- Best for: RL, Wiki, LoRA
- Must-read when: supervising state machine reasoning
- Notes: useful for traceable state evolution

### `compatibility_edges.jsonl`
- Purpose: primitive compatibility graph edges
- Best for: RL, Wiki, LoRA
- Must-read when: enforcing combo constraints
- Notes: supports hard filtering and conflict detection

---

## Thinking layer

### `thinking_trace.jsonl`
- Purpose: decision order, intermediate judgments, and recovery / upgrade traces
- Best for: RL, Wiki, LoRA
- Must-read when: preserving reasoning cadence and decision style
- Notes: captures how the role thinks, not just what it does

---

## Training and evaluation files

### `training_prompts.jsonl`
- Purpose: prompt templates for synthetic sample generation
- Best for: RL, LoRA
- Must-read when: creating more synthetic data
- Notes: not usually a direct wiki reading target

### `synthetic_samples.jsonl`
- Purpose: synthetic training samples
- Best for: RL, LoRA
- Must-read when: training on structured examples
- Notes: good for supervised adaptation

### `evaluation_set.jsonl`
- Purpose: held-out evaluation records
- Best for: RL, LoRA
- Must-read when: checking model consistency after changes
- Notes: keep as a stable regression gate

---

## Index and routing files

### `manifest.json`
- Purpose: file roles, counts, and dataset navigation
- Best for: RL, Wiki, LoRA
- Must-read when: locating the right record family
- Notes: source of truth for current counts

### `usage_matrix.md`
- Purpose: consumer routing matrix
- Best for: RL, Wiki, LoRA
- Must-read when: choosing the correct downstream view
- Notes: quick chooser for file priority

### `dataset_schema.md`
- Purpose: field definitions and record family contract
- Best for: RL, Wiki, LoRA
- Must-read when: implementing parsers or adding fields
- Notes: schema authority for the package

### `README.md`
- Purpose: top-level overview and usage summary
- Best for: Wiki, RL, LoRA
- Must-read when: onboarding a new user
- Notes: human-facing starting point

---

## View folders

### `rl/README.md`
- Purpose: RL-oriented usage notes
- Best for: RL
- Must-read when: training reasoning and constraint learning

### `wiki/README.md`
- Purpose: human reference navigation notes
- Best for: Wiki
- Must-read when: building a personal knowledge base

### `lora/README.md`
- Purpose: LoRA-oriented tuning notes
- Best for: LoRA
- Must-read when: fine-tuning style and analysis order

---

## Recommended dependency order

1. `dataset_schema.md`
2. `manifest.json`
3. `usage_matrix.md`
4. `README.md`
5. core structure files
6. evolution and control files
7. thinking layer
8. training and evaluation files
9. view folders

---

## One-line summary

Use the schema and manifest first, then route by consumer: structure for RL, navigation for wiki, and prompt/sample/evaluation plus thinking-trace fidelity for LoRA.
