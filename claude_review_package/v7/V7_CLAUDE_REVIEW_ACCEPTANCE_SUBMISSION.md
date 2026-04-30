# V7 Claude 评审验收提交清单（第二十五轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十五轮生产化增强进行验收（治理运行日志自动清理策略）

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

## 3. 第二十五轮能力增量

1. 新增治理运行日志自动清理能力：`auto_prune_maintenance_alert_governance_runs`。
2. 新增自动清理接口：
   `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`
3. 新增自动清理策略环境变量：
   `AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_TRIGGER_COUNT`
   `AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_KEEP_LAST`
4. 自动清理支持 `dry_run/apply` 双路径。
5. 自动清理响应输出 `should_prune + prune` 详细结果，便于值班联动。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`70 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 自动清理阈值触发行为是否准确（低于阈值不触发、高于阈值触发）。
2. `dry_run` 与 `apply` 语义是否一致且可解释。
3. `should_prune` 与 `prune` 明细输出是否满足运维消费。
4. 策略环境变量与 API 行为联动是否正确。
