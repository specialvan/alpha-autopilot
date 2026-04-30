# V7 Claude 评审验收提交清单（第二十九轮生产化）

- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十九轮生产化增强进行验收（治理运行连续失败熔断升级）

## 1. 需求与计划文档

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 代码提交范围

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `tests/test_narrative_v7_modules.py`
4. `tests/test_narrative_v7_api.py`

## 3. 第二十九轮能力增量

1. 新增治理运行连续失败升级阈值策略：`AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK`。
2. 治理运行摘要新增连续失败计数：`consecutive_failed_runs`。
3. 治理运行 Digest 新增失败熔断字段：`escalation_failure_streak_limit/failure_streak_exhausted`。
4. 当连续失败达到阈值时，Digest 推荐动作升级为 `escalate_failed_run`（message: `consecutive_failure_streak_exhausted`）。
5. auto-remediate 新增连续失败升级原因输出：`consecutive_failures_{n}_reached_limit_{limit}`。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`78 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 连续失败计数 `consecutive_failed_runs` 是否准确反映最新连续失败窗口。
2. Digest 在连续失败超阈值场景下是否稳定给出 `escalate_failed_run`。
3. 重试预算充足但连续失败超阈值时，是否正确触发熔断升级而非继续重试。
4. auto-remediate 在连续失败升级场景下的 `escalation_reason` 是否可用于值班处置。
