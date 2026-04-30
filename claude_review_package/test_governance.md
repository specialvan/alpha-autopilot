# Test Governance

This project uses path-based test layers so we can run the right slice of the suite without scattering markers across existing tests.

## Layers

| Layer | Purpose | Command |
| --- | --- | --- |
| `core` | Pure domain and pipeline logic | `pytest tests/test_alpha_autopilot_v2_domain.py tests/test_alpha_autopilot_v3_pipeline.py tests/test_alpha_autopilot_v3_taxonomy_and_models.py tests/test_narrative_v3_projection_bridge.py` |
| `quality` | Regression, golden-case, and validation coverage | `pytest tests/test_alpha_autopilot_v2_golden_cases.py tests/test_alpha_autopilot_v2_rule_fixtures_runtime.py tests/test_alpha_autopilot_v2_validation_assets.py tests/test_alpha_autopilot_v2_validation_ledger.py tests/test_alpha_autopilot_v3_build_script.py tests/test_alpha_autopilot_v3_retention_metrics.py tests/test_alpha_autopilot_v3_qc_report.py tests/test_narrative_training_service_projection.py` |
| `api` | Backend routing, service wiring, and preview endpoints | `pytest tests/test_narrative_v2_api.py tests/test_narrative_v2_app_wiring.py tests/test_narrative_v2_backend_app_route.py tests/test_narrative_v2_decision_contract.py tests/test_narrative_v2_preview_service.py tests/test_narrative_v2_services.py tests/test_narrative_v2_workbench_context_api.py` |
| `frontend` | React/Vitest coverage in `ui-react` | `npm test -- src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/characterInterviewPanel.test.tsx src/features/v2Workbench/contextMapping.test.ts src/features/v2Workbench/session.test.ts src/pages/V2WorkbenchPage.test.tsx src/router/AppRouter.test.tsx` |
| `import` | PlotPilot import and imported-context conversion | `pytest tests/test_alpha_autopilot_v3_plotpilot_import.py tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_quality_enrichment.py` |
| `v6` | Dynamic narrative simulation gates | `pytest tests/test_narrative_seed_extractor.py tests/test_character_parameterizer.py tests/test_parallel_plot_simulation.py tests/test_emergent_conflict_probe.py tests/test_event_injection_checkpoint.py tests/test_character_interview.py tests/test_group_memory_layer.py tests/test_graph_rag_retrieval.py tests/test_v6_graph_memory_store.py tests/test_v6_state_store.py tests/test_narrative_v6_observability.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py` |

## Runner

Use `scripts/run_layered_tests.py` to print and run one or more layers:

```bash
python scripts/run_layered_tests.py core quality
python scripts/run_layered_tests.py api
python scripts/run_layered_tests.py frontend import
python scripts/run_layered_tests.py v6 api
```

The script resolves each layer to an explicit command and prints it before execution.

## Rules

- Prefer layer selection over broad `pytest` runs when you are validating a change.
- Keep the layer map path-based. Do not add markers unless a future change truly needs them.
- Add new tests to the narrowest layer that still reflects the behavior under test.
- If a change crosses boundaries, run every affected layer rather than moving tests around.

## Notes

- `frontend` runs from `ui-react/`.
- The repo root is the default working directory for the Python layers.
- This document should stay in sync with `scripts/run_layered_tests.py`.
