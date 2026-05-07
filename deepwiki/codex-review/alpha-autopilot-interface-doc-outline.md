# alpha-autopilot 接口文档大纲建议

适用目标：

- 作为仓库根目录新增文档的大纲草案
- 作为后续 `docs/` 目录分拆文档的目录骨架
- 作为 DeepWiki 自动组织前的“人工定锚”

建议不要先写一份超长总文档，而是按下面顺序拆成 6 到 8 份：

## 0. 文档总则

建议新增：

- `docs/interfaces/README.md`
- `docs/interfaces/CONVENTIONS.md`

必须说明：

- Baseline / Increment / Experimental 的治理边界
- “代码事实优先于历史文档”的判定规则
- `[推断]` 与 `待确认` 的标记规范
- 字段说明模板
- 状态流转模板

## 1. 系统边界与分层

建议新增：

- `docs/interfaces/01-system-boundary-and-layering.md`

必须说明：

- `alpha_autopilot/` 是基础推荐核
- `alpha_autopilot_v2/v3/v4` 是增量算法层
- `backend/app/services/` 是服务编排层
- `backend/app/api/routes/` 是 HTTP 暴露层
- `ui-react/` 是消费层

这一篇只讲“谁依赖谁”，不要细讲字段。

## 2. 核心数据契约

建议新增：

- `docs/interfaces/02-core-data-contracts.md`

优先固定的对象：

1. `StoryState`
2. `CharacterState`
3. `NarrativeV2PreviewRequest`
4. `NarrativeV2WorkbenchContextPayload`
5. `ParallelSimulationRequest`
6. `EventInjectionRequest`
7. `UnifiedDecisionPreviewRequest`
8. `BenchmarkMaintenanceAlert*`
9. `BenchmarkMaintenanceAlertGovernance*`
10. `NarrativeV8` control/transition 相关对象

每个对象统一写：

- 所在文件
- 字段表
- 枚举值
- 必填项
- 默认值
- 兼容性说明
- 是否由 UI 直接依赖

## 3. HTTP API 合同

建议新增：

- `docs/interfaces/10-http-api-contract.md`

按接口簇拆，而不是按文件名拆：

### 3.1 基础推荐与训练

- `GET /api/dashboard`
- `POST /api/recommendation/preview`
- `POST /api/training`
- `POST /api/feedback`
- `GET /api/history`
- `POST /api/history/export`

### 3.2 V2 Workbench

- `POST /api/v2/recommendation/preview`
- `GET /api/v2/workbench/contexts`
- `POST /api/v2/workbench/contexts/refresh`

### 3.3 V4 Preview 与 Observability

- `POST /api/v4/plot/preview`
- `POST /api/v4/workbench/preview`
- `GET /api/v4/observability/snapshot`
- `POST /api/v4/observability/alerts/route`

### 3.4 V6 模拟与 GraphRAG

- `POST /api/narrative/v6/seed/extract`
- `POST /api/narrative/v6/characters/parameterize`
- `POST /api/narrative/v6/simulations/parallel`
- `GET /api/narrative/v6/simulations/{id}`
- `POST /api/narrative/v6/simulations/{id}/inject-event`
- `POST /api/narrative/v6/characters/{id}/interview`
- `POST /api/narrative/v6/group-memory/apply`
- `POST /api/narrative/v6/graph/retrieve`
- `POST /api/narrative/v6/graph/memory/compact`
- `GET /api/narrative/v6/graph/memory/audit`
- `POST /api/narrative/v6/graph/memory/audit/snapshot`
- `GET /api/narrative/v6/graph/memory/audit/history`
- `GET /api/narrative/v6/graph/memory/audit/alerts`
- `GET /api/narrative/v6/observability`

### 3.5 V7 决策与治理

第一版只写最关键子集：

- `POST /api/narrative/v7/sample`
- `POST /api/narrative/v7/market-state/adapt`
- `POST /api/narrative/v7/decision/preview`
- `POST /api/narrative/v7/decision`
- `GET /api/narrative/v7/decision/rules`
- `POST /api/narrative/v7/opening-gate`
- `POST /api/narrative/v7/hook-guard`
- `POST /api/narrative/v7/deadlock/check`
- `POST /api/narrative/v7/antipattern/check`
- `POST /api/narrative/v7/benchmark/ingest`
- `POST /api/narrative/v7/benchmark/query`
- `GET /api/narrative/v7/benchmark/versions`
- `POST /api/narrative/v7/benchmark/restore/{version}`
- `GET /api/narrative/v7/benchmark/maintenance/alert`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
- `GET /api/narrative/v7/observability`

第二版再补那些长链 `auto-remediations/.../auto-remediate/runs/...` 路径。

每个接口统一使用同一模板：

- 名称
- 方法与路径
- 所在文件
- 功能说明
- 请求体 / Query / Path 参数
- 响应体
- 成功分支
- 失败分支
- 回退逻辑
- 依赖配置
- 写入产物

## 4. 工作台上下文与推荐流程

建议新增：

- `docs/interfaces/20-workbench-and-recommendation-flows.md`

必须讲清楚：

### 4.1 V2 Workbench 上下文源优先级

1. 在线 PlotPilot API
2. 本地 raw report
3. 导入 fixture
4. live fallback

### 4.2 V2 Preview 主流程

- state build
- rule evaluate
- search
- evaluation
- validation
- ledger append

### 4.3 V4/V8 Preview 嵌入位置

- 为什么 `GET /api/v2/workbench/contexts` 的单个 context 会附带 `v4_preview` 与 `v8_preview`

这一篇应明确在线流程与离线流程边界。

## 5. 事件、告警、复盘对象

建议新增：

- `docs/interfaces/30-alerts-events-and-postmortem-objects.md`

必须优先固定：

- `TrainingLogEntry`
- `MatrixSnapshot`
- `GraphMemoryRecord`
- `BenchmarkMaintenanceAlertEvent`
- `BenchmarkMaintenanceAlertGovernanceRunRecord`
- `BenchmarkMaintenanceAlertGovernanceEscalationEvent`
- `BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord`
- V4 alert sink row

必须说明：

- 它们写到哪个文件
- 为什么算“事件”而不是普通日志
- 用于哪个复盘页面或治理动作
- 哪些对象会被后续 digest / summary / export 聚合

## 6. 状态机与任务流转

建议新增：

- `docs/interfaces/40-state-machines-and-task-lifecycles.md`

必须讲清楚的状态：

### 6.1 V2 规则状态

- `legal`
- `blocked`
- `prerequisite_missing`

### 6.2 V6 simulation path 状态

- `ok`
- `failed`

### 6.3 V7 治理状态

- governance run: `succeeded / failed`
- maintenance alert level: `ok / warn / critical`
- version integrity: `verified / unverified / failed`
- digest recommended_action 的常见动作

### 6.4 V8 control surface state

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

每个状态机都要写：

- 入口条件
- 迁移条件
- 输出对象
- 异常兜底

## 7. 外部服务、配置项、运行依赖

建议新增：

- `docs/interfaces/50-external-dependencies-and-config.md`

必须说明：

### 7.1 外部 HTTP

- PlotPilot report API
- V4 remote webhook

### 7.2 本地存储

- SQLite
- JSON
- JSONL
- archive 目录

### 7.3 环境变量

按域拆：

- 通用 API / app 信息
- V2 online report
- V4 alert / compression / guard
- V6 simulation store / graph memory / observability
- V7 decision rules / governance / archive / stale thresholds

### 7.4 未发现项

- 无入站 webhook
- 无消息队列
- 无内建 scheduler

## 8. 测试与验收映射

建议新增：

- `docs/interfaces/60-tests-and-contract-verification.md`

必须说明：

- 每个关键契约由哪些测试覆盖
- 哪些测试是 acceptance-level
- 哪些文档可以直接引用测试名作为“行为证据”

优先列：

- `test_narrative_v2_*`
- `test_narrative_v6_*`
- `test_narrative_v7_*`
- `test_narrative_v8_*`
- `test_run_v4_production_cycle.py`
- `test_run_v6_acceptance_review.py`
- `test_run_v7_acceptance_review.py`
- `test_run_v8_acceptance_review.py`

## 推荐落地顺序

1. `01-system-boundary-and-layering.md`
2. `02-core-data-contracts.md`
3. `10-http-api-contract.md`
4. `20-workbench-and-recommendation-flows.md`
5. `30-alerts-events-and-postmortem-objects.md`
6. `40-state-machines-and-task-lifecycles.md`
7. `50-external-dependencies-and-config.md`
8. `60-tests-and-contract-verification.md`

## 写作提醒

- 先固定接口契约，再解释实现细节。
- 先写主链，再写实验层。
- 不要把 V7 的长链 auto-remediate 路径一次性铺满首页文档，先给总图，再分章节展开。
- 任何不确定结论都要显式标记 `[推断]` 或 `待确认`。
