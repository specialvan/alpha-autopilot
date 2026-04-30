# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十七轮生产化增强验收）：

## 评审目标

1. 验证治理运行一键自愈能力是否满足生产值班联动要求。
2. 验证自愈动作选择与 Digest 推荐动作的一致性。
3. 验证失败重试自愈路径的稳定性与可追踪性。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
  - 动作选择：`action`
  - 执行结果：`executed/governance_run/auto_prune`
  - 对比输出：`digest_before/digest_after`
  - 干跑路径：`dry_run`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十七轮生产化验收）
5. 第二十八轮建议切片（按 PR-AA 编号）
