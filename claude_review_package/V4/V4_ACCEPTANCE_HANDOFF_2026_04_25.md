# V4 验收交接包（2026-04-25）

## 1. 本轮验收目标

为后续 Claude 验收评审准备可直接核验的证据，聚焦以下增量：

- `mapped_chapter` 上下文从聚合式 fallback 升级为真实章节 report 驱动 contract
- `v2` workbench contexts API 输出章节级 `compare_baseline`
- `/api/v2/workbench/contexts` 路由补齐显式 `response_model`（OpenAPI 可见）
- 前端 `V2 Workbench` 显示 baseline 对比信息

## 2. 功能落地范围

### 2.1 后端

- `NarrativeV2WorkbenchService` 新增 source 优先级：
  1. latest PlotPilot raw `report.json`
  2. imported `workbench_contexts.json`
  3. live history fallback
- 新增 `real_chapter_context_v1` 输出元信息：
  - `source`
  - `context_contract`
  - `report_path`
- 新增 `compare_baseline`：
  - `baseline_context_id`
  - `baseline_chapter_number`
  - `delta`（章节 state 数值字段差值）
- `/api/v2/workbench/contexts` 路由声明 `response_model=NarrativeV2WorkbenchContextsResponsePayload`

### 2.2 前端

- `compare_baseline` 全链路接入：
  - API 类型
  - backend context normalize
  - Context Rail 展示（Baseline chapter/context + top delta）
- V4 preview 展示与 compare baseline 并存，不破坏原有 workbench 行为

### 2.3 文档

- 新增 contract 文档：
  - `docs/api/v2-workbench-real-chapter-context-contract.md`
- README 增加 contract 入口链接

## 3. 关键文件（Claude 评审入口）

### 后端

- `backend/app/services/narrative_v2/imported_contexts.py`
- `backend/app/services/narrative_v2/workbench_service.py`
- `backend/app/services/narrative_v2/schemas.py`
- `backend/app/api/routes/workbench_v2.py`

### 前端

- `ui-react/src/api.ts`
- `ui-react/src/features/v2Workbench/types.ts`
- `ui-react/src/features/v2Workbench/backendContexts.ts`
- `ui-react/src/features/v2Workbench/components/ContextRail.tsx`

### 测试

- `tests/test_narrative_v2_imported_contexts.py`
- `tests/test_narrative_v2_workbench_context_api.py`
- `ui-react/src/features/v2Workbench/backendContexts.test.ts`
- `ui-react/src/pages/V2WorkbenchPage.test.tsx`

## 4. 验证证据（已执行）

1. `pytest tests/test_narrative_v2_imported_contexts.py -q`
- 结果：`7 passed`

2. `pytest tests/test_narrative_v2_workbench_context_api.py -q`
- 结果：`6 passed`

3. `pytest tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_quality_enrichment.py -q`
- 结果：`16 passed`

4. `python scripts/run_layered_tests.py api import frontend`
- 结果：通过（API 19 passed / import 11 passed / frontend 14 passed）

5. `python scripts/run_layered_tests.py api import v4 frontend`
- 结果：通过（API 19 passed / import 11 passed / v4 18 passed / frontend 14 passed）

6. `npm run build`（`ui-react`）
- 结果：成功

7. `python scripts/run_layered_tests.py`
- 结果：通过（core 7 passed / quality 11 passed / api 19 passed / frontend 14 passed / import 11 passed / v4 18 passed）

8. `python scripts/run_claude_acceptance_review.py`
- 结果：通过，生成验收报告
- 报告路径：`artifacts/acceptance/claude-acceptance-20260425T051048Z.md`

## 5. Claude 验收建议清单

- 校验 `/openapi.json` 中 `/api/v2/workbench/contexts` 的 200 响应为 `$ref` 模型
- 校验 `plotpilot_report` 场景返回：
  - `source=plotpilot_report`
  - `context_contract=real_chapter_context_v1`
  - `report_path` 非空且以 `report.json` 结尾
- 校验 `compare_baseline` 的 delta 字段是否覆盖约定数值字段
- 校验 imported fixture 与 live fallback 路径仍可用
- 校验前端 Context Rail 中 `Compare Baseline` 展示存在

## 6. 当前仍保留风险（供评审记录）

- 当前真实章节来源仍是本地 raw report 文件，不是线上章节服务 API
- latest report 选择策略基于文件 `mtime`，多源并发写入时仍需更强一致性规则
- `compare_baseline` 当前基于相邻章节比较，尚未支持跨窗口多 baseline 诊断

## 7. 一句话交接

本轮已把 `mapped_chapter` 从“聚合式临时上下文”推进到“可验证的真实章节 contract”，并补齐 API 显式模型、前端对比展示与分层验证证据，可直接进入 Claude 验收评审。
