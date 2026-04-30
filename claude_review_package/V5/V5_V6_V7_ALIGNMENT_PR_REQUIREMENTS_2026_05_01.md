# V5 同步对齐 V6/V7 适配 PR 需求文档（Codex 评审版）

## 1. 文档定位

- 日期：2026-05-01
- 目标：基于当前仓库真实代码与测试现状，梳理 V5 对齐 V6/V7 的可合入能力、关键差距与串行实施任务。
- 执行策略：单任务推进、单任务验收、未通过不切换下一任务。
- 评审对象：Codex / Claude（工程验收口径一致）。

输入依据：

- `claude_review_package/V5/v5-pr.md`
- `claude_review_package/V6/V6_IMPLEMENTATION_TASK_BOARD.md`
- `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`
- `backend/app/api/routes/narrative_v6.py`
- `backend/app/api/routes/narrative_v7.py`
- `backend/app/services/narrative_v6/`
- `backend/app/services/narrative_v7/`
- `tests/test_narrative_v6_api.py`
- `tests/test_narrative_v6_observability.py`
- `tests/test_narrative_v7_api.py`
- `tests/test_narrative_v7_modules.py`

## 2. 当前能力对齐结论

### 2.1 V5（PR-AA-01~08）

- 状态：已落地（以 `claude_review_package/V5/v5-pr.md` 为准）。
- 覆盖：留存向量、六步脚手架、情绪滑块、人设功能位、关系图输入、宏观结构、提示词压缩。

### 2.2 V6（PR-AA-09~15）

- 状态：已落地并在任务板标记 `ACCEPTED`。
- 覆盖：seed 提取、人设参数化、并行推演、冲突探针、事件注入、角色访谈、群体记忆。
- 代码锚点：`backend/app/services/narrative_v6/*` + `/api/narrative/v6/*` 路由。

### 2.3 V7（PR-AA-26~39）

- 状态：主体能力已落地（采样、阈值、决策、门禁、风控、benchmark 生命周期治理均存在）。
- 风险：当前回归存在 1 个失败用例，影响治理链稳定性基线。失败用例为 `tests/test_narrative_v7_modules.py::test_benchmark_store_governance_retry_limit_escalates`。

## 3. 可合入功能需求（对齐当前工程）

可直接合入（代码已具备，主要补编排和入口）：

1. V6 动态叙事推演全链能力（seed -> 参数化 -> 并行推演 -> 注入重算）。
2. V6 图检索与跨会话记忆拼接（GraphRAG + history stitching）。
3. V7 决断反馈控制能力（sample/threshold/decision/opening/deadlock/antipattern/pacing）。
4. V7 benchmark 资产治理能力（版本、修复、审计、自动治理、告警日志）。

需要适配后合入（当前缺编排或契约桥接）：

1. V5 `retention_desire` 与 V6 `retention_desire_vector` 评分权重的统一映射。
2. V5 六步脚手架到 V6 推演输入/输出的一致传递。
3. V2 `StoryState` 到 V7 `NarrativeMarketState` 的统一适配层。
4. Workbench 的 V5/V6/V7 一体化决策入口（当前仅 V2+V4 主路径，V6 仅访谈面板）。
5. V4/V6/V7 观测字段统一口径（目前各版本可观测快照格式差异大）。

## 4. 关键差距清单（适配项）

| Gap ID | 差距描述 | 当前证据 | 适配要求 | 优先级 |
| --- | --- | --- | --- | --- |
| GAP-01 | V5 留存向量语义未统一到 V6 评分权重 | `backend/app/services/narrative_v6/scoring.py` 使用 `hook_strength/suspense/...`；V5 用 `primal_desire/...` | 新增兼容映射层，保持旧参数兼容 | P0 |
| GAP-02 | 六步脚手架未形成 V5->V6 的单一契约 | V2 preview 支持 `plot_unit_scaffold`，V6 仅在路径结果里输出 `six_step_scaffold_mapping` | 建立统一输入字段并贯通推演 | P0 |
| GAP-03 | 缺少 StoryState -> NarrativeMarketState 适配器 | V7 `DecisionRequest` 需完整 `market_state`，V2/V6 不直接产出 | 增加桥接服务与默认参数策略 | P0 |
| GAP-04 | 缺少“一键链路”入口将 V5/V6 结果送入 V7 决断 | 路由层分散于 `/api/v2`、`/api/narrative/v6`、`/api/narrative/v7` | 增加 orchestration endpoint（预览级） | P0 |
| GAP-05 | 观测口径不一致，难以生产验收 | V4/V6/V7 observability 各自 schema 不同 | 增加统一 envelope 和关键指标字典 | P1 |
| GAP-06 | 前端缺少 V6/V7 主流程可视化入口 | `ui-react` 当前仅 V6 Character Interview 入口 | 增加最小可用编排面板与错误态处理 | P1 |
| GAP-07 | V7 治理 digest 重试次数统计有回归 | 现网回归：`latest_failed_attempt` 断言失败（期望 3，实际 2） | 先修复并锁定回归用例 | P0 |

## 5. 串行执行任务板（V5 对齐 V6/V7）

执行规则：

1. 同一时间只允许一个 `ACTIVE` 任务。
2. 当前任务未 `ACCEPTED` 不进入下个任务。
3. 每个任务必须有固定验收命令。
4. 任务完成必须回写状态文档与证据路径。

当前激活任务：

- active_task_id: `COMPLETE`
- active_task_name: `A08 completed - full-chain regression and runbook closeout`
- cycle_status: `ACCEPTED`
本轮已验收：

- `A01` 已完成并验收通过（2026-05-01）
- 验收命令：`pytest -q tests/test_narrative_v7_modules.py -k "governance_retry_limit_escalates or governance_failure_streak_escalates"`
- 回归命令：`pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py`
- 结果：`106 passed`（后端回归子集），`20 passed`（前端全量），`build success`
任务池：

| Task ID | 任务名称 | 范围 | 验收命令 | 状态 |
| --- | --- | --- | --- | --- |
| A01 | 修复 V7 治理 digest 重试次数统计回归 | `backend/app/services/narrative_v7/benchmark_store.py` + `tests/test_narrative_v7_modules.py` | `pytest -q tests/test_narrative_v7_modules.py -k "governance_retry_limit_escalates or governance_failure_streak_escalates"` | ACCEPTED (2026-05-01) |
| A02 | V5->V6 retention vector compatibility mapping | `backend/app/services/narrative_v6/scoring.py` + `parallel_simulation.py` + tests | `pytest -q tests/test_parallel_plot_simulation.py tests/test_narrative_v6_api.py` | ACCEPTED (2026-05-01) |
| A03 | 六步脚手架契约贯通 V5/V6 | `backend/app/services/narrative_v6/schemas.py` + `parallel_simulation.py` + API tests | `pytest -q tests/test_parallel_plot_simulation.py tests/test_narrative_v6_api.py` | ACCEPTED (2026-05-01) |
| A04 | StoryState->NarrativeMarketState 适配器 | `backend/app/services/narrative_v7/` 新增 adapter + route tests | `pytest -q tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` | ACCEPTED (2026-05-01) |
| A05 | 新增 V5/V6->V7 一体化决策预览路由 | `backend/app/api/routes/narrative_v7.py` + adapter/service | `pytest -q tests/test_narrative_v7_api.py` | ACCEPTED (2026-05-01) |
| A06 | 统一 V4/V6/V7 observability envelope | `backend/app/services/narrative_v4|v6|v7/observability*.py` | `pytest -q tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py` | ACCEPTED (2026-05-01) |
| A07 | Workbench 增加 V6/V7 编排可视化入口 | `ui-react/src/api.ts` + `ui-react/src/features/v2Workbench/*` | `npm --prefix ui-react run test -- src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/characterInterviewPanel.test.tsx` | ACCEPTED (2026-05-01) |
| A08 | 全链回归与运行手册更新 | `scripts/` + `PROJECT_STATUS.md` + review package docs | `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py && npm --prefix ui-react run test && npm --prefix ui-react run build` | ACCEPTED (2026-05-01) |
## 6. 验收口径（全任务通用）

每个任务都必须满足：

1. 不破坏 `v1/v2` 基线路径。
2. 不绕开 `v3` 留存目标函数主逻辑。
3. feature flag 可关闭并可回退。
4. deterministic/mock 路径可运行。
5. 文档、代码、测试三者同批同步。

## 7. 本轮结论

- V5、V6、V7 功能主体已具备“可对齐”条件。
- 当前不是“从零开发”，而是“契约桥接 + 编排收口 + 观测统一 + 回归修复”。
- 建议立即按任务板从 `A01` 开始，逐项验收后再推进下一个任务。

## 8. A02 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_parallel_plot_simulation.py tests/test_narrative_v6_api.py` -> `15 passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `95 passed`
- Scope delivered: V5 desire-key compatibility mapping for V6 retention scoring (including dominant key support in request schema).


## 9. A03 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_parallel_plot_simulation.py tests/test_narrative_v6_api.py` -> `18 passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `96 passed`
- Scope delivered: V5/V2 `plot_unit_scaffold` contract accepted by V6 parallel simulation and propagated into `six_step_scaffold_mapping` with `action_climax_turn_type`.

## 10. A04 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `86 passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `100 passed`
- Scope delivered: added StoryState->NarrativeMarketState adapter service and `/api/narrative/v7/market-state/adapt` route with default strategy and override support.

## 11. A05 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_narrative_v7_api.py` -> `45 passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `102 passed`
- Scope delivered: added unified `/api/narrative/v7/decision/preview` route (adapter -> sampler -> decision) for one-request V5/V6->V7 decision preview.

## 12. A06 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py` -> `48 passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `104 passed`
- Scope delivered: introduced shared `unifiedEnvelope` (`obs-envelope.v1`) across V4/V6/V7 observability snapshots with consistent keyMetrics and thresholds projection.

## 13. A07 Acceptance Evidence (2026-05-01)

- Target verification: `npm --prefix ui-react run test -- src/pages/V2WorkbenchPage.test.tsx src/features/v2Workbench/characterInterviewPanel.test.tsx` -> `2 files passed, 11 tests passed`
- Regression verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `106 passed`
- Scope delivered: added Workbench V6/V7 orchestration entry with `/api/narrative/v7/decision/preview` integration and surfaced decision route/risk/composite outputs.

## 14. A08 Acceptance Evidence (2026-05-01)

- Target verification: `pytest -q tests/test_narrative_v6_api.py tests/test_narrative_v6_observability.py tests/test_narrative_v7_api.py tests/test_narrative_v7_modules.py` -> `106 passed`
- Frontend full test: `npm --prefix ui-react run test` -> `7 files passed, 20 tests passed`
- Frontend build: `npm --prefix ui-react run build` -> `build success`
- Scope delivered: full V5->V6/V7 task chain (A01-A08) accepted with backend/frontend regression and documentation closeout updates.
