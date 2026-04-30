# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十八轮生产化增强验收）：

## 评审目标

1. 验证治理运行重试上限策略是否正确生效。
2. 验证 Digest 在失败超限场景下的升级动作（`escalate_failed_run`）是否稳定。
3. 验证 auto-remediate 在升级场景下是否输出可执行升级信号。
4. 验证新增 `422 retry_attempt_limit_exceeded` API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
  - 重试上限：`retry_attempt_limit_exceeded`（422）
  - 重试链路：`retry_run_id / attempt`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
  - 升级信号：`recommended_action=escalate_failed_run`
  - 预算字段：`retry_max_attempts/latest_failed_attempt/retry_exhausted`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
  - 升级输出：`escalation_required/escalation_reason`
  - 对比输出：`digest_before/digest_after`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十八轮生产化验收）
5. 第二十九轮建议切片（按 PR-AA 编号）
