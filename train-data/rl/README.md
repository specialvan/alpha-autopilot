# RL Training Subset

This subdirectory documents the preferred RL-oriented view of the `train-data` package.

## Purpose

Use this subset when training a reasoning-focused model to:

- classify persona structures
- match legitimacy shells
- map target gaps to primitive choices
- reason about scene fit and observer topology
- diagnose failure and repair paths
- infer transitions and upgrade paths
- enforce compatibility and hard rejection constraints
- preserve decision-trace fidelity when needed

## Recommended source files

- `../persona_cards.jsonl`
- `../shell_library.jsonl`
- `../gap_library.jsonl`
- `../primitive_library.jsonl`
- `../scene_matrix.jsonl`
- `../failure_recovery.jsonl`
- `../transition_matrix.jsonl`
- `../compatibility_edges.jsonl`
- `../thinking_trace.jsonl`
- `../evaluation_set.jsonl`

## Suggested workflow

1. Read `../dataset_schema.md`
2. Read `../manifest.json`
3. Load the relevant record family
4. Train on `../synthetic_samples.jsonl`
5. Validate on `../evaluation_set.jsonl`
6. If reasoning cadence matters, sample from `../thinking_trace.jsonl`

## Notes

- Keep structure first.
- Treat hard constraints as first-class signals.
- Use evaluation records as held-out reasoning checks.
- Use thinking traces to supervise decision order and recovery logic.
