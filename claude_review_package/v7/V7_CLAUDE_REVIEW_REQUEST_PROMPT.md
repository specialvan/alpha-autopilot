# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十二轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件日志清理（`escalations/prune`）的接口契约与生命周期行为。
2. 验证 `dry_run` 与 `apply` 两条路径的统计口径一致性。
3. 验证脏行（malformed）计数与清理行为可追溯。
4. 验证清理后升级事件列表与保留策略（`keep_last`）一致。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/prune`
  - 统计字段：`total_events_before/kept_count/candidate_count/pruned_count`
  - 脏行字段：`malformed_candidate_count/malformed_dropped_count`
  - 语义字段：`dry_run/keep_last/message`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/export`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十二轮生产化验收）
5. 第三十三轮建议切片（按 PR-AA 编号）
