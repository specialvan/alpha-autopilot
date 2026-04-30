# V7 Claude 评审验收提交清单（第三十轮生产化）

- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十轮生产化增强进行验收（治理升级事件落盘与查询）

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

## 3. 第三十轮能力增量

1. 新增治理升级事件落盘能力：`emit_maintenance_alert_governance_escalation`。
2. 新增治理升级事件分页查询能力：`list_maintenance_alert_governance_escalations`。
3. 新增升级事件 API：
   - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit`
   - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
4. auto-remediate 升级路径新增自动事件发射（`source=auto_remediate`）。
5. 新增升级事件日志文件：`_maintenance_alert_governance_escalations.jsonl`。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`80 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 升级事件发射门禁是否准确（非升级动作时不误发，返回 `no_escalation_needed`）。
2. 升级事件字段是否满足值班追踪需求（`reason/source/latest_run/latest_failed_run`）。
3. auto-remediate 升级场景是否自动落盘并回填 `escalation_event`。
4. 升级事件分页查询（`cursor/next_cursor/has_more`）语义是否稳定。
