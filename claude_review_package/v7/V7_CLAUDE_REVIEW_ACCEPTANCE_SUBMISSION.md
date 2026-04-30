# V7 Claude 评审验收提交清单（第三十七轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十七轮生产化增强进行验收（治理升级事件自愈运行历史审计）。

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

## 3. 第三十七轮能力增强

1. 新增治理升级事件自愈运行历史落盘能力（remediation runs）。
2. 新增自愈历史查询 API：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations`。
3. 历史记录输出动作与执行字段：`action/executed/emitted/pruned`。
4. 历史记录输出审计字段：`emitted_event_id/auto_prune_pruned_count/auto_prune_malformed_dropped_count`。
5. 支持 `limit/cursor` 分页消费并输出 `malformed_line_count`。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`96 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 自愈历史是否完整覆盖 dry-run 与 apply 两类执行轨迹。
2. 历史分页与排序口径是否稳定可复现。
3. 历史字段是否可回放关键执行结果（emit/prune）。
4. 历史计数与实时执行结果（auto-remediate response）是否一致。