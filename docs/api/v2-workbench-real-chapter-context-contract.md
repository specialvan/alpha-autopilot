# V2 Workbench Real Chapter Context Contract

Updated: 2026-04-25

## Endpoint

- `GET /api/v2/workbench/contexts`
- `POST /api/v2/workbench/contexts/refresh`
- Route response model: `NarrativeV2WorkbenchContextsResponsePayload`

## Source Priority

The backend resolves `mapped_chapter` contexts in this order:

1. Online PlotPilot report API (`PLOTPILOT_REPORT_API_URL`, optional)
2. Latest PlotPilot raw chapter report (`raw/model_switch_tests/**/report.json`)
3. Imported fixture contexts (`workbench_contexts.json`)
4. Live fallback context derived from local state + history snapshots

## Top-Level Response

```json
{
  "contexts": [],
  "source": "plotpilot_report",
  "context_contract": "real_chapter_context_v2",
  "report_path": "D:/.../report.json",
  "run_id": "v3_20260421_220604",
  "manifest_path": "D:/.../manifest.json",
  "preferred_model": "gpt-5.4",
  "resolved_model": "gpt-5.4",
  "report_success_rate": 1.0,
  "report_timestamp": "2026-04-21T16:13:33.767178",
  "arbitration_strategy": "manifest-model-success-rate-v1"
}
```

- `contexts`: required, array of chapter contexts
- `source`: optional, current source tag (for report path this is `plotpilot_report`)
- `source=plotpilot_api` indicates an online API report source
- `context_contract`: optional, current explicit contract version (`real_chapter_context_v2`)
- `report_path`: optional, resolved raw report path when source is report-driven
- `report_url`: optional, resolved online report URL when source is API-driven
- `run_id`: optional, decomposition manifest run id when arbitration matched a manifest
- `manifest_path`: optional, resolved manifest path that contributed run arbitration
- `preferred_model`: optional, preferred benchmark model used during arbitration
- `resolved_model`: optional, model from the selected report
- `report_success_rate`: optional, success / total from selected report
- `report_timestamp`: optional, selected report timestamp
- `arbitration_strategy`: optional, fixed strategy id for report selection
- `fallback_reason`: optional, populated when `online_only=true` refresh cannot reach online source
- `source_diagnostics`: optional, includes source probe status (for example online fetch status / error type)
  - online diagnostics may include:
    - `attempts_count`
    - `max_attempts`
    - `retried`
    - `retry_exhausted`
    - `attempt_history[]`

## Refresh Semantics

- `POST /api/v2/workbench/contexts/refresh` forces a fresh source resolution pass.
- Query parameter `online_only=true` enforces online source:
  - if online source is unavailable, response returns `contexts=[]` with `fallback_reason=online-report-unavailable`
  - diagnostics remain available under `source_diagnostics.online_report`

## Online Source Configuration

- `PLOTPILOT_REPORT_API_URL`: online report endpoint URL (optional)
- `PLOTPILOT_REPORT_API_KEY`: bearer token for online report endpoint (optional)
- `PLOTPILOT_REPORT_API_TIMEOUT_SECONDS`: per-attempt timeout
- `PLOTPILOT_REPORT_API_MAX_ATTEMPTS`: retry attempt cap (includes first attempt)
- `PLOTPILOT_REPORT_API_BACKOFF_SECONDS`: exponential backoff base delay in seconds

## Context Object

Each item in `contexts` follows:

```json
{
  "id": "plotpilot-chapter-02",
  "chapterNumber": 2,
  "title": "guest from medicine valley",
  "stage": "opening",
  "summary": "PlotPilot ...",
  "state": {
    "chapter_index": 2,
    "stage": "opening",
    "mainline_progress": 0.19,
    "sideplot_progress": 0.264,
    "conflict_intensity": 0.649,
    "emotional_temperature": 0.5607,
    "pacing_speed": 0.5527,
    "foreshadowing_load": 0.276,
    "payoff_pressure": 0.272,
    "characters": {},
    "tags": ["plotpilot_import", "opening"]
  },
  "compare_baseline": {
    "baseline_context_id": "plotpilot-chapter-01",
    "baseline_chapter_number": 1,
    "delta": {
      "mainline_progress": 0.095,
      "payoff_pressure": 0.066
    }
  },
  "v4_preview": {}
}
```

## `compare_baseline` Rules

- Present from chapter 2 onward in a sequential source bundle.
- Baseline is the previous context in the resolved chapter order.
- `delta` is computed over numeric state fields:
  - `mainline_progress`
  - `sideplot_progress`
  - `conflict_intensity`
  - `emotional_temperature`
  - `pacing_speed`
  - `foreshadowing_load`
  - `payoff_pressure`

## Compatibility Notes

- Existing `state`, quality enrichment fields (`admission`, `primary_function`, `style_dna`, `checkpoints`, `quality_notes`) and `v4_preview` remain backward compatible.
- Route uses `response_model_exclude_none=True`; optional metadata keys are omitted when unavailable.
