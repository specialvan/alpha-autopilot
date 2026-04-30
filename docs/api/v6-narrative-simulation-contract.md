# V6 Narrative Simulation API Contract

## Scope

This document defines the V6 API contract delivered for `PR-AA-09` to `PR-AA-15`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/narrative/v6/seed/extract` | Extract `NarrativeSeed` from chapter text |
| `POST` | `/api/narrative/v6/characters/parameterize` | Build `ParameterizedCharacterProfile[]` |
| `POST` | `/api/narrative/v6/simulations/parallel` | Run 2-3 parallel simulation paths |
| `GET` | `/api/narrative/v6/simulations/{id}` | Fetch stored simulation result |
| `POST` | `/api/narrative/v6/conflicts/probe` | Run emergent conflict probe rounds |
| `POST` | `/api/narrative/v6/simulations/{id}/inject-event` | Inject event at simulation checkpoint and re-rank |
| `POST` | `/api/narrative/v6/characters/{id}/interview` | Character interview (voice/motive/risk probing) |
| `POST` | `/api/narrative/v6/group-memory/apply` | Apply group memory propagation and reversible patches |
| `POST` | `/api/narrative/v6/graph/retrieve` | Deterministic GraphRAG retrieval over seed/relations/group memory |
| `POST` | `/api/narrative/v6/graph/memory/compact` | Compact persisted GraphRAG history memory |
| `GET` | `/api/narrative/v6/graph/memory/audit` | Return read-only GraphRAG history memory audit snapshot |
| `POST` | `/api/narrative/v6/graph/memory/audit/snapshot` | Persist current graph memory audit snapshot |
| `GET` | `/api/narrative/v6/graph/memory/audit/history` | Return persisted graph memory audit snapshot history |
| `GET` | `/api/narrative/v6/graph/memory/audit/alerts` | Return graph memory audit trend alerts |
| `GET` | `/api/narrative/v6/observability` | Return V6 runtime metrics snapshot and threshold alerts |

## Contract Notes

- All endpoints are deterministic-first and testable without live LLM dependencies.
- Parallel simulation isolates failed paths; one failed path does not fail the whole batch.
- Event injection response includes ranking changes, macro risks, and audit logs.
- Character interview response includes transcript plus OOC and hidden-info risk flags.
- Group memory apply response includes propagation logs and reversible patches.
- Graph retrieve response includes ranked hits, retrieval mode, and fallback reason.
- Graph retrieve response now includes cross-session stitching telemetry:
  - `history_recall_used: bool`
  - `stitched_from_history_count: int`
  - `retrieval_mode` can be `deterministic_stitched` when history recall contributes hits.
- History stitching policy is configurable via backend settings:
  - `v6_graph_memory_max_age_hours` (TTL)
  - `v6_graph_memory_chapter_window`
  - `v6_graph_memory_min_token_overlap`
  - `v6_graph_memory_compaction_max_rows`
  - `v6_graph_memory_audit_max_rows`
  - `v6_graph_memory_audit_expired_rate_threshold`
  - `v6_graph_memory_audit_duplicate_groups_threshold`
  - `v6_graph_memory_audit_active_drop_rate_threshold`
  - `v6_graph_memory_source_weights_json`
- Graph memory compaction removes expired and duplicate records, rewrites `v6_graph_memory.jsonl`, and returns `before/after/removed`.
- Graph memory audit is read-only and returns row counts, expired/hidden/duplicate counters, chapter bounds, source/type distribution, active policy, and latest record summaries.
- Graph memory audit snapshots are persisted to `artifacts/history/v6_graph_memory_audit.jsonl` and trimmed by `v6_graph_memory_audit_max_rows`.
- Graph memory audit alerts are read-only trend checks over persisted audit history for expired-row rate, duplicate groups, and active-row drop.
- Default simulation persistence is file-backed at `artifacts/history/v6_simulation_results.jsonl`.
- Simulation persistence supports row/size-based rotation with date-bucketed archive replay under `artifacts/history/v6_simulation_archive/`.
- Runtime observability metrics are persisted at `artifacts/history/v6_runtime_metrics.jsonl`.
- Cross-session GraphRAG memory is persisted at `artifacts/history/v6_graph_memory.jsonl`.
- Parallel simulation paths and character interview responses can carry GraphRAG hints for auditability.

## Compatibility

- V6 routes are additive and do not replace V2/V4 routes.
- V2 Workbench baseline behavior remains unchanged.
- V6 can be consumed incrementally by UI features (current minimum: Character Interview panel).
