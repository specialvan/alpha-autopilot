# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十六轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件发射冷却（cooldown）与重复防抖语义。
2. 验证抑制审计字段与日志事件追溯一致性。
3. 验证 `ignore_cooldown` 旁路能力在人工介入场景下可用。
4. 验证冷却策略不会误伤跨源升级事件链路。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit`
  - 抑制字段：`suppressed/suppression_reason/suppressed_by_event_id/cooldown_seconds`
  - 语义字段：`emitted/message`
  - 旁路参数：`ignore_cooldown`
- 关联核验：
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十六轮生产化验收）
5. 第三十七轮建议切片（按 PR-AA 编号）