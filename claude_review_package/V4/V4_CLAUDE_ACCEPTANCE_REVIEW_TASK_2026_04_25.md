# V4 Claude 验收评审任务单（2026-04-25）

## 1. 评审目标

请对当前 `alpha-autopilot` 分支进行验收评审，重点验证以下四项是否真实落地且未破坏主线：

1. `mapped_chapter` 上下文已优先从真实章节 report 构建（而非仅聚合 fallback）
2. `/api/v2/workbench/contexts` 已声明显式 `response_model`，OpenAPI 可见
3. 章节级 `compare_baseline` 已贯通后端 contract 与前端展示
4. 现有 V2/V3/V4 与前端分层门禁未被回归破坏

## 2. 输入文档（按顺序）

1. `claude_review_package/README_FOR_CODEX.md`
2. `claude_review_package/V4/V4_ACCEPTANCE_HANDOFF_2026_04_25.md`
3. `docs/api/v2-workbench-real-chapter-context-contract.md`
4. `PROJECT_STATUS.md`

## 3. 必跑验证命令

在仓库根目录执行并记录结果：

1. `python scripts/run_layered_tests.py`
2. `pytest tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_quality_enrichment.py -q`
3. `npm --prefix ui-react run build`

可选一键命令（会自动执行以上命令并产出 Markdown 报告）：

- `python scripts/run_claude_acceptance_review.py`

## 4. 必查代码入口

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

- `tests/test_narrative_v2_workbench_context_api.py`
- `tests/test_narrative_v2_imported_contexts.py`
- `ui-react/src/features/v2Workbench/backendContexts.test.ts`
- `ui-react/src/pages/V2WorkbenchPage.test.tsx`

## 5. 阻断判定标准

只有满足以下任一条件才判定阻断（P1）：

1. `/api/v2/workbench/contexts` 在 OpenAPI 中无显式 `$ref` 响应模型
2. report 场景返回缺少 `source/context_contract/report_path` 任一关键字段
3. `compare_baseline` 在 report 场景或前端展示链路中断裂
4. 分层门禁命令出现失败

以下情况不应作为阻断（仅记录为后续项）：

- 当前真实章节来源仍是本地 raw report 文件，尚未接线上章节服务 API
- latest report 选择策略使用 `mtime`，尚未做多源一致性治理
- baseline 对比当前为相邻章节，不含多窗口策略

## 6. 评审输出格式

请严格按以下结构输出：

1. **结论**：`通过` / `有条件通过` / `不通过`
2. **阻断项（P1）**：逐条给出证据（文件+行号或命令输出）
3. **非阻断风险（P2/P3）**：逐条给出影响与建议
4. **验证记录**：列出实际执行命令与结果摘要
5. **建议动作**：最多 3 条，按优先级排序

## 7. 一句话要求

请以“当前代码状态”为准裁决，不要复用已过时评审结论作为本轮阻断依据。
