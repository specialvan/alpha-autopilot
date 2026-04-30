# V7 Claude 评审验收提交清单（第三十一轮生产化）

- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十一轮生产化增强进行验收（治理升级事件摘要与导出）

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

## 3. 第三十一轮能力增量

1. 新增治理升级事件摘要能力：`summarize_maintenance_alert_governance_escalations`。
2. 新增治理升级事件导出能力：`export_maintenance_alert_governance_escalations`。
3. 新增摘要 API：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary`。
4. 新增导出 API：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/export`。
5. 升级事件新增 source/触发类型统计字段与稳定排序增强，便于值班看板消费。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`82 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 升级事件摘要统计是否准确（`manual_emit/auto_remediate/retry_exhausted/failure_streak_exhausted`）。
2. 升级事件导出结构是否满足单请求验收（`summary + paged events`）。
3. 摘要与导出的 `total_events/malformed_line_count` 口径是否一致。
4. 同秒多事件场景下排序与分页是否稳定可复现。
