# Workbench 与推荐链路

更新时间：2026-05-08

## 说明

本页聚焦“从触发到完成”的关键主链，不展开所有实现细节。目标是帮助 DeepWiki 和团队先理解：

- 推荐链路
- 任务调度入口
- 策略选择
- 执行反馈
- 在线 / 离线分界
- 异常兜底

## 1. Baseline 推荐预览

### 触发入口

- `POST /api/recommendation/preview`
- 实现：`backend/app/api/routes/recommendation.py`

### 流程

1. `build_preview(payload)` 构造基础 `state`。
2. 将 `tuningWeights` 转成内部调权列表。
3. 调用 `preview_recommendations(state, tuning, FeatureMatrix())`。
4. 返回 `{recommendations:[...]}`。

### 成功输出

- 推荐列表
- 每条推荐包含动作、分数、说明、风险、前置条件、下一步

### 失败分支

- 当前无显式兜底包装，异常直接由 FastAPI 返回错误。

### 说明

- `[推断]` 当前请求体中的 `recommendations` 字段未参与计算，更像前端保留输入。

## 2. 训练 / 反馈 / 历史闭环

### 2.1 训练链

#### 触发入口

- `POST /api/training`

#### 流程

1. `NarrativeTrainingService.train()` 加载内置样本。
2. 尝试从 V3 projection 文件补充训练样本。
3. `Trainer.fit(samples)` 训练特征矩阵。
4. `VersionManager.create_version()` 生成版本快照。
5. 遍历训练历史，写入 training log。
6. 遍历 value metrics，写入 metrics。
7. 返回 `TrainingResult`。

#### 成功输出

- `version`
- `sample_count`
- `weights`
- `summary`
- `history`
- `value_metrics`
- `top_actions`

#### 失败分支

- 训练或写盘异常直接上抛。
- projection 样本缺失不会阻断训练，只是退回基础样本集。

### 2.2 反馈链

#### 触发入口

- `POST /api/feedback`

#### 流程

1. 路由层根据 `accepted/score` 推导 `predicted`。
2. `NarrativeFeedbackService.record_feedback()` 组装 feedback payload。
3. 若 `abs(target - predicted) > 0.12` 或 `feedback < 0.8`，生成 feedback correction 版本快照。
4. 写 training log。
5. 写 value metric。
6. 聚合最新 summary 和 top actions。
7. 返回 `FeedbackResult`。

#### 失败分支

- 任一持久化失败则返回 `accepted=false` 与失败消息。

### 2.3 历史链

#### 触发入口

- `GET /api/history`
- `POST /api/history/export`

#### 流程

1. `HistoryService.get_history()` 读取 training logs。
2. 按 `stage/action/limit` 过滤。
3. 聚合 `valueSummary`、`topActions`、`versionTimeline`、`stageTimeline`。
4. `HistoryExportService.export_json()` 可将 training logs 与 value metrics 导出为 JSON。

## 3. V2 Workbench 上下文装载链

### 触发入口

- `GET /api/v2/workbench/contexts`
- `POST /api/v2/workbench/contexts/refresh`

### 源优先级

`NarrativeV2WorkbenchService.list_contexts()` 的优先级是固定的：

1. 在线 PlotPilot 报告 API
2. 本地 raw report + manifest 仲裁
3. 导入 fixture
4. live fallback

### 详细流程

1. 读取质量记录 `v3_records/*`，供 context enrichment 使用。
2. 调用 `probe_online_plotpilot_report_contexts()`：
   - 如果在线可用，转换为 `contexts[]`
   - 补 `source_diagnostics`
   - 对每个 context 追加 `v4_preview` 与 `v8_preview`
3. 若在线不可用且 `online_only=true`：
   - 直接返回空 `contexts`
   - `source=plotpilot_api`
   - `fallback_reason=online-report-unavailable`
4. 若允许回退：
   - 尝试 `load_latest_plotpilot_report_contexts()`
   - 不行再尝试 `load_imported_workbench_contexts()`
5. 如果仍然失败：
   - 构造 `live context`
   - 来源于 `base_state() + dashboard + history`
   - 仍会补 `v4_preview` 与 `v8_preview`

### 成功输出

- `contexts[]`
- `source`
- `context_contract`
- `fallback_reason`
- `run_id`
- `manifest_path`
- `preferred_model/resolved_model`
- `source_diagnostics`

### 失败 / 降级分支

- 在线 API 超时、5xx、429、网络错误：按重试策略退回本地或 fixture。
- V4 preview 构造异常：嵌入 `enabled=false` 的 fallback preview。
- V8 preview 构造异常：嵌入 `enabled=false` 的 fallback preview。

## 4. V2 推荐预览链

### 触发入口

- `POST /api/v2/recommendation/preview`

### 流程

1. `NarrativeV2StateBuilder.build()`
2. `NarrativeV2RuleService.evaluate()`
3. `NarrativeV2SearchService.search()`
4. `NarrativeV2EvaluationService.rank()`
5. `NarrativeV2ValidationService.record()`
6. best-effort `append_ledger()`
7. 返回 preview payload

### 成功输出

- `state`
- `rule_checks`
- `recommendations`
- `decision`
- `evaluation_summary`
- `validation`

### 失败 / 降级分支

- validation ledger 写失败不会中断主响应，只会留下 warning 语义。
- 其他异常由 FastAPI 直接返回。

### 策略选择含义

- V2 的核心是“规则过滤 + 搜索候选 + 评估排序”，不是黑箱生成。

## 5. V4 关系图预览与可观测性

### 触发入口

- `POST /api/v4/plot/preview`
- `POST /api/v4/workbench/preview`
- `GET /api/v4/observability/snapshot`
- `POST /api/v4/observability/alerts/route`

### 预览链

1. 合并关系历史与反馈历史。
2. 构造 relationship graph input。
3. 执行角色约束与 character validation。
4. 根据阈值决定是否做 prompt compression。
5. 组装候选、timeline、memory summary、genre calibration。
6. 记录 runtime metric。

### 观测与告警链

1. 聚合 runtime / feedback / relationship 指标。
2. 生成 observability snapshot。
3. 识别 critical alerts。
4. 判断 cooldown。
5. 若允许远端投递：
   - 组装告警 payload
   - 出站 POST 到 IM/Webhook
6. 无论是否成功远端送达，都写本地 sink row。

### 降级分支

- 无 critical alert：仅返回 `no-critical-alert`
- cooldown 生效：返回 `cooldown-active`
- 无远端配置：仅本地留痕
- 缺少 oncall 联系人：阻断远端投递
- 远端 HTTP 失败：状态降级为 `degraded-local-only`

## 6. V6 Simulation / GraphRAG / 事件注入

### 6.1 Simulation 主链

#### 触发入口

- `POST /api/narrative/v6/simulations/parallel`

#### 流程

1. `_ensure_enabled()` 检查 `v6_enabled`。
2. 基于请求构造默认 GraphRAG query：
   - 优先 `graph_rag_query`
   - 否则 `open_threads[0]`
   - 否则 `plot_events[0]`
   - 否则 `"main conflict direction"`
3. 调用 `_retrieve_graph_with_stitching()`：
   - 先做 deterministic GraphRAG
   - 再从 graph memory history 回拼
4. 将命中写入 graph memory store。
5. 调用 `parallel_simulation_service.run(...)` 生成 2 到 3 条路径。
6. 写入 simulation store。
7. 记录 runtime metric。

#### 成功输出

- `simulation_id`
- `paths`
- `winner_path_id`
- `decision_summary`
- `risk_flags`

#### 失败 / 降级分支

- 无 winner path：200 返回，但 runtime 状态记为 fallback。
- GraphRAG fallback：主链继续，只在结果与指标中标记 fallback。
- `v6_enabled=false`：返回 `503 v6_disabled`

### 6.2 事件注入链

#### 触发入口

- `POST /api/narrative/v6/simulations/{id}/inject-event`

#### 流程

1. 检查 simulation 是否存在。
2. 调用 `EventInjectionService.inject(simulation, payload)`。
3. 重排路径得分与 winner。
4. 覆盖保存 `updated_simulation`。
5. 返回注入结果与审计日志。

#### 失败 / 降级分支

- simulation 不存在：404
- 重排后无 winner：200 返回，但记为 fallback

## 7. V7 决策与治理主链

### 7.1 决策预览链

#### 触发入口

- `POST /api/narrative/v7/decision/preview`

#### 流程

1. `StoryStateMarketAdapter.adapt()` 把 story state 归一成 market state。
2. `NQMSampler.sample()` 计算 `vector + ohlcv`。
3. `DecisionFeedbackController.decide()` 产出 route-based decision。
4. `_execute_with_metrics()` 统一记录 runtime metric。

#### 成功输出

- `market_state`
- `vector`
- `ohlcv`
- `decision`
- `defaults_applied`

#### 失败分支

- `v7_enabled=false`：503
- 其他内部异常：500

### 7.2 Benchmark 入库链

#### 触发入口

- `POST /api/narrative/v7/benchmark/ingest`

#### 流程

1. 检查 `sample_payload` 非空。
2. 检查 `book_id` 是否重复。
3. 追加一条 benchmark row。
4. 写主 JSONL。
5. 同时生成版本快照。

#### 失败分支

- `empty_sample_payload` -> 422
- `duplicate_book_id` -> 409

### 7.3 治理 run 主链

#### 触发入口

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`

#### 流程

1. 读取治理 policy。
2. 根据 `idempotency_key` 判断是否重复请求。
3. 读取 active alerts summary。
4. 执行 auto archive。
5. 执行 archive cleanup。
6. 记录 governance run record。
7. 返回 run response。

#### 成功输出

- `run_id`
- `performed_steps`
- `auto_archive`
- `archive_cleanup`
- `active_summary_before/after`
- `archive_index_before/after`

#### 失败 / 升级分支

- 幂等冲突
- retry 对象不存在
- retry 对象状态不允许
- retry 次数超过上限
- digest 可能后续建议：
  - `retry_latest_failed_run`
  - `escalate_failed_run`
  - `auto_prune_runs`

### 7.4 自动补救链

#### 触发入口

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`

#### 流程

1. 读取 governance digest。
2. 判断推荐动作：
   - `observe`
   - `run_governance`
   - `prune_history`
   - `escalate`
3. 按推荐动作执行 governance run、auto prune 或 escalation emit。
4. 返回 `digest_before/digest_after`。

#### 说明

- `[推断]` 这一链路更像外部调度器驱动的维护入口，而不是在线实时主链。

## 8. V8 Workbench 嵌入预览

### 触发位置

- 不存在独立 FastAPI route。
- 当前通过 `GET/POST /api/v2/workbench/contexts*` 的单个 context 响应嵌入。

### 流程

1. `build_v8_workbench_preview()` 接收 context。
2. 若 `v8_workbench_enabled=false`，返回禁用态 preview。
3. 否则执行控制态选择、过渡与 follow-up scene 生成。
4. 将 `next_control_state`、`transition`、`future_hooks` 嵌入 context。

## 9. 在线 / 离线分界

### 在线主链

- Baseline preview
- V2 preview
- V2 Workbench contexts
- V4 workbench preview
- V6 simulation preview
- V7 decision preview

### 离线 / 维护链

- Training
- History export
- Benchmark ingest
- Governance run
- Auto archive / auto remediate / prune

## 10. 待确认

- V2 live fallback context 是否应长期保留为正式对外 contract，需确认。
- V8 preview 当前只作为嵌入输出，后续是否会升级为独立 route，需确认。
