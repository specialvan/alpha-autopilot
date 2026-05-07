# alpha-autopilot 仓库说明草案

更新时间：2026-05-08

## 项目概览

`alpha-autopilot` 是一个“研究导向、可解释、数据库弱依赖”的小说章节推荐与写作辅助系统。它并不是单一模型服务，而是由多层显式规则、评分、上下文装载、模拟、治理告警与工作台预览能力拼成的实验性平台。

从代码结构看，当前仓库可以按五层理解：

1. `alpha_autopilot/`
   最早的基础推荐核，负责 `StoryState -> 候选动作 -> 特征打分 -> 推荐输出`，同时提供训练、版本快照、训练日志、指标聚合。
2. `alpha_autopilot_v2/`
   V2 规则/搜索/评估/验证层，构成 `/api/v2/recommendation/preview` 的核心决策链。
3. `alpha_autopilot_v3/`
   V3 质量与留存增强层，主要提供 decomposition、retention、generation control 等能力，被 V2/V4 间接复用。
4. `alpha_autopilot_v4/` 与 `backend/app/services/narrative_v4|v6|v7|v8/`
   V4 以后开始进入关系图、角色约束、GraphRAG、事件注入、决策控制、benchmark 治理、告警升级、自动补救等增量能力。
5. `backend/` 与 `ui-react/`
   FastAPI 作为统一入口；React Workbench 与 Dashboard 作为在线消费层。

治理上，仓库自身强调：

- `v1/v2` 属于 Baseline，应该稳定收口。
- `v3` 及以后是 Increment/实验增强层。
- DeepWiki 优先应解释“主链契约和层次关系”，不要先堆砌“大而全模块说明”。

## 模块地图

### 1. 核心推荐与训练基座

- `alpha_autopilot/narrative.py`
  `StoryState`、`CharacterState`、`NarrativeCandidate`、`RecommendationResult` 的基础数据模型。
- `alpha_autopilot/feature_matrix.py`
  特征矩阵与上下文权重，含题材、节奏、阶段加权逻辑。
- `alpha_autopilot/planner.py`
  候选动作枚举与 feature 抽取。
- `alpha_autopilot/recommend.py`
  推荐结果包装、风险级别、前置条件、下一步文案、调权预览。
- `alpha_autopilot/trainer.py`
  训练样本回放、矩阵更新、value metrics 聚合。
- `alpha_autopilot/versioning.py`
  版本快照写入 `artifacts/registry.json` 与 `artifacts/matrix_vXXX.json`。
- `alpha_autopilot/training_log.py`
  训练/反馈日志落盘。
- `alpha_autopilot/repositories.py`
  历史仓储抽象，支持：
  - `FileHistoryRepository`
  - `DbHistoryRepository`
  - `FallbackHistoryRepository`
- `alpha_autopilot/storage.py`
  `artifacts/` 路径约定中心。

### 2. V2 决策与工作台

- `alpha_autopilot_v2/domain|rules|search|evaluation|validation/`
  V2 规则、搜索、评估与验证账本实现。
- `backend/app/services/narrative_v2/preview_service.py`
  V2 preview 主流程编排器。
- `backend/app/services/narrative_v2/workbench_service.py`
  Workbench 上下文源解析器，负责在线/本地/导入/live fallback 四级回退。
- `backend/app/services/narrative_v2/online_report_contexts.py`
  访问外部 PlotPilot 在线报告 API。
- `backend/app/services/narrative_v2/imported_contexts.py`
  本地报告、导入 fixture、质量记录富化、`compare_baseline` 生成。
- `docs/api/v2-workbench-real-chapter-context-contract.md`
  现有较权威的 V2 workbench context 契约。

### 3. V3 质量与留存增强

- `alpha_autopilot_v3/decomposition/`
  章节拆解、QC、projection、taxonomy。
- `alpha_autopilot_v3/retention/`
  retention vector、target function、metrics。
- `alpha_autopilot_v3/generation_control/`
  生成控制策略。

V3 在当前后端中的主要作用不是独立 API，而是作为 V2/V4 的评分增强与质量记录来源。

### 4. V4 关系图、提示压缩、可观测性与告警

- `alpha_autopilot_v4/integration/`
  V4 到 V3 的桥接结果。
- `backend/app/services/narrative_v4/bridge.py`
  关系图、角色约束、prompt 压缩、记忆摘要、genre calibration、Workbench preview 组装。
- `backend/app/services/narrative_v4/memory_store.py`
  V4 反馈/关系/runtime 指标 JSONL 持久化。
- `backend/app/services/narrative_v4/observability.py`
  V4 snapshot、trend、alerts、统一 envelope。
- `backend/app/services/narrative_v4/alert_channel.py`
  关键告警路由器，支持本地 JSONL 留痕与远程 webhook 投递。
- `backend/app/services/narrative_v4/character_validation.py`
  角色生成/自检/定向修复闭环。
- `backend/app/services/narrative_v4/prompt_compressor.py`
  prompt token 阈值压缩与约束覆盖率检测。

### 5. V6 模拟、事件注入、GraphRAG

- `backend/app/services/narrative_v6/seed_extractor.py`
  从章节文本抽取 `NarrativeSeed`。
- `backend/app/services/narrative_v6/character_parameterizer.py`
  角色画像参数化。
- `backend/app/services/narrative_v6/parallel_simulation.py`
  多路径模拟。
- `backend/app/services/narrative_v6/event_injection.py`
  在 checkpoint 上注入事件并重新排序路径。
- `backend/app/services/narrative_v6/state_store.py`
  simulation result JSONL 存储与归档轮转。
- `backend/app/services/narrative_v6/graph_rag.py`
  deterministic GraphRAG 检索。
- `backend/app/services/narrative_v6/graph_memory_store.py`
  跨会话 GraphRAG 命中记忆、压缩、审计、趋势告警。
- `backend/app/services/narrative_v6/observability.py`
  V6 runtime observability。

### 6. V7 决策控制与 benchmark 治理

- `backend/app/services/narrative_v7/market_state_adapter.py`
  把故事状态映射成 market-state 风格的统一决策输入。
- `backend/app/services/narrative_v7/decision_controller.py`
  核心 route/rule 决策器，产出 `route_id` 和 `DecisionType`。
- `backend/app/services/narrative_v7/decision_rules.py`
  默认规则集和环境变量/外部 JSON 覆盖。
- `backend/app/services/narrative_v7/benchmark_store.py`
  V7 最复杂模块：
  - benchmark ingest/query/version/restore/diff
  - maintenance alert
  - governance run
  - escalation emit
  - escalation remediation
  - 多层 auto-remediate / auto-prune / digest / export
- `backend/app/services/narrative_v7/observability.py`
  V7 runtime observability。

### 7. V8 内部状态机与 Workbench 预览

- `backend/app/services/narrative_v8/controller.py`
  villain feedback / knife selection 主控。
- `backend/app/services/narrative_v8/schemas.py`
  Control phase、control surface state、fallback action、transition/state ledger 契约。
- `backend/app/services/narrative_v8/workbench_bridge.py`
  将 V2 context 转成 V8 preview。

注意：V8 当前没有独立 FastAPI route，而是作为 `v2/workbench/contexts` 的嵌入预览输出。

### 8. API 与前端入口

- `backend/app/main.py`
  主 FastAPI app，聚合 dashboard / preview / training / feedback / history / v4 / v6 / v7。
- `backend_app.py`
  早期 demo-only FastAPI 入口。
- `ui-react/src/api.ts`
  前端消费的契约镜像，能反向帮助识别哪些接口是稳定对外面的。
- `ui-react/src/features/v2Workbench/useV2WorkbenchController.ts`
  Workbench 状态编排器，最能体现 V2/V4/V7 接口是如何被联用的。

## 入口文件

### 后端入口

- `backend/app/main.py`
  生产/主入口，当前最重要。
- `backend_app.py`
  demo API，仍可运行，但只覆盖 dashboard、基础 preview 和 V2 preview。

### 离线脚本

- `train.py`
  离线训练入口。
- `recommend.py`
  离线推荐打印入口。
- `demo.py`
  待确认：脚本引用 `TrainingExample`，当前仓库中未找到该类型定义，疑似过期入口。

### 前端入口

- `ui-react/src/main.tsx`
- `ui-react/src/App.tsx`
- `ui-react/src/router/AppRouter.tsx`

## 配置文件

- `pyproject.toml`
  Python 依赖与 Ruff 配置。
- `pytest.ini`
  pytest 启动参数。
- `.env` / `.env.local`
  `backend/app/core/config.py` 通过 `pydantic_settings` 加载。
- `backend/app/core/config.py`
  后端统一配置中心。
- `backend/app/services/narrative_v7/decision_rules.default.json`
  V7 决策规则默认文件；也可通过 `AA_V7_DECISION_RULES_JSON` 覆盖。
- `docs/api/v2-workbench-real-chapter-context-contract.md`
- `docs/api/v6-narrative-simulation-contract.md`

## 测试文件与测试重心

`tests/` 覆盖比较完整，建议 DeepWiki 优先引用这些集群，而不是平均描述全部测试：

- `test_narrative_v2_*`
  V2 API、preview service、workbench context、decision contract。
- `test_narrative_v6_*`、`test_v6_*`
  V6 API、observability、simulation store、graph memory store。
- `test_narrative_v7_*`
  V7 API 和 benchmark governance 主链。
- `test_narrative_v8_*`
  V8 controller、schemas、selection、transitions、workbench preview。
- `test_alpha_autopilot_v3_*`
  V3 decomposition / QC / retention。
- `test_run_v4_production_cycle.py`
- `test_run_v6_acceptance_review.py`
- `test_run_v7_acceptance_review.py`
- `test_run_v8_acceptance_review.py`

## 外部依赖与边界

### 代码依赖

- Python:
  - `fastapi`
  - `pydantic`
  - `pydantic-settings`
  - `uvicorn`
- Frontend:
  - `react`
  - `react-dom`
  - `react-router-dom`
  - `vite`
  - `vitest`

### 本地持久化依赖

核心推荐本身是数据库弱依赖，但“历史、治理、审计、可观测性”大量依赖本地文件：

- `artifacts/training/training_log.json`
- `artifacts/metrics/recommendation_value_metrics.json`
- `artifacts/registry.json`
- `artifacts/matrix_vXXX.json`
- `artifacts/db/history.sqlite3`
- `artifacts/history/v4_*.jsonl`
- `artifacts/history/v6_*.jsonl`
- `artifacts/history/v7_*.jsonl`

### 外部 HTTP 调用

1. `backend/app/services/narrative_v2/online_report_contexts.py`
   对 PlotPilot 在线报告 API 发起 `GET` 请求，可带 Bearer Token。
2. `backend/app/services/narrative_v4/alert_channel.py`
   对远端 IM/Webhook 目标发起 `POST` 告警投递。

### 明确未发现的能力

- 未发现入站 Webhook 路由。
- 未发现消息队列客户端或 broker 依赖。
- 未发现仓库内自带 scheduler/cron/worker 进程。
- 因此 `/auto-archive`、`/governance/run`、`/auto-remediate` 更像“给外部调度器调用的维护接口”。这一点是代码推断，不是代码内显式说明。

## 关键流程图文字版

### 流程 1：基础推荐链路

触发：
- `POST /api/recommendation/preview`
- 或 `recommend.py`

流转：
1. 构造 `StoryState`
2. `ChapterPlanner.recommend(state)`
3. `FeatureMatrix.score(state, features)`
4. `recommend_chapter()` 包装风险、前置条件、next_step
5. 预览接口再叠加 tuning weight 调整

成功分支：
- 返回推荐列表，按 score 排序

失败分支：
- 当前基础链路几乎无显式异常治理；多为 Python 异常直接抛出

依赖：
- `alpha_autopilot/feature_matrix.py`
- `alpha_autopilot/planner.py`
- `alpha_autopilot/recommend.py`

### 流程 2：训练 / 反馈 / 历史闭环

触发：
- `POST /api/training`
- `POST /api/feedback`
- `GET /api/history`

流转：
1. `NarrativeTrainingService.train()`
2. 默认样本 + 可选 projection 样本并入
3. `Trainer.fit()`
4. `VersionManager.create_version()`
5. `NarrativeWriteService.persist_training()`
6. `persist_value_metric()`
7. `HistoryService` 再从 repository 聚合 timeline / summary

成功分支：
- 产出 version、history、value metrics、top actions

失败分支：
- repository 不可写时返回 `WriteResult(ok=False, ...)`
- feedback 流中任一持久化失败则返回 `accepted=False`

依赖：
- JSON 文件
- 可选 SQLite
- V3 projection 产物

### 流程 3：V2 Preview 决策链

触发：
- `POST /api/v2/recommendation/preview`

流转：
1. `NarrativeV2StateBuilder.build()`
2. `NarrativeV2RuleService.evaluate()`
3. `NarrativeV2SearchService.search()`
4. `NarrativeV2EvaluationService.rank()`
5. `NarrativeV2ValidationService.record()`
6. best-effort `append_ledger()`
7. `build_preview_decision()`

成功分支：
- 返回 `state + rule_checks + recommendations + decision + validation`

失败分支：
- ledger 落账失败不会中断主响应，只补 `ledger_warning`
- 其他异常由 FastAPI 直接失败

依赖：
- `alpha_autopilot_v2/*`
- `alpha_autopilot_v3.retention.target_function`
- 验证账本文件

### 流程 4：V2 Workbench 上下文解析

触发：
- `GET /api/v2/workbench/contexts`
- `POST /api/v2/workbench/contexts/refresh`

流转：
1. 先尝试在线 PlotPilot 报告 API
2. 失败则尝试本地 raw report + manifest arbitration
3. 失败则回退导入 fixture
4. 再失败则构造 live fallback context
5. 对每个 context 追加：
   - `compare_baseline`
   - `v4_preview`
   - `v8_preview`

成功分支：
- 返回 `contexts[]` 与 source / run_id / diagnostics

失败分支：
- 在线模式 `online_only=true` 下，返回空 `contexts` + `fallback_reason=online-report-unavailable`

依赖：
- 外部 PlotPilot API
- 本地 report/manifest
- `v4` preview builder
- `v8` preview builder

### 流程 5：V4 预览、观测、告警

触发：
- `POST /api/v4/plot/preview`
- `POST /api/v4/workbench/preview`
- `GET /api/v4/observability/snapshot`
- `POST /api/v4/observability/alerts/route`

流转：
1. 关系历史 / 反馈历史合并
2. relationship graph input 过滤与历史写回
3. character validation loop
4. prompt 压缩
5. 生成 preview payload
6. runtime metric 写入 `v4_runtime_metrics.jsonl`
7. observability snapshot 聚合 alerts
8. critical alert 经过 cooldown 后可发到远程 webhook

成功分支：
- preview 返回候选、timeline、memory summary、genre calibration
- alert route 返回 routing 结果

失败分支：
- preview 内部异常时 Workbench Service 会包装 fallback preview
- 告警远程发送失败时降级为本地留痕，`remoteRouting.status=degraded-local-only`

依赖：
- `alpha_autopilot_v4.integration`
- 本地 JSONL memory
- 可选远程 webhook

### 流程 6：V6 模拟与事件注入

触发：
- `POST /api/narrative/v6/simulations/parallel`
- `GET /api/narrative/v6/simulations/{id}`
- `POST /api/narrative/v6/simulations/{id}/inject-event`

流转：
1. GraphRAG 检索
2. 历史 hit stitching
3. 平行模拟生成 2 到 3 条 path
4. result 落入 simulation store
5. 后续 inject-event 按 event_type 与 force_level 调整 path 分数
6. 重新排名并更新 winner

成功分支：
- 返回 simulation result / updated result

失败分支：
- simulation id 不存在时 404
- winner 为空时 route metric 记为 fallback
- GraphRAG 没有命中时 fallback 到 deterministic fallback hits

依赖：
- `v6_graph_memory.jsonl`
- `v6_simulation_results.jsonl`
- runtime metrics JSONL

### 流程 7：V7 决策控制与 benchmark 治理

触发：
- `POST /api/narrative/v7/decision/preview`
- `POST /api/narrative/v7/benchmark/ingest`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
- 以及多层 `/digest`、`/escalation/emit`、`/auto-remediate`

流转：
1. `market_state_adapter` 归一化 story_state
2. `NQMSampler.sample()` 生成指标向量
3. `DecisionFeedbackController.decide()` 根据 route rules 产出决策
4. benchmark ingest/query/versioning 在本地 version store 上运行
5. maintenance alert 判断 SLA breach
6. governance run 负责：
   - auto archive
   - archive cleanup
   - run record 写入
7. governance run digest 可给出：
   - execute_governance_run
   - retry_latest_failed_run
   - auto_prune_runs
   - escalate_failed_run
8. escalation emit 生成 escalation event
9. escalation auto-remediate / remediation auto-remediate / run-history auto-remediate 形成多层治理闭环

成功分支：
- 所有治理对象写入本地 JSONL，支持 list / summary / export / digest / prune

失败分支：
- idempotency key 冲突 -> 409
- retry 目标不存在 -> 404
- retry 目标不是 failed -> 422
- retry 次数超限 -> 422

依赖：
- `decision_rules.default.json` 或 `AA_V7_DECISION_RULES_JSON`
- 大量 `AA_V7_*` 环境变量
- benchmark/alert/governance/escalation 多份 JSONL 事件日志

## 接口契约表

以下优先保留“核心链路接口”，不是穷尽仓库中全部 URL。

### A. HTTP API

| 名称 | 文件路径 | 功能说明 | 输入参数 | 输出结果 | 前置条件 | 错误分支 | 依赖关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `GET /api/dashboard` | `backend/app/api/routes/dashboard.py` | 返回 Dashboard 基础概览与 V4 观测快照 | 无 | `DashboardResponse` | 无 | 异常直接失败 | `build_dashboard()`、`FeatureMatrix`、V4 observability |
| `POST /api/recommendation/preview` | `backend/app/api/routes/recommendation.py` | 基础推荐预览 | `PreviewRequest`：`tuningWeights[]`、`recommendations[]` | `{recommendations: [...]}` | 无 | 异常直接失败 | `alpha_autopilot.recommend.preview_recommendations` |
| `POST /api/training` | `backend/app/api/routes/training.py` | 训练特征矩阵并写版本/日志/指标 | 无 | `TrainingResult` | 本地 artifacts 可写 | 写仓储失败会体现在 message | `Trainer`、`VersionManager`、`NarrativeWriteService` |
| `POST /api/feedback` | `backend/app/api/routes/feedback.py` | 写反馈并更新指标 | `recommendationAction`、`accepted`、`score`、`notes?` | `FeedbackResult` | repository 可用 | 训练日志或指标持久化失败返回 `accepted=false` | `NarrativeFeedbackService`、SQLite/JSON |
| `GET /api/history` | `backend/app/api/routes/history.py` | 聚合训练/反馈历史 | Query: `stage?` `action?` `limit` | history logs / snapshots / timelines | 历史仓储可读 | 异常直接失败 | `HistoryRepository` |
| `POST /api/history/export` | `backend/app/api/routes/history.py` | 导出历史 JSON | 可选 target path 仅内部 service 支持，HTTP 无入参 | `{ok,path,counts}` | artifacts 可写 | 写文件失败直接抛错 | `HistoryExportService` |
| `POST /api/v2/recommendation/preview` | `backend/app/api/routes/recommendation_v2.py` | V2 决策主链 | `case_id`、`state`、`plot_unit_scaffold?` | preview payload | `state` 完整，数值在 0..1 | ledger 写入失败仅返回 `ledger_warning` | V2 rules/search/evaluation/validation |
| `GET /api/v2/workbench/contexts` | `backend/app/api/routes/workbench_v2.py` | Workbench context 读取 | 无 | `NarrativeV2WorkbenchContextsResponsePayload` | 任一 source 可用 | 若全失败则退 live fallback | PlotPilot API、本地 report、V4/V8 preview |
| `POST /api/v2/workbench/contexts/refresh` | `backend/app/api/routes/workbench_v2.py` | 强制刷新 context | Query: `online_only=false` | 同上 | source resolution 可执行 | `online_only=true` 时可能空 contexts | 同上 |
| `POST /api/v4/workbench/preview` | `backend/app/api/routes/narrative_v4.py` | V4 Workbench preview | context dict，至少要有 `state` | preview payload | `state` 存在更完整 | 缺失 `state` 时返回 fallback payload | V4 bridge、memory store |
| `GET /api/v4/observability/snapshot` | `backend/app/api/routes/narrative_v4.py` | V4 可观测性快照 | Query: `limit`、`include_alert_routing` | snapshot + 可选 alert routing | 有或无 memory rows 都可 | 无数据时 `enabled=false` | V4 memory/runtime metrics、alert channel |
| `POST /api/v4/observability/alerts/route` | `backend/app/api/routes/narrative_v4.py` | 对当前 snapshot 做告警路由 | Query: `limit` | `{routing,snapshot}` | snapshot 中存在 critical alert 才会真正路由 | cooldown、生效目标缺失、远端失败 | V4 alert channel、webhook |
| `POST /api/narrative/v6/simulations/parallel` | `backend/app/api/routes/narrative_v6.py` | 平行模拟 | `ParallelSimulationRequest` | `ParallelPlotSimulationResult` | `v6_enabled=true` | GraphRAG fallback；无 winner 记 fallback | GraphRAG、simulation store |
| `GET /api/narrative/v6/simulations/{id}` | 同上 | 读取 simulation | path `simulation_id` | simulation result | id 存在 | 不存在返回 404 | simulation store |
| `POST /api/narrative/v6/simulations/{id}/inject-event` | 同上 | 注入事件并重排 | `EventInjectionRequest` | `EventInjectionResult` | simulation 已存在 | 不存在 404；winner 为空 fallback | simulation store、EventInjectionService |
| `POST /api/narrative/v6/graph/retrieve` | 同上 | 图检索 | `query` + 可选 seed/graph/group memory | `GraphRAGRetrieveResponse` | `v6_enabled=true` | 无命中触发 fallback | deterministic GraphRAG + graph history stitching |
| `GET /api/narrative/v6/observability` | 同上 | V6 runtime 指标快照 | Query: `limit` | snapshot | `v6_enabled=true` | 无数据时 info alert | runtime metrics JSONL |
| `POST /api/narrative/v7/decision/preview` | `backend/app/api/routes/narrative_v7.py` | V7 市场态决策预览 | `text`、`story_state`、`project_state?`、`benchmark_state?`、`metric_overrides?`、`decision_state?`、`override_confirmed?` | `UnifiedDecisionPreviewResponse` | `v7_enabled=true` | 规则禁用或异常 | market adapter、sampler、decision controller |
| `POST /api/narrative/v7/benchmark/ingest` | 同上 | benchmark 样本入库 | `book_id`、`channel`、`genre_track`、`sample_payload` | `BenchmarkIngestResponse` | payload 非空且 book_id 未重复 | 空 payload=422；重复=409 | V7 benchmark store |
| `POST /api/narrative/v7/benchmark/query` | 同上 | 查询 benchmark corridor | `channel`、`genre_track` 等 | `BenchmarkQueryResponse` | 无 | 无命中时返回 fallback corridor | V7 benchmark store |
| `GET /api/narrative/v7/benchmark/versions` | 同上 | 查询版本列表 | Query: `limit` | `BenchmarkVersionListResponse` | 无 | 异常直接失败 | version store |
| `POST /api/narrative/v7/benchmark/restore/{version}` | 同上 | 恢复某版本 | path `version` | `BenchmarkRestoreResponse` | version 存在 | 404 | version store |
| `GET /api/narrative/v7/benchmark/maintenance/alert` | 同上 | 当前 SLA 告警 | Query: `limit` | `BenchmarkMaintenanceAlertResponse` | 无 | 异常直接失败 | maintenance report + SLA policy |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run` | 同上 | 执行治理 run | Query: `dry_run`、`alert_limit`、`archive_limit`、`idempotency_key`、`retry_run_id` | `BenchmarkMaintenanceAlertGovernanceRunResponse` | `v7_enabled=true` | idempotency 冲突/重试目标异常 | alert archive、cleanup、run log |
| `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest` | 同上 | 读治理 run digest | Query: `limit` | `BenchmarkMaintenanceAlertGovernanceRunDigestResponse` | 运行日志存在更有意义 | 无日志返回 observe/stale | governance runs log |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit` | 同上 | 发治理升级事件 | Query: `limit`、`ignore_cooldown` | `BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse` | digest 推荐 `escalate_failed_run` | cooldown suppress 或 no_escalation_needed | escalation event log |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate` | 同上 | 对 governance run 做自动补救 | Query: `dry_run`、`limit`、`alert_limit`、`archive_limit` | `BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse` | digest 推荐动作可执行 | dry-run / no_action / escalation_required | governance run + escalation emit + auto prune |

### B. 内部服务调用

| 名称 | 文件路径 | 功能说明 | 输入参数 | 输出结果 | 前置条件 | 错误分支 | 依赖关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `build_preview()` | `backend/app/services/narrative/preview_service.py` | 基础 preview 编排 | `PreviewRequest` | recommendations dict | base_state 可构造 | 异常上抛 | `alpha_autopilot.preview_recommendations` |
| `NarrativeV2PreviewService.build_preview()` | `backend/app/services/narrative_v2/preview_service.py` | V2 主编排器 | `NarrativeV2PreviewRequest` | 完整 preview payload | `state` 合法 | ledger 写失败仅 warning | V2 domain services |
| `NarrativeV2WorkbenchService.list_contexts()` | `backend/app/services/narrative_v2/workbench_service.py` | 解析 context source 并附加 V4/V8 preview | `include_source_diagnostics`、`online_only` | workbench contexts payload | source 可访问或 fallback 可构造 | 在线 unavailable 时 fallback | PlotPilot API、本地 report、V4/V8 |
| `build_v4_workbench_preview()` | `backend/app/services/narrative_v4/bridge.py` | 从 V2 state 派生 V4 preview | context dict | V4 preview payload | `context.state` 存在 | 返回 fallback payload | V4 integration、memory store |
| `build_v8_workbench_preview()` | `backend/app/services/narrative_v8/workbench_bridge.py` | 从 Workbench context 派生 V8 控制态预览 | context dict | V8 preview payload | preview enabled | 异常由上层包装 fallback | V8 controller |
| `GraphRAGRetriever.retrieve()` | `backend/app/services/narrative_v6/graph_rag.py` | deterministic GraphRAG | `GraphRAGRetrieveRequest` | ranked hits | query 非空 | 无命中 fallback | seed/relationship/group memory |
| `EventInjectionService.inject()` | `backend/app/services/narrative_v6/event_injection.py` | 事件注入重排 | simulation + event request | `EventInjectionResult` | simulation 已存在 | 无 winner / author intent violation | path ranking |
| `DecisionFeedbackController.decide()` | `backend/app/services/narrative_v7/decision_controller.py` | V7 route rule 决策 | `DecisionRequest` | `DecisionResponse` | vector + market_state 完整 | 异常上抛 | rule set + threshold engine |
| `V7BenchmarkStore.run_maintenance_alert_governance()` | `backend/app/services/narrative_v7/benchmark_store.py` | 治理 run 核心执行器 | `dry_run/limits/idempotency/retry` | governance run response | logs/path 可写 | 失败写 failed run record 后再抛错 | alert/archive/governance logs |

### C. 回调 / Webhook

代码结论：

- 未发现入站 callback / webhook endpoint。
- 仅发现出站 webhook 路由器。

| 名称 | 文件路径 | 功能说明 | 输入参数 | 输出结果 | 前置条件 | 错误分支 | 依赖关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V4 远程告警投递 | `backend/app/services/narrative_v4/alert_channel.py` | 将 critical alert 发往 IM/Webhook | 内部 snapshot；配置项 `v4_alert_*` | `remoteRouting` 结果 | snapshot 中有 critical alerts，且开启 remote | cooldown 抑制；missing oncall；HTTPError；降级本地留痕 | `urllib.request`、本地 sink JSONL |

出站 payload 字段来自代码，可固定为：

- `timestamp`
- `signature`
- `critical_alerts`
- `snapshot_meta`
- `oncall.contacts`

### D. 定时任务

代码结论：

- 仓库内未发现 scheduler、cron runner、Celery、RQ、APScheduler 一类定时框架。
- 下列接口具备“被外部定时器驱动”的形态，这里标记为 `[推断]`：

| 名称 | 文件路径 | 功能说明 | 输入参数 | 输出结果 | 前置条件 | 错误分支 | 依赖关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `[推断]` benchmark alert auto-archive | `backend/app/api/routes/narrative_v7.py` | 自动归档 alert 事件 | `dry_run` | `BenchmarkMaintenanceAlertAutoArchiveResponse` | alert log 存在 | no_action / dry_run | V7 alert log |
| `[推断]` governance run auto-prune | 同上 | 自动裁剪 governance run 历史 | `dry_run` | auto prune response | run log 存在 | no_action / dry_run | governance run log |
| `[推断]` governance runs auto-remediate | 同上 | 自动执行治理或升级 | `dry_run`、`limit` 等 | auto remediate response | digest 有推荐动作 | escalation_required / no_action | governance logs |
| `[推断]` escalation auto-remediate | 同上 | 自动发升级事件或裁剪 escalation 历史 | `dry_run`、`limit` | auto remediate response | escalation digest 有动作 | no_action / dry_run | escalation logs |

### E. 消息队列 / 事件

未发现 MQ/Broker，但存在大量“事件式对象 + JSONL 日志”。

优先解释这些对象，而不是笼统写成“日志文件”：

| 事件/对象 | 文件路径 | 用途 | 关键字段 |
| --- | --- | --- | --- |
| `TrainingLogEntry` | `alpha_autopilot/training_log.py` | 训练/反馈流水 | `timestamp, stage, action, predicted, target, feedback, version` |
| `MatrixSnapshot` | `alpha_autopilot/versioning.py` | 模型版本快照 | `version, created_at, weights, bias, sample_count, notes` |
| `GraphMemoryRecord` | `backend/app/services/narrative_v6/schemas.py` | GraphRAG 历史记忆命中 | `record_id, query, source_route, node_id, hidden, created_at_utc` |
| `BenchmarkMaintenanceAlertEvent` | `backend/app/services/narrative_v7/schemas.py` | benchmark 维护告警事件 | `event_id, level, should_page, breaches` |
| `BenchmarkMaintenanceAlertGovernanceRunRecord` | 同上 | 治理 run 记录 | `run_id, status, attempt, idempotency_key, performed_steps` |
| `BenchmarkMaintenanceAlertGovernanceEscalationEvent` | 同上 | 治理升级事件 | `event_id, source, escalation_reason, latest_failed_run_id` |
| `BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord` | 同上 | 升级补救 run 记录 | `run_id, action, executed, emitted, pruned` |

### F. 状态机 / 任务流转接口

| 名称 | 文件路径 | 功能说明 | 输入参数 | 输出结果 | 前置条件 | 错误分支 | 依赖关系 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V2 规则状态流转 | `backend/app/services/narrative_v2/schemas.py` | 标记动作合法性 | story state | `legal / blocked / prerequisite_missing` | state 合法 | 无显式异常 | V2 RuleService |
| V6 模拟路径状态 | `backend/app/services/narrative_v6/schemas.py` | 标记 path 成功或失败 | simulation path | `ok / failed` | path 已生成 | failed path 仍保留于结果中 | Parallel simulation |
| V7 决策路由状态 | `backend/app/services/narrative_v7/decision_controller.py` | route-based 决策分流 | market_state + vector | `DecisionType + route_id + risk_level` | vector 已采样 | override / stop_loss / repair / observe | RuleSet + ThresholdBand |
| V7 治理 run 状态 | `backend/app/services/narrative_v7/schemas.py` | 维护 run 成败 | run execution | `succeeded / failed` | governance run 执行 | 失败记录仍持久化 | benchmark store |
| V8 control surface state | `backend/app/services/narrative_v8/schemas.py` | 角色控制态转移 | villain/target/scene | `next_state`、`next_control_state` | V8 preview enabled | fallback mode | V8 controller |

V8 `ControlSurfaceState` 可固定的枚举值来自代码：

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

## 数据契约重点

### 1. 输入数据

优先文档化这些核心输入对象：

- `StoryState` / `StoryStatePayload`
- `NarrativeV2PreviewRequest`
- `NarrativeV2WorkbenchContextPayload`
- `ParallelSimulationRequest`
- `EventInjectionRequest`
- `UnifiedDecisionPreviewRequest`
- `BenchmarkIngestRequest`

### 2. 模型 / 规则

- 基础推荐模型不是黑盒 LLM，而是显式特征矩阵。
- V2 是规则 + 搜索 + 评估。
- V7 是 market-state + NQM sampler + route rules。
- V8 是 knife selection + transition state machine。

### 3. 排序结果

- 基础推荐：
  `score`, `risk_level`, `prerequisites`, `next_step`
- V2：
  `rule_checks`, `recommendations`, `decision.selected_action`
- V6：
  `paths[].retention_score`, `winner_path_id`
- V7：
  `decision.route_id`, `decision.decision_type`, `risk_level`

### 4. 最终输出

- 在线 Workbench 最终对前端最重要的是：
  - `contexts[]`
  - `v4_preview`
  - `v8_preview`
  - `decision`
  - `history timelines`

## 推荐的文档优先级

DeepWiki 和团队协作第一批应优先写：

1. `backend/app/main.py` 的路由分层与版本边界
2. `backend/app/services/narrative_v2/*` 的 preview 与 workbench contract
3. `backend/app/services/narrative_v4/*` 的 observability、alert routing、memory store
4. `backend/app/services/narrative_v6/*` 的 simulation / GraphRAG / event injection
5. `backend/app/services/narrative_v7/*` 的 benchmark governance 与 auto-remediate 家族

可以略写的部分：

- `alpha_autopilot/board.py`、`eval.py`、`search.py`、`engine.py`
  这些更像早期中国象棋示例遗留，与当前小说推荐主链关联弱。
- `demo.py`
  疑似过期。

## DeepWiki repo notes

1. `backend/app/main.py` 是主入口；当前最重要的对外契约不是根目录脚本，而是 `/api`、`/api/v2`、`/api/v4`、`/api/narrative/v6`、`/api/narrative/v7` 这五组路由。
2. 解释仓库时请把 `alpha_autopilot/` 视为基础推荐核，把 `alpha_autopilot_v2/v3/v4` 视为增量算法层，再把 `backend/app/services/` 视为这些算法层的编排与暴露层。
3. 文档优先级应放在“推荐链路、工作台上下文装载、事件注入、benchmark 治理、告警升级”，而不是先平铺每个工具模块。
4. `backend/app/services/narrative_v2/workbench_service.py` 是核心关系节点：它连接在线 PlotPilot 报告、本地报告、导入 fixture、live fallback，并嵌入 `v4_preview` 与 `v8_preview`。
5. 仓库没有内建 MQ、没有内建 scheduler、没有入站 webhook；很多“治理/自动补救”接口实际上是给外部调度器调用的 HTTP maintenance endpoints，这是理解系统边界的关键。
6. `backend/app/services/narrative_v4/alert_channel.py` 只负责出站 webhook 投递；`backend/app/services/narrative_v2/online_report_contexts.py` 是另一处真实外部 HTTP 调用，二者应单独解释依赖与失败回退。
7. `backend/app/services/narrative_v6/` 是事件化最明显的一层：simulation store、GraphRAG history、event injection、audit snapshot、observability 都是可落盘、可复盘对象。
8. `backend/app/services/narrative_v7/benchmark_store.py` 是复杂度最高的治理模块，应按“版本库、维护告警、governance run、escalation、remediation、auto-remediate 链”分段解释，不要试图一次性平铺全部 50+ 路径。
9. `ui-react/src/api.ts` 可作为前端稳定消费契约镜像；当源码关系复杂时，可优先用它确认哪些响应字段已经被 UI 依赖。
10. `docs/api/v2-workbench-real-chapter-context-contract.md` 与 `docs/api/v6-narrative-simulation-contract.md` 是现有最接近权威契约的文档，应优先引用并与代码对齐。

## 待补充项清单

1. `demo.py` 当前引用 `TrainingExample`，代码内未找到定义，需确认是过期脚本还是缺失迁移。
2. `backend_app.py` 与 `backend/app/main.py` 的职责边界建议补一页显式说明，避免 DeepWiki把 demo API 误判成主服务。
3. 需要单独梳理 `artifacts/history/` 下 V4/V6/V7 各 JSONL 文件名、对象 schema、保留策略、归档规则。
4. V7 auto-remediate 家族存在多层递归命名路径，建议由团队确认哪些属于长期保留接口，哪些属于中间实验接口。
5. 如需给新同学看，建议新增“在线流程 vs 离线流程”分界文档，明确：
   - 在线：dashboard、preview、workbench、simulation preview、decision preview
   - 离线：training、benchmark ingest、alert/governance/prune/remediate
6. 需要补充一页“异常兜底与默认值”说明，尤其是：
   - V2 context source fallback
   - V4 preview fallback
   - V6 GraphRAG fallback
   - V7 governance digest 推荐动作
7. 需要补一页“配置项索引”，至少覆盖：
   - PlotPilot API
   - V4 alert / compression / genre guard
   - V6 store / graph memory / observability
   - V7 decision rules / governance / archive / stale threshold

## 强调事项

这个仓库最值得优先讲清楚的不是“大模块列表”，而是下面四条贯穿链：

- 推荐链路：输入状态 -> 规则/特征/评分 -> 排序结果 -> 最终推荐
- 任务调度：虽然仓库内无 scheduler，但存在大量可被外部调度的治理、归档、自动补救接口
- 策略选择：V2 的规则搜索评估、V7 的 route-based decision、V8 的 knife selection 都属于策略层
- 执行反馈：feedback、history、GraphRAG history、benchmark alert/governance/escalation 共同构成复盘对象

以及三组容易被忽略的边界：

- 输入数据、模型/规则、排序结果、最终输出要分层描述，不要混在一个接口说明里。
- 在线/离线流程需要明确切开，避免把治理维护接口误认为线上实时主链。
- 异常兜底、默认值、配置项必须跟契约一起写，否则 DeepWiki 很容易误读字段语义和模块关系。
