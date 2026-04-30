# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十三轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件日志自动清理（`escalations/auto-prune`）的接口契约与策略行为。
2. 验证 `dry_run` 与 `apply` 两条路径的统计口径一致性。
3. 验证环境变量阈值策略（trigger/keep_last）生效正确性。
4. 验证自动清理后升级事件列表与保留策略一致。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`
  - 策略字段：`trigger_count/keep_last`
  - 统计字段：`total_events/malformed_line_count/should_prune`
  - 明细字段：`prune.dry_run/prune.candidate_count/prune.pruned_count`
- 关联核验：
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/prune`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十三轮生产化验收）
5. 第三十四轮建议切片（按 PR-AA 编号）