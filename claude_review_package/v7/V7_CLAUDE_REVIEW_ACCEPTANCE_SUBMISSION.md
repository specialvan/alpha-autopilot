# V7 Claude 评审验收提交清单（第二十六轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十六轮生产化增强进行验收（治理运行健康 Digest）

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

## 3. 第二十六轮能力增量

1. 新增治理运行健康 Digest 能力：`build_maintenance_alert_governance_runs_digest`。
2. 新增治理运行 Digest 接口：
   `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
3. 新增新鲜度策略环境变量：
   `AA_V7_BENCH_GOVERNANCE_RUNS_STALE_SECONDS`
4. Digest 输出推荐动作：
   `retry_latest_failed_run / auto_prune_runs / execute_governance_run / observe`
5. Digest 输出运行新鲜度与窗口摘要，便于值班快速决策。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`72 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. Digest 推荐动作逻辑是否与失败优先处理原则一致。
2. 新鲜度阈值策略是否正确影响 `is_stale` 与推荐动作。
3. Digest 输出字段是否满足值班排障与调度联动需求。
4. API 契约、异常路径与测试证据是否一致。
