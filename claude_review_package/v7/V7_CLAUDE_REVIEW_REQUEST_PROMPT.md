# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十一轮生产化增强验收）：

## 评审目标

1. 验证治理执行幂等机制（`idempotency_key`）是否满足生产可运维标准。
2. 验证治理失败记录与重试机制（`retry_run_id`）是否稳定、可追踪。
3. 验证治理运行历史查询契约是否完整可用。
4. 验证新增 API 契约、异常行为与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
  - 幂等复用路径（同 key 同请求）
  - 幂等冲突路径（同 key 不同请求，409）
  - 失败记录路径（500 后是否有 failed 记录）
  - 重试路径（`retry_run_id` -> attempt 递增）
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - 分页与统计字段（`limit/cursor/next_cursor/has_more/total_records`）
  - 记录字段完整性（`status/attempt/error_type/error_message`）

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十一轮生产化验收）
5. 第二十二轮建议切片（按 PR-AA 编号）
