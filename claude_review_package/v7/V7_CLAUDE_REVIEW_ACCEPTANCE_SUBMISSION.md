# V7 Claude 评审验收提交清单（第二十二轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十二轮生产化增强进行验收（治理运行日志生命周期治理）

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

## 3. 第二十二轮能力增量

1. 新增治理运行日志清理能力：`prune_maintenance_alert_governance_runs`。
2. 新增治理运行日志清理接口：
   `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune`
3. 支持 `dry_run/apply` 双路径，便于先预演后执行。
4. 支持 `keep_last` 保留最近 N 条治理运行记录。
5. 支持治理运行日志脏行统计与清理（`malformed_candidate_count/malformed_dropped_count`）。
6. 历史排序稳定性增强：按 `generated_at/completed_at/run_id` 多键排序，避免极短间隔失败+重试顺序抖动。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`64 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 运行日志清理契约是否完整（统计、候选、保留、删除结果）。
2. `dry_run` 预演与 `apply` 执行语义是否严格一致。
3. 脏行存在时，是否只在 apply 时进行实际剔除并正确计数。
4. 清理后历史查询接口是否返回预期保留窗口。
5. 排序稳定性修正是否覆盖高频失败+重试场景。
