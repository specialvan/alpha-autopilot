# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件发射门禁与事件字段是否满足值班追踪需求。
2. 验证升级事件 API（emit/list）契约与分页语义是否稳定。
3. 验证 auto-remediate 升级场景是否自动发射并回填 escalation event。
4. 验证升级事件与 Digest 推荐动作一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit`
  - 发射门禁：`emitted` / `message=no_escalation_needed|escalation_emitted`
  - 事件字段：`source/recommended_action/escalation_reason/latest_run_id/latest_failed_run_id`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
  - 分页字段：`cursor/next_cursor/has_more`
  - 计数字段：`total_events/malformed_line_count`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
  - 升级输出：`escalation_required/escalation_reason/escalation_event`
  - 对比输出：`digest_before/digest_after`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十轮生产化验收）
5. 第三十一轮建议切片（按 PR-AA 编号）
