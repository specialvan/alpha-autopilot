# V7 Claude 评审验收提交清单（第二十八轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十八轮生产化增强进行验收（治理运行重试上限与升级联动）

## 1. 需求与计划文档

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 代码提交范围

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `backend/app/api/routes/narrative_v7.py`
4. `tests/test_narrative_v7_modules.py`
5. `tests/test_narrative_v7_api.py`

## 3. 第二十八轮能力增量

1. 新增治理运行重试上限策略：`AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS`。
2. 治理运行重试门禁：当 `retry_target.attempt >= max_retry_attempts` 时返回 `retry_attempt_limit_exceeded`。
3. 治理运行 Digest 新增升级动作：`escalate_failed_run`，并输出 `retry_max_attempts/latest_failed_attempt/retry_exhausted`。
4. auto-remediate 新增升级输出：`escalation_required/escalation_reason`，达到重试上限时不再执行重试。
5. API 路由新增错误码映射：重试超限返回 `422`。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`76 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 重试上限门禁是否严格生效（超限后拒绝重试且不污染运行日志）。
2. Digest 在失败超限场景下是否稳定给出 `escalate_failed_run`。
3. auto-remediate 在升级场景下是否输出清晰升级信号（`escalation_required/reason`）。
4. 新增 422 错误码语义是否与测试证据一致。
