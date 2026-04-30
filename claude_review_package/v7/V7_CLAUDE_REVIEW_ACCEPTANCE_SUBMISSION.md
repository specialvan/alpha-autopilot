# V7 Claude 评审验收提交清单（第三十二轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十二轮生产化增强进行验收（治理升级事件日志生命周期治理：prune）。

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

## 3. 第三十二轮能力增强

1. 新增治理升级事件日志生命周期治理能力：`prune_maintenance_alert_governance_escalations`。
2. 新增治理升级事件清理 API：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/prune`。
3. 支持 `dry_run/apply` 双路径，便于先验收再执行。
4. 支持 `keep_last` 保留最近 N 条升级事件。
5. 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`84 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. `escalations/prune` 的 `dry_run/apply` 语义是否清晰且可复现。
2. `total_events_before/kept_count/candidate_count/pruned_count` 口径是否一致。
3. 脏行处理是否满足治理要求（`malformed_candidate_count` 与 `malformed_dropped_count`）。
4. 执行 prune 后，`GET /escalations` 的可见事件窗口是否符合保留策略。
