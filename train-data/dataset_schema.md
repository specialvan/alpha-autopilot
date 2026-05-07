# Dataset Schema

This dataset uses JSONL records. One object per line.

## Common fields

Most records share these fields:

- `id`: unique string identifier
- `name`: human-readable label
- `source`: evidence or provenance note
- `tags`: array of short classification labels
- `summary`: short structural summary
- `notes`: additional review notes

## 1. Persona card

File: `persona_cards.jsonl`

Fields:

- `id`
- `name`
- `core_wound`
- `core_need`
- `core_fear`
- `time_horizon`
- `control_preference`
- `fear_structure`
- `psychology_literacy`
- `default_failure_mode`
- `legitimacy_shells`
- `best_gaps`
- `best_arenas`
- `upgrade_bias`
- `state_path`

## 2. Shell library

File: `shell_library.jsonl`

Fields:

- `id`
- `name`
- `surface_behavior`
- `perceived_identity`
- `actual_function`
- `best_scene_types`
- `collapse_triggers`
- `misread_risks`
- `best_target_gaps`
- `compatible_personas`

## 3. Gap library

File: `gap_library.jsonl`

Fields:

- `id`
- `name`
- `target_signal`
- `best_knives`
- `best_scenes`
- `required_observer_roles`
- `failure_if_absent`
- `hard_rejection_conditions`

## 4. Primitive library

File: `primitive_library.jsonl`

Fields:

- `id`
- `name`
- `mechanism`
- `surface_action`
- `hidden_intent`
- `best_gaps`
- `best_personas`
- `best_scenes`
- `cost`
- `failure_condition`
- `recovery_path`
- `upgrade_trigger`
- `transition_effect`
- `compatibility`

## 5. Scene matrix

File: `scene_matrix.jsonl`

Fields:

- `id`
- `scene_type`
- `visibility`
- `observer_roles`
- `power_topology`
- `time_pressure`
- `best_personas`
- `best_shells`
- `best_primitives`
- `bad_primitives`
- `cost`
- `failure_condition`
- `recovery_path`
- `upgrade_trigger`
- `transition_effect`

## 6. Failure / recovery / upgrade / transition

File: `failure_recovery.jsonl`

Fields:

- `id`
- `failure_type`
- `trigger`
- `immediate_response`
- `repair_strategy`
- `repair_cost`
- `repair_limit`
- `upgrade_trigger`
- `upgrade_path`
- `collapse_threshold`
- `state_from`
- `state_to`
- `notes`

## 7. Explicit state transitions

File: `transition_matrix.jsonl`

Fields:

- `id`
- `state_from`
- `state_to`
- `trigger`
- `visibility_change`
- `trust_change`
- `narrative_change`
- `psychological_change`
- `hook_change`
- `recovery_or_upgrade`
- `best_personas`
- `best_scenes`
- `notes`

## 8. Compatibility graph edges

File: `compatibility_edges.jsonl`

Fields:

- `left`
- `right`
- `relation`
- `reason`

## 9. Training prompts

File: `training_prompts.jsonl`

Fields:

- `id`
- `task_type`
- `prompt`
- `expected_output_schema`
- `evaluation_focus`
- `notes`

## 10. Synthetic training samples

File: `synthetic_samples.jsonl`

Fields:

- `id`
- `task_type`
- `input`
- `output`
- `notes`

## 11. Held-out evaluation set

File: `evaluation_set.jsonl`

Fields:

- `id`
- `task_type`
- `input`
- `expected`
- `metrics`
- `notes`

## 12. Thinking trace

File: `thinking_trace.jsonl`

Fields:

- `id`
- `persona_id`
- `scene_id`
- `target_gap`
- `current_state`
- `observation_order`
- `intermediate_judgments`
- `risk_checks`
- `recovery_check`
- `upgrade_check`
- `decision_point`
- `final_action`
- `state_transition`
- `notes`

## Suggested state labels

- `harmless`
- `suspicious`
- `distrusted`
- `repair_attempt`
- `partially_restored`
- `upgraded`
- `more_hidden`
- `stronger`
- `hardened`
- `collapsed`

## Suggested scene labels

- `private_intimate`
- `semi_public_familiar`
- `public_social`
- `resource_competition`
- `power_obedience`
- `long_term_companionship`
- `nightlife_party`
- `old_relationship_return`
- `competitive_audience`
- `conversion_harvest`
