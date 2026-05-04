# 项目进度表

## 当前阶段

- 项目名称：小说章节智能推荐引擎
- 目标目录：`D:\workspace\alpha-autopilot`
- 当前状态：`v2` 推荐工作台已独立落地，`V3` 已建立读者留存目标函数与生成控制层，`V4` 已进入生产级工程化推进（以可回滚、可观测、可验收为门禁）
- 执行模式：`V4` 生产周期单任务推进（`V4_PRODUCTION_CYCLE_TASK_BOARD.md`）
- 当前激活任务：`T04` 远端告警通道（已验收）
- 下一任务候选：`T05` 灰度与回滚流程
- `V6` 增量状态：PR-AA-09 至 PR-AA-15 已全部完成并通过门禁，`T01~T08` 全部 `ACCEPTED`

## 进度清单

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 叙事状态模型 | 已完成 | 已具备 `StoryState`、`CharacterState`、规则/搜索/评估基础抽象 |
| 特征矩阵原型 | 已完成 | 已具备训练、版本、日志、历史聚合基础 |
| `v2` 核心域 | 已完成 | `alpha_autopilot_v2` 已具备 rule / search / evaluation / validation |
| `v2` API | 已完成 | 已提供 `/api/v2/recommendation/preview` 与 `/api/v2/workbench/contexts` |
| `v2` 前端工作台 | 已完成 | 已从嵌入式实验面板升级为独立 `V2 Workbench` 路由 |
| PlotPilot 测试资产迁移 | 已完成 | 已迁入本地 `.env.local` 与测试样本，生成 workbench contexts |
| `V3` taxonomy / schema | 已完成 | 已冻结章节功能、style DNA、checkpoint 基础契约 |
| `V3` heuristic decomposition pipeline | 已完成 | 已支持章节拆解、evidence span、checkpoint、admission 分级 |
| `V3` PlotPilot report import | 已完成 | 已支持从 PlotPilot report 转换为 `reverse_outline_records` |
| `V3` 本地构建脚本 | 已完成 | 已支持生成 `reverse_outline_records.jsonl` 与 `matrix_projection.json` |
| `V3` 留存目标函数 | 进行中 | 正在把“留住读者”抽象成顶层目标函数 |
| `V3` 生成控制层 | 进行中 | 正在把情绪、节奏、爽点等标签转成生成决策变量 |
| `V4` 人物关系驱动剧情 | 进行中 | 已落地关系分析与张力评分工程实现（可测试 / 可回滚） |
| `V4` 人物性格驱动选择 | 进行中 | 已落地性格偏好分析、压力响应工程实现与题材校准接口 |
| `V4` 外部压力驱动爆发 | 进行中 | 已落地压力源建模与强度指数工程实现 |
| `V4` API 与桥接契约 | 进行中 | 已提供 `/api/v4/plot/preview`、`/api/v4/workbench/preview` 与 `v4_enabled` 回滚开关 |
| `V4` 跨章节关系位移跟踪 | 进行中 | 已支持 `relationship_history` 驱动 displacement events 与 graph summary |
| `V4` 留存反馈动态回写 | 进行中 | 已支持 `v3_feedback_history` 驱动 retention 权重自适应 |
| `V4` live 历史反馈注入 | 进行中 | `V2` live workbench context 已自动从 history snapshots 注入反馈样本 |
| `V4` 跨会话记忆存储 | 进行中 | 已落地 `v4_relationship_memory.jsonl` / `v4_feedback_memory.jsonl` 持久化回读 |
| `mapped_chapter` 真实章节上下文 contract | 进行中 | `/api/v2/workbench/contexts` 已优先读取 PlotPilot raw `report.json`，输出 `real_chapter_context_v1` 与章节级 `compare_baseline` |
| `v2` workbench contexts API 显式契约 | 已完成 | 路由已声明 `response_model`，OpenAPI 可见 `NarrativeV2WorkbenchContextsResponsePayload` |
| `V6` PR-AA-09 小说种子结构化提取器 | 已完成 | 已新增 `NarrativeSeed` schema、deterministic extractor、关系图兼容输出与 `needs_review` 门禁 |
| `V6` PR-AA-10 文本驱动自动人设参数化 | 已完成 | 已新增 `ParameterizedCharacterProfile` 自动推断、override 优先生效与 evidence/override_log 输出 |
| `V6` PR-AA-11 多路径并行推演 | 已完成 | 已新增 2~3 路并行推演、单路径失败隔离、winner 留存排序、simulation 查询与持久化回放存储 |
| `V6` P1 交互增强（AA-12~14） | 已完成 | 已落地冲突探针、事件注入重算、角色访谈接口与风险标记 |
| `V6` P2 群体记忆层（AA-15） | 已完成 | 已落地群体传播、章节过滤、hidden 抑制、reversible patch |

## 当前已知风险

- `mapped_chapter` 已从聚合式来源升级为本地 raw report 驱动 contract，但尚未接入线上真实章节服务 API
- `V3` 的留存目标函数如果实现成单一模板规则，可能重新导向八股文
- `V4` 如果直接落成固定桥段库，会失去“剧情自然长出来”的核心价值
- `matrix_projection` 已可导出，但尚未正式接入现有训练主链路
- 前端 dashboard 与 workbench 已分离，但 dashboard 仍保留较多原型式展示面板
- V4 记忆衰减/去噪、题材自动学习守护回退、可观测趋势与告警已落地首版，并已支持按题材分桶阈值配置、远端 IM/Webhook 告警路由与 on-call 校验

## 最新验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q` -> `26 passed`
- `python scripts/run_layered_tests.py v4` -> 通过
- `python scripts/run_layered_tests.py quality api import` -> 通过
- `python scripts/run_layered_tests.py frontend import v4` -> 通过
- `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py tests/test_narrative_v2_workbench_quality_enrichment.py tests/test_narrative_v2_workbench_context_api.py -q` -> `25 passed`
- `pytest tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_quality_enrichment.py -q` -> `16 passed`
- `python scripts/run_layered_tests.py api import frontend` -> 通过
- `python scripts/run_layered_tests.py api import v4 frontend` -> 通过
- `python scripts/run_layered_tests.py` -> 通过（core/quality/api/frontend/import/v4 全层）
- `python scripts/run_claude_acceptance_review.py` -> 通过（产出 `artifacts/acceptance/claude-acceptance-20260426T065834Z.md`）
- `python scripts/run_v4_production_cycle.py T01` -> 通过（产出 `artifacts/production_cycles/t01/v4-t01-20260426T142211Z.md`）
- `python scripts/run_v4_production_cycle.py T02` -> 通过（产出 `artifacts/production_cycles/t02/v4-t02-20260426T143039Z.md`）
- `python scripts/run_v4_production_cycle.py T03` -> 通过（产出 `artifacts/production_cycles/t03/v4-t03-20260426T144055Z.md`）
- `python scripts/run_v4_production_cycle.py T04` -> 通过（产出 `artifacts/production_cycles/t04/v4-t04-20260426T145418Z.md`）
- `npm test` -> `16 passed`（layered frontend）
- `npm run build` -> 成功
- `pytest tests/test_narrative_seed_extractor.py tests/test_character_parameterizer.py tests/test_parallel_plot_simulation.py tests/test_emergent_conflict_probe.py tests/test_event_injection_checkpoint.py tests/test_character_interview.py tests/test_group_memory_layer.py tests/test_v6_state_store.py tests/test_narrative_v6_api.py tests/test_run_layered_tests.py -q` -> `24 passed`
- `python scripts/run_layered_tests.py v6` -> 通过（V6 20 passed）
- `npm --prefix ui-react test -- src/features/v2Workbench/backendContexts.test.ts src/features/v2Workbench/characterInterviewPanel.test.tsx src/features/v2Workbench/contextMapping.test.ts src/features/v2Workbench/session.test.ts src/pages/V2WorkbenchPage.test.tsx src/router/AppRouter.test.tsx` -> `6 files passed, 18 tests passed`
- `python scripts/run_layered_tests.py v6 api v4 frontend` -> 通过（V6 18 passed + API 24 passed + V4 38 passed + Frontend 18 passed）
- `python scripts/run_layered_tests.py v4` -> 通过（V4 38 passed）

## 下一步计划

1. 把 `V3` 留存目标函数正式接入代码层
2. 把 `V3` 生成控制层接入现有生成/推荐链路
3. 把 `V4` 的人物关系 / 性格 / 压力模型继续细化为可配置模块接口
4. 将当前本地 report 驱动的真实章节 contract 扩展为线上真实章节服务 API（替换文件源）
5. 为 V4 题材自动学习守护策略补线上配置项（阈值可调、灰度开关）
6. 进入 `T05`：固化灰度放量条件、回退触发条件与回滚脚本演练证据
7. 进入 `V6.1`：推进 GraphRAG 接入、持久化归档策略与线上可观测门禁

## V6.1 Update (2026-04-28)

- Task board: `claude_review_package/V6/V6_IMPLEMENTATION_TASK_BOARD.md` moved to `T10 ACCEPTED`.
- Scope delivered: simulation JSONL rotation/archival replay + V6 runtime observability thresholds (`latencyP95Ms`, `errorRate`, `fallbackRate`).
- New API: `GET /api/narrative/v6/observability`.
- New acceptance script: `python scripts/run_v6_acceptance_review.py`.
- Evidence:
  - `pytest tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py tests/test_v6_state_store.py tests/test_narrative_v6_observability.py tests/test_narrative_v6_api.py -q` -> `18 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 27 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - acceptance report: `artifacts/acceptance/v6-acceptance-20260428T135155Z.md`

## V6.1 GraphRAG Update (2026-04-28)

- Task board moved to `T11 ACCEPTED` with GraphRAG retrieval integration.
- Added deterministic retrieval service and API route: `POST /api/narrative/v6/graph/retrieve`.
- Integrated GraphRAG hints into simulation paths and character interview evidence outputs.
- Evidence:
  - `pytest tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py tests/test_graph_rag_retrieval.py tests/test_parallel_plot_simulation.py tests/test_character_interview.py tests/test_narrative_v6_api.py -q` -> `22 passed`
- `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 33 + API 24 + V4 38 + Frontend 18 passed`
- `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260428T141803Z.md`
- `npm --prefix ui-react run build` -> `build success`

## V6.1 Cross-Session Graph Memory Update (2026-04-28)

- Task board moved to `T12 ACCEPTED` with cross-session graph memory stitching.
- Added persistent graph memory store: `backend/app/services/narrative_v6/graph_memory_store.py`.
- Integrated stitched retrieval into:
  - `/api/narrative/v6/graph/retrieve`
  - `/api/narrative/v6/simulations/parallel`
  - `/api/narrative/v6/characters/{character_id}/interview`
- Retrieval response now exposes:
  - `history_recall_used`
  - `stitched_from_history_count`
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` -> `19 passed`
  - `python scripts/run_layered_tests.py v6` -> `36 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 36 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260428T144920Z.md`

## V6.1 Stitching Policy Hardening Update (2026-04-28)

- Task board moved to `T13 ACCEPTED`.
- Added configurable graph memory retrieval policy:
  - `v6_graph_memory_max_age_hours` (TTL)
  - `v6_graph_memory_chapter_window`
  - `v6_graph_memory_source_weights_json`
- `PersistentGraphMemoryStore` now applies:
  - max-age filtering for stale records
  - chapter-window filtering
  - source-route weight scoring
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` -> `22 passed`
  - `python scripts/run_layered_tests.py v6` -> `39 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 39 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260428T150658Z.md`

## V6.1 Semantic-Drift Guard + Memory Compaction Update (2026-05-01)

- Task board moved to `T14 ACCEPTED`.
- Added semantic-drift guard via `v6_graph_memory_min_token_overlap`.
- Added graph memory compaction:
  - removes expired records
  - removes duplicate summary/source/hidden rows
  - rewrites `artifacts/history/v6_graph_memory.jsonl`
- New API: `POST /api/narrative/v6/graph/memory/compact`.
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_narrative_v6_api.py -q` -> `15 passed`
  - `python scripts/run_layered_tests.py v6` -> `42 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 42 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260430T160849Z.md`

## V6.1 Graph Memory Audit Snapshot Update (2026-05-01)

- Task board moved to `T15 ACCEPTED`.
- Added read-only graph memory audit snapshots:
  - total/active/expired/hidden row counts
  - duplicate group count
  - chapter min/max bounds
  - source route and node type distributions
  - active policy and latest records
- New API: `GET /api/narrative/v6/graph/memory/audit`.
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_narrative_v6_api.py -q` -> `17 passed`
  - `python scripts/run_layered_tests.py v6` -> `44 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 44 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260430T161748Z.md`

## V6.1 Graph Memory Audit Snapshot Persistence Update (2026-05-01)

- Task board moved to `T16 ACCEPTED`.
- Added persisted graph memory audit snapshots:
  - `POST /api/narrative/v6/graph/memory/audit/snapshot`
  - `GET /api/narrative/v6/graph/memory/audit/history`
- Snapshot history is stored in `artifacts/history/v6_graph_memory_audit.jsonl` and trimmed by `v6_graph_memory_audit_max_rows`.
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_narrative_v6_api.py -q` -> `19 passed`
  - `python scripts/run_layered_tests.py v6` -> `46 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 46 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260430T162412Z.md`

## V6.1 Graph Memory Audit Trend Alerts Update (2026-05-01)

- Task board moved to `T17 ACCEPTED`.
- Added graph memory audit trend alerts:
  - expired row rate
  - duplicate group count
  - active row drop rate
- New API: `GET /api/narrative/v6/graph/memory/audit/alerts`.
- Evidence:
  - `pytest tests/test_v6_graph_memory_store.py tests/test_narrative_v6_api.py -q` -> `21 passed`
  - `python scripts/run_layered_tests.py v6` -> `50 passed`
  - `python scripts/run_layered_tests.py v6 api v4 frontend` -> `V6 50 + API 24 + V4 38 + Frontend 18 passed`
  - `npm --prefix ui-react run build` -> `build success`
  - `python scripts/run_v6_acceptance_review.py` -> report `artifacts/acceptance/v6-acceptance-20260430T163049Z.md`

## V5->V6/V7 Alignment Cycle Closeout (2026-05-01)

- Alignment task board `claude_review_package/V5/V5_V6_V7_ALIGNMENT_PR_REQUIREMENTS_2026_05_01.md` completed through `A08 ACCEPTED`.
- Delivered in this cycle:
  - A02: V5 retention desire keys -> V6 retention vector compatibility mapping.
  - A03: V5/V2 six-step scaffold contract bridged into V6 simulation input/output.
  - A04: StoryState -> NarrativeMarketState adapter (`/api/narrative/v7/market-state/adapt`).
  - A05: Unified decision preview route (`/api/narrative/v7/decision/preview`).
  - A06: Shared observability envelope (`unifiedEnvelope`, schema `obs-envelope.v1`) across V4/V6/V7.
  - A07: Workbench V6/V7 orchestration UI entry integrated with V7 preview route.
  - A08: Full-chain backend/frontend regression and build closeout.
- Final evidence:
  - `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `106 passed`
  - `npm --prefix ui-react run test` -> `7 files passed, 20 tests passed`
  - `npm --prefix ui-react run build` -> `build success`

## V8.2 Villain Feedback Control Core Update (2026-05-05)

- Status: `V8.1` standalone core has been tightened into a `V8.2` runtime-aligned increment control core under `backend/app/services/narrative_v8/`.
- Boundary kept intact:
  - no dedicated V8 route registration
  - no baseline dashboard or recommendation-path replacement
  - only controlled enrichment on existing `/api/v2/workbench/contexts`
  - no `writer` or LLM invocation
  - no persistence coupling
  - no default-path impact on existing `v1/v2/v4/v6/v7`
- Delivered modules:
  - `schemas.py`
  - `knife_library.py`
  - `constraints.py`
  - `selection.py`
  - `flavor.py`
  - `ledger.py`
  - `fallbacks.py`
  - `transition_policy.py`
  - `transitions.py`
  - `controller.py`
  - `BuildVillainFeedbackOutput.build_followup_scene(...)` handoff path in `schemas.py`
- Delivered engineering gates:
  - focused V8 pytest suite under `tests/test_narrative_v8_*.py`
  - layered gate `python scripts/run_layered_tests.py v8`
  - acceptance report script `python scripts/run_v8_acceptance_review.py`
- First external consumer wiring:
  - `backend/app/services/narrative_v8/workbench_bridge.py`
  - `backend/app/services/narrative_v2/workbench_service.py`
  - `backend/app/services/narrative_v2/schemas.py` (`v8_preview`)
  - `backend/app/core/config.py` (`v8_workbench_enabled`)
- Evidence:
  - `pytest tests/test_narrative_v8_workbench_preview.py tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_workbench_quality_enrichment.py tests/test_run_layered_tests.py tests/test_run_v8_acceptance_review.py -q` -> `22 passed`
  - `python scripts/run_layered_tests.py api import v8` -> `api: 24 passed`, `import: 20 passed`, `v8: 84 passed`
  - `python scripts/run_v8_acceptance_review.py` -> report `artifacts/acceptance/v8-acceptance-20260504T185216Z.md`
- Residual guard items:
  - transition thresholds are now locked into explicit topology-gated policy rules, and benchmark breadth now covers public-network upgrade, private-recovery fallback, and disabled rollback workbench paths, but broader topology coverage is still bounded
  - `next_control_state` and `build_followup_scene(...)` now feed a first external consumer through `/api/v2/workbench/contexts` `v8_preview`, gated by `v8_workbench_enabled`, but broader caller adoption still needs guardrails
  - controller/helper boundaries are now guarded by delegate, transition pass-through, workbench preview, and integration regression tests, but future consumers still need to preserve those owners
- Rollback / impact note:
  - V8 remains isolated from baseline recommendation and default runtime paths.
  - Current rollback remains trivial because the only wired caller is workbench preview enrichment and it can be disabled through `v8_workbench_enabled`.
