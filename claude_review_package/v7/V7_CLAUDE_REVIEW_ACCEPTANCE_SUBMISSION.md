# V7 Claude 评审验收提交清单（第二十四轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十四轮生产化增强进行验收（治理运行导出能力）

## 1. 需求与计划文档

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 代码提交范围

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `backend/app/services/narrative_v7/benchmark_library.py`
4. `backend/app/api/routes/narrative_v7.py`
5. `tests/test_narrative_v7_modules.py`
6. `tests/test_narrative_v7_api.py`

## 3. 第二十四轮能力增量

1. 新增治理运行导出能力：`export_maintenance_alert_governance_runs`。
2. 新增治理运行导出接口：
   `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/export`
3. 导出结构统一为：`summary + paged records`，便于评审脚本与运维看板一次消费。
4. 导出接口支持 `limit/cursor` 分页，适配长窗口治理运行日志。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`68 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 导出接口分页行为（`limit/cursor/next_cursor/has_more`）是否稳定。
2. `summary` 与 `records` 组合是否满足审计/值班消费场景。
3. 导出结果中的统计字段与历史列表/摘要接口是否一致。
4. API 契约、异常路径与测试证据是否一致。
