# LoRA Style / Analysis Tuning Subset

This subdirectory documents the LoRA-oriented view of the `train-data` package.

## Purpose

Use this subset when fine-tuning a model to adopt a stable structural analysis style for fictional character reasoning.

The goal is not surface imitation alone, but a consistent internal order of analysis:

1. persona bedrock
2. legitimacy shell
3. target gap
4. primitive / knife choice
5. scene fit
6. failure mode
7. repair path
8. upgrade trigger
9. state transition
10. decision-trace fidelity

## Recommended source files

- `../thinking_trace.jsonl`
- `../training_prompts.jsonl`
- `../synthetic_samples.jsonl`
- `../evaluation_set.jsonl`
- selected slices from `../persona_cards.jsonl`
- selected slices from `../shell_library.jsonl`
- selected slices from `../gap_library.jsonl`
- selected slices from `../primitive_library.jsonl`
- selected slices from `../scene_matrix.jsonl`
- selected slices from `../failure_recovery.jsonl`
- selected slices from `../transition_matrix.jsonl`

## Suggested training emphasis

- structure-first analysis
- consistent reasoning order
- differential comparison between similar personas
- scene-dependent primitive selection
- repair versus upgrade distinction
- honest fallback versus forced interpretation
- state transition reasoning
- decision-trace fidelity

## Suggested sample mix

- 35% structure extraction
- 15% scene judgment
- 15% failure diagnosis
- 10% upgrade inference
- 10% transition inference
- 10% thinking trace imitation
- 5% persona comparison

## Notes

- Avoid training only on stylistic outputs.
- Keep labels aligned with the shared schema family.
- Use `evaluation_set.jsonl` as a held-out quality gate.
- Use `thinking_trace.jsonl` to preserve the reasoning cadence, not just the final answer.
