# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十四轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件 Digest（`escalations/digest`）接口契约与动作推荐语义。
2. 验证 Digest 对 runs-digest 与 escalation summary 的联动一致性。
3. 验证升级事件新鲜度判定与阈值配置生效正确性。
4. 验证异常日志（malformed）触发自动清理建议行为。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`
  - 新鲜度字段：`stale_threshold_seconds/latest_event_age_seconds/is_stale`
  - 动作字段：`recommended_action/message`
  - 聚合字段：`summary/run_digest`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/summary`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十四轮生产化验收）
5. 第三十五轮建议切片（按 PR-AA 编号）