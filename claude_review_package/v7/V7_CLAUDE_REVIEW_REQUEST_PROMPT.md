# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十六轮生产化增强验收）：

## 评审目标

1. 验证治理运行健康 Digest 能力是否满足值班可观测要求。
2. 验证 Digest 推荐动作与失败/新鲜度状态的一致性。
3. 验证新鲜度阈值策略环境变量对输出行为的影响是否正确。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
  - 新鲜度字段：`stale_threshold_seconds/latest_run_age_seconds/is_stale`
  - 推荐动作：`recommended_action`
  - 摘要字段：`summary`（尤其 `failed_count/latest_run/latest_failed_run`）
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/summary`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十六轮生产化验收）
5. 第二十七轮建议切片（按 PR-AA 编号）
