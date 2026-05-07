# HTTP API 合同

更新时间：2026-05-08

## 说明

本页只固定最关键、最值得 DeepWiki 优先解释的 HTTP 契约，不尝试把所有 V7 长尾路由平铺成一张大表。对于没有显式 schema 的接口，文档会注明 `[推断]` 或 `待确认`。

## 1. 主入口与范围

- 主入口：`backend/app/main.py`
- 当前统一挂载：
  - `/api`
  - `/api/v2`
  - `/api/v4`
  - `/api/narrative/v6`
  - `/api/narrative/v7`

## 2. Baseline：在线推荐、训练、反馈、历史

| 接口 | 文件 | 功能 | 输入 | 输出 | 前置条件 | 错误分支 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `GET /api/dashboard` | `backend/app/api/routes/dashboard.py` | 返回 Dashboard 总览与 V4 可观测性快照 | 无 | `DashboardResponse` | 无 | 异常直接失败 | `build_dashboard()`、基础推荐核、V4 observability |
| `POST /api/recommendation/preview` | `backend/app/api/routes/recommendation.py` | baseline 推荐预览 | `PreviewRequest` | `{recommendations:[...]}` | `base_state()` 可构造 | 异常直接失败 | `preview_recommendations()`、`FeatureMatrix` |
| `POST /api/training` | `backend/app/api/routes/training.py` | 训练基础矩阵并写版本、日志、指标 | 无请求体 | `TrainingResult` | 本地 artifacts 可写 | 持久化失败体现在返回消息或异常 | `Trainer`、`VersionManager`、`NarrativeWriteService` |
| `POST /api/feedback` | `backend/app/api/routes/feedback.py` | 写反馈并更新指标 | `recommendationAction/accepted/score/notes` | `FeedbackResult` | repository 可写 | 任一持久化失败则 `accepted=false` | `NarrativeFeedbackService`、训练日志、value metrics |
| `GET /api/history` | `backend/app/api/routes/history.py` | 查询训练/反馈历史 | Query: `stage/action/limit` | history 聚合对象 | repository 可读 | 异常直接失败 | training logs、value metrics |
| `POST /api/history/export` | `backend/app/api/routes/history.py` | 导出训练日志和价值指标 | 无请求体 | `{ok,path,counts}` | 导出目录可写 | 写盘失败抛异常 | `HistoryExportService` |

### 补充说明

- `POST /api/training` 没有请求体，训练样本由服务内部默认样本和可选 V3 projection 样本组成。
- `POST /api/feedback` 中 `predicted` 值不是前端传入字段，而是服务内部按 `accepted/score` 推导。
- `[推断]` `POST /api/recommendation/preview` 当前没有消费 `recommendations` 入参，只消费调权列表。

## 3. V2：Workbench 上下文与推荐预览

| 接口 | 文件 | 功能 | 输入 | 输出 | 前置条件 | 错误分支 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `POST /api/v2/recommendation/preview` | `backend/app/api/routes/recommendation_v2.py` | V2 推荐预览主链 | `NarrativeV2PreviewRequest` | `state + rule_checks + recommendations + decision + validation` | `case_id` 与 `state` 合法 | ledger 写失败只警告，不中断主响应 | `NarrativeV2PreviewService`、V2 rule/search/evaluation/validation |
| `GET /api/v2/workbench/contexts` | `backend/app/api/routes/workbench_v2.py` | 读取 Workbench contexts | 无 | `NarrativeV2WorkbenchContextsResponsePayload` | 任一来源可读，或 live fallback 可构造 | 全部失败时退到 live fallback | 在线 PlotPilot、本地 report、导入 fixture、V4/V8 preview |
| `POST /api/v2/workbench/contexts/refresh` | 同上 | 刷新 contexts | Query: `online_only=false` | 同上 | 同上 | `online_only=true` 且在线不可用时可返回空 contexts + fallback 原因 | 同上 |

### V2 关键流程

1. `preview`：`state build -> rule evaluate -> search -> evaluation -> validation -> best-effort ledger`
2. `workbench contexts`：`在线 PlotPilot -> 本地 report -> 导入 fixture -> live fallback`
3. `contexts` 返回后，会继续嵌入：
   - `v4_preview`
   - `v8_preview`
   - `compare_baseline`
   - `quality/source_diagnostics`

## 4. V4：预览、可观测性、告警路由

| 接口 | 文件 | 功能 | 输入 | 输出 | 前置条件 | 错误分支 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `POST /api/v4/plot/preview` | `backend/app/api/routes/narrative_v4.py` | 生成 V4 plot preview | body: `dict[str, object]` | V4 bridge payload | `context.id` 可推导 | 异常记录 runtime metric 后抛出 | `build_v4_bridge_payload_with_memory`、V4 memory store |
| `POST /api/v4/workbench/preview` | 同上 | 生成 V4 Workbench 预览 | body: `dict[str, object]` | `NarrativeV4WorkbenchPreviewPayload` 形态 | `context.state` 存在更稳妥 | 异常记录 runtime metric 后抛出 | `build_v4_workbench_preview`、V4 memory store |
| `GET /api/v4/observability/snapshot` | 同上 | 聚合 V4 观测快照 | Query: `limit=600`、`include_alert_routing=true` | snapshot + 可选 `alertRouting` | 本地 memory/runtime 文件可读 | 无数据时仍返回 snapshot，只是指标较弱 | `build_v4_observability_snapshot`、`route_v4_observability_alerts` |
| `POST /api/v4/observability/alerts/route` | 同上 | 对当前 snapshot 执行告警路由 | Query: `limit=600` | `{routing,snapshot}` | 通常要求 snapshot 中存在 critical alert 才会真实外发 | 冷却、未配置远端、远端失败时降级为本地留痕 | `alert_channel.py`、远端 webhook |

### V4 出站依赖

- `backend/app/services/narrative_v4/alert_channel.py`
- 出站地址来自配置：
  - `v4_alert_im_webhook_url`
  - `v4_alert_webhook_url`
  - `v4_alert_remote_enabled`

## 5. V6：模拟、事件注入、GraphRAG

| 接口 | 文件 | 功能 | 输入 | 输出 | 前置条件 | 错误分支 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `POST /api/narrative/v6/seed/extract` | `backend/app/api/routes/narrative_v6.py` | 抽取 narrative seed | `NarrativeSeedExtractionRequest` | `NarrativeSeedExtractionResponse` | `v6_enabled=true` | 关闭时 `503 v6_disabled` | seed extractor、runtime metrics |
| `POST /api/narrative/v6/characters/parameterize` | 同上 | 角色画像参数化 | `CharacterParameterizeRequest` | `CharacterParameterizeResponse` | `v6_enabled=true` | 关闭时 `503` | parameterizer |
| `POST /api/narrative/v6/simulations/parallel` | 同上 | 运行并落盘并行模拟 | `ParallelSimulationRequest` | `ParallelPlotSimulationResult` | `v6_enabled=true` | 无 winner 时标记 fallback；异常时 500/503 | GraphRAG、simulation store、runtime metrics |
| `GET /api/narrative/v6/simulations/{simulation_id}` | 同上 | 读取既有模拟 | path `simulation_id` | `ParallelPlotSimulationResult` | 目标 simulation 已存在 | 不存在返回 `404 simulation not found` | simulation store |
| `POST /api/narrative/v6/simulations/{simulation_id}/inject-event` | 同上 | 对既有模拟注入事件 | path `simulation_id` + `EventInjectionRequest` | `EventInjectionResult` | simulation 已存在 | 不存在 404；重排后无 winner 则 fallback | event injection、simulation store |
| `POST /api/narrative/v6/conflicts/probe` | 同上 | 试探涌现冲突 | `EmergentConflictProbeRequest` | `EmergentConflictProbeResult` | `v6_enabled=true` | 异常直接失败 | conflict probe |
| `POST /api/narrative/v6/characters/{character_id}/interview` | 同上 | 角色访谈 | path `character_id` + `CharacterInterviewRequest` | `CharacterInterviewResponse` | `v6_enabled=true` | 异常直接失败 | interview service、可选 GraphRAG |
| `POST /api/narrative/v6/group-memory/apply` | 同上 | 应用群体记忆图 | `GroupMemoryApplyRequest` | `GroupMemoryGraph` | `v6_enabled=true` | 异常直接失败 | group memory service |
| `POST /api/narrative/v6/graph/retrieve` | 同上 | 图记忆检索 | `GraphRAGRetrieveRequest` | `GraphRAGRetrieveResponse` | `v6_enabled=true` | fallback 时保留 200，但状态记录为 fallback | GraphRAG + history stitching |
| `POST /api/narrative/v6/graph/memory/compact` | 同上 | 压缩图记忆存储 | 无 body | `dict[str,int]` | `v6_enabled=true` | 异常直接失败 | graph memory store |
| `GET /api/narrative/v6/graph/memory/audit` | 同上 | 图记忆审计快照 | Query: `limit` | `dict[str,object]` | `v6_enabled=true` | 异常直接失败 | graph memory store |
| `POST /api/narrative/v6/graph/memory/audit/snapshot` | 同上 | 落盘审计快照 | Query: `limit` | `dict[str,object]` | `v6_enabled=true` | 异常直接失败 | graph memory store |
| `GET /api/narrative/v6/graph/memory/audit/history` | 同上 | 查询审计历史 | Query: `limit` | `list[dict]` | `v6_enabled=true` | 异常直接失败 | graph memory store |
| `GET /api/narrative/v6/graph/memory/audit/alerts` | 同上 | 图记忆趋势告警 | Query: `limit` | `dict[str,object]` | `v6_enabled=true` | 异常直接失败 | graph memory store |
| `GET /api/narrative/v6/observability` | 同上 | V6 runtime 快照 | Query: `limit=500` | `dict[str,object]` | `v6_enabled=true` | 关闭时 503 | runtime metrics store |

### V6 关键流程

1. Simulation 路由会先做 GraphRAG 检索与 history stitching。
2. 检索命中会写入 graph memory history。
3. 并行模拟结果写入 simulation store。
4. 事件注入会在已有 simulation 上重排路径并覆盖保存。

## 6. V7：决策、benchmark、治理主链

### 6.1 重点解释接口

| 接口 | 文件 | 功能 | 输入 | 输出 | 前置条件 | 错误分支 | 依赖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `POST /api/narrative/v7/sample` | `backend/app/api/routes/narrative_v7.py` | 从文本采样 NQM 指标 | `NQMSampleRequest` | `NQMSampleResponse` | `v7_enabled=true` | 关闭时 `503 v7_disabled` | sampler |
| `POST /api/narrative/v7/market-state/adapt` | 同上 | 统一 story state 到 market state | `StoryStateMarketAdaptRequest` | `StoryStateMarketAdaptResponse` | `v7_enabled=true` | 关闭时 503 | market state adapter |
| `POST /api/narrative/v7/decision/preview` | 同上 | 一次性完成 adapt + sample + decide | `UnifiedDecisionPreviewRequest` | `UnifiedDecisionPreviewResponse` | `v7_enabled=true` | 关闭时 503；内部异常 500 | adapter、sampler、decision controller |
| `POST /api/narrative/v7/decision` | 同上 | 只执行决策 | `DecisionRequest` | `DecisionResponse` | `market_state/vector/ohlcv` 完整 | 关闭时 503 | decision controller |
| `GET /api/narrative/v7/decision/rules` | 同上 | 输出规则说明 | 无 | `dict` | `v7_enabled=true` | 关闭时 503 | decision controller |
| `POST /api/narrative/v7/opening-gate` | 同上 | 首章开门审查 | `OpeningGateRequest` | `OpeningGateResponse` | `v7_opening_gate_enabled=true` | 关闭时 `503 opening_gate_disabled` | opening gate |
| `POST /api/narrative/v7/hook-guard` | 同上 | 钩子密度审查 | `HookGuardRequest` | `HookGuardResponse` | `v7_enabled=true` | 异常直接失败 | expectation manager |
| `POST /api/narrative/v7/deadlock/check` | 同上 | 僵局检查 | `DeadlockCheckRequest` | `DeadlockCheckResponse` | `v7_deadlock_router_enabled=true` | 关闭时 `503 deadlock_router_disabled` | deadlock router |
| `POST /api/narrative/v7/antipattern/check` | 同上 | 反模式检查 | `AntiPatternCheckRequest` | `AntiPatternCheckResponse` | `v7_antipattern_guard_enabled=true` | 关闭时 `503 antipattern_guard_disabled` | antipattern registry |
| `POST /api/narrative/v7/benchmark/ingest` | 同上 | benchmark 样本入库 | `BenchmarkIngestRequest` | `BenchmarkIngestResponse` | `sample_payload` 非空 | 空 payload 返回 422；冲突返回 409 | benchmark library/store |
| `POST /api/narrative/v7/benchmark/query` | 同上 | 查询 benchmark corridor | `BenchmarkQueryRequest` | `BenchmarkQueryResponse` | `v7_enabled=true` | 异常直接失败 | benchmark library |
| `GET /api/narrative/v7/benchmark/versions` | 同上 | 查询版本列表 | Query: `limit=20` | `BenchmarkVersionListResponse` | `v7_enabled=true` | 异常直接失败 | benchmark library |
| `POST /api/narrative/v7/benchmark/restore/{version}` | 同上 | 恢复指定版本 | path `version` | `BenchmarkRestoreResponse` | version 存在 | 不存在返回 404 | benchmark library |
| `GET /api/narrative/v7/benchmark/maintenance/alert` | 同上 | 当前维护告警态 | Query: `limit` | `BenchmarkMaintenanceAlertResponse` | `v7_enabled=true` | 异常直接失败 | SLA policy + report |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run` | 同上 | 执行治理 run | Query: `dry_run/alert_limit/archive_limit/idempotency_key/retry_run_id` | `BenchmarkMaintenanceAlertGovernanceRunResponse` | `v7_enabled=true` | 幂等冲突、重试对象异常、运行失败 | benchmark store + archive + governance log |
| `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest` | 同上 | 读取治理 digest | Query: `limit` | `BenchmarkMaintenanceAlertGovernanceRunDigestResponse` | `v7_enabled=true` | 异常直接失败 | governance runs log |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit` | 同上 | 触发升级事件 | Query: `limit/ignore_cooldown` | `BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse` | 通常需要 digest 推荐升级 | 冷却或无需升级时返回 suppress/no-op 语义 | escalation log |
| `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate` | 同上 | 治理主链自动补救 | Query: `dry_run/limit/alert_limit/archive_limit` | `BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse` | digest 有推荐动作 | `escalation_required`、`no_action`、dry-run | governance run + auto prune + escalation |
| `GET /api/narrative/v7/observability` | 同上 | V7 runtime 指标快照 | Query: `limit=500` | `dict` | `v7_enabled=true` | 关闭时 503 | runtime metrics store |

### 6.2 V7 次级接口

以下接口存在，但不建议在第一版 DeepWiki 文档中平铺：

- `thresholds/preview`
- `emotion/score`
- `loop/analyze`
- `pacing/evaluate`
- `benchmark/versions/diff`
- `benchmark/audit/export`
- `benchmark/versions/repair`
- `benchmark/versions/auto-remediate`
- `benchmark/maintenance/alerts/*` 的 list/summary/export/prune/archive 家族
- `benchmark/maintenance/alerts/governance/runs/escalations/*`
- 更长链的 `auto-remediations/.../auto-remediate/runs/...`

建议单独写“治理对象与状态流转”文档说明，而不是在总接口页平铺 50+ 路由。

## 7. 回调、Webhook、定时任务边界

### 7.1 入站回调 / Webhook

- 当前未发现入站 callback 或 webhook route。

### 7.2 出站 Webhook

- V4 仅存在出站告警投递：
  - 文件：`backend/app/services/narrative_v4/alert_channel.py`
  - 触发条件：observability snapshot 中出现 critical alert，且配置允许远端投递。

### 7.3 定时任务入口

- 当前未发现仓库内建 scheduler、cron worker、Celery、RQ、APScheduler。
- `[推断]` 下列接口更像供外部调度器调用的 maintenance endpoints：
  - `/api/narrative/v7/benchmark/maintenance/alerts/auto-archive`
  - `/api/narrative/v7/benchmark/maintenance/alerts/governance/run`
  - `/api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
  - `/api/narrative/v7/benchmark/versions/auto-remediate`

## 8. 在线 / 离线分界

### 在线主链

- `GET /api/dashboard`
- `POST /api/recommendation/preview`
- `POST /api/v2/recommendation/preview`
- `GET/POST /api/v2/workbench/contexts*`
- `POST /api/v4/workbench/preview`
- `POST /api/narrative/v6/simulations/parallel`
- `POST /api/narrative/v7/decision/preview`

### 离线或维护链

- `POST /api/training`
- `POST /api/history/export`
- `POST /api/narrative/v7/benchmark/ingest`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
- `POST /api/narrative/v7/benchmark/versions/auto-remediate`

## 9. 待确认

- `POST /api/recommendation/preview` 的 `recommendations` 请求字段当前是否应该参与计算，需确认。
- `POST /api/v4/plot/preview` 与 `POST /api/v4/workbench/preview` 目前以 `dict[str, object]` 接收上下文，建议后续补正式 request schema。
- V7 长链治理接口中，哪些属于长期稳定 API、哪些属于中间实验接口，需团队确认。
