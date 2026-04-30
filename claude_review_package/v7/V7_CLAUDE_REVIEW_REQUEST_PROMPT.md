# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十一轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件摘要统计与导出结构是否满足值班消费需求。
2. 验证升级事件摘要/导出 API 契约与分页语义是否稳定。
3. 验证摘要统计口径与原始事件列表一致性。
4. 验证同秒多事件场景下排序与导出稳定性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary`
  - 统计字段：`manual_emit_count/auto_remediate_count/retry_exhausted_count/failure_streak_exhausted_count`
  - 计数字段：`total_events/window_event_count/malformed_line_count`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/export`
  - 导出结构：`summary + events`
  - 分页字段：`cursor/next_cursor/has_more`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十一轮生产化验收）
5. 第三十二轮建议切片（按 PR-AA 编号）
