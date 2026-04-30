# V7 Claude 评审验收提交清单（第三十四轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十四轮生产化增强进行验收（治理升级事件 Digest 能力）。

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

## 3. 第三十四轮能力增强

1. 新增治理升级事件 Digest 能力：`build_maintenance_alert_governance_escalations_digest`。
2. 新增 Digest API：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`。
3. 支持升级事件新鲜度阈值环境变量：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS`。
4. Digest 联动 runs-digest 推荐动作（`emit_escalation/auto_prune_escalations/observe`）。
5. 输出 `summary + run_digest` 聚合上下文，便于值班单请求验收。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`92 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. Digest 推荐动作口径是否与 runs-digest/事件摘要一致。
2. `escalation_needed -> observe -> malformed_detected` 动作迁移是否可复现。
3. `summary.latest_event` 新鲜度与阈值判断是否正确。
4. 自动清理建议触发条件（malformed/threshold）是否与 prune 策略对齐。