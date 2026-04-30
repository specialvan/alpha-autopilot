# V7 Claude 评审验收提交清单（第二十一轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十一轮生产化增强进行验收（治理执行幂等保护 + 失败重试记录）

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

## 3. 第二十一轮能力增量

1. 治理执行接口支持 `idempotency_key`，并引入请求指纹（request fingerprint）保护。
2. 相同 `idempotency_key + 同请求` 复用历史成功结果，不重复执行治理动作。
3. 相同 `idempotency_key + 不同请求` 返回冲突（409），避免误复用。
4. 治理执行失败会持久化运行记录（`status/error_type/error_message/attempt`）。
5. 治理执行支持 `retry_run_id`，仅允许对 failed 记录重试并自动递增 `attempt`。
6. 新增治理运行历史查询接口：
   `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`62 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 幂等语义是否严格：复用与冲突路径是否可解释、可追踪。
2. 失败记录完整性：失败时是否稳定落盘并保留错误上下文。
3. 重试约束是否合理：`retry_run_id` 是否仅接受 failed 记录。
4. 运行历史契约是否满足运维消费（分页、状态、attempt、错误信息）。
5. API 契约、异常路径与测试证据是否一致。
