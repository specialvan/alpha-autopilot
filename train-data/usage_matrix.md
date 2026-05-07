# Train Data Usage Matrix

This file summarizes which dataset files to read first, what each file is for, and which downstream consumer should prefer it.

## Legend

- **RL** — reasoning-oriented training / constraint learning
- **Wiki** — human reference and knowledge navigation
- **LoRA** — style / analysis tuning

---

| File | Layer | Primary purpose | Best for | Read first? |
|---|---|---|---|---|
| `dataset_schema.md` | Index / schema | Field definitions and record family contract | RL, Wiki, LoRA | Yes |
| `manifest.json` | Index / schema | File roles, counts, and dataset navigation | RL, Wiki, LoRA | Yes |
| `README.md` | Index / overview | Top-level dataset orientation | Wiki, RL, LoRA | Yes |
| `persona_cards.jsonl` | Core structure | Persona-level reasoning units | RL, Wiki, LoRA | Yes |
| `shell_library.jsonl` | Core structure | Legitimacy shell matching | RL, Wiki, LoRA | Yes |
| `gap_library.jsonl` | Core structure | Target gap mapping | RL, Wiki, LoRA | Yes |
| `primitive_library.jsonl` | Core structure | Primitive / knife selection and compatibility | RL, Wiki, LoRA | Yes |
| `scene_matrix.jsonl` | Core structure | Scene fit and observer topology reasoning | RL, Wiki, LoRA | Yes |
| `failure_recovery.jsonl` | Evolution / control | Failure, repair, upgrade, collapse logic | RL, Wiki, LoRA | Yes |
| `transition_matrix.jsonl` | Evolution / control | Explicit state transitions | RL, Wiki, LoRA | Yes |
| `compatibility_edges.jsonl` | Evolution / control | Hard constraint graph for knife combinations | RL, Wiki, LoRA | Yes |
| `thinking_trace.jsonl` | Thinking / reasoning | Decision order, intermediate judgments, and trace fidelity | RL, Wiki, LoRA | Yes |
| `training_prompts.jsonl` | Training / evaluation | Prompt templates for sample generation | RL, LoRA | No |
| `synthetic_samples.jsonl` | Training / evaluation | Generated supervised training examples | RL, LoRA | After schema |
| `evaluation_set.jsonl` | Training / evaluation | Held-out validation and regression checks | RL, LoRA | After schema |
| `rl/README.md` | View folder | RL-oriented usage notes | RL | Optional |
| `wiki/README.md` | View folder | Human reference notes | Wiki | Optional |
| `lora/README.md` | View folder | LoRA-oriented tuning notes | LoRA | Optional |

---

## Recommended reading order by consumer

### RL

1. `dataset_schema.md`
2. `manifest.json`
3. `persona_cards.jsonl`
4. `shell_library.jsonl`
5. `gap_library.jsonl`
6. `primitive_library.jsonl`
7. `scene_matrix.jsonl`
8. `failure_recovery.jsonl`
9. `transition_matrix.jsonl`
10. `compatibility_edges.jsonl`
11. `thinking_trace.jsonl`
12. `training_prompts.jsonl`
13. `synthetic_samples.jsonl`
14. `evaluation_set.jsonl`

### Wiki

1. `README.md`
2. `manifest.json`
3. `dataset_schema.md`
4. `persona_cards.jsonl`
5. `shell_library.jsonl`
6. `gap_library.jsonl`
7. `primitive_library.jsonl`
8. `scene_matrix.jsonl`
9. `failure_recovery.jsonl`
10. `transition_matrix.jsonl`
11. `compatibility_edges.jsonl`
12. `thinking_trace.jsonl`

### LoRA

1. `dataset_schema.md`
2. `manifest.json`
3. `thinking_trace.jsonl`
4. `training_prompts.jsonl`
5. `synthetic_samples.jsonl`
6. `evaluation_set.jsonl`
7. selected slices from structure files as needed

---

## Decision rules

- If you need **hard reasoning**, start with the structure and control layers.
- If you need **human navigation**, start with the wiki view.
- If you need **style tuning**, start with prompts, synthetic samples, evaluation, and then the thinking-trace layer.
- If you need **consistency checks**, always use `evaluation_set.jsonl` after model changes.
- If you need **decision-style fidelity**, read `thinking_trace.jsonl` before sample generation.

---

## One-line summary

Read the schema and manifest first, then choose the layer according to the task: structure for RL, navigation for wiki, and prompt/sample/evaluation plus thinking-trace fidelity for LoRA.
