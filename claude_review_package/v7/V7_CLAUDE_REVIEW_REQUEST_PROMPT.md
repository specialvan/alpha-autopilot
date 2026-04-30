# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十五轮生产化增强验收）：

## 评审目标

1. 验证治理运行日志自动清理策略是否满足生产运维要求。
2. 验证自动清理接口在 `dry_run/apply` 两条路径下契约一致性。
3. 验证环境变量策略与自动清理行为的联动一致性。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`
  - 触发判定：`should_prune`
  - 策略参数：`trigger_count/keep_last`
  - 执行结果：`prune` 结构（candidate/pruned/malformed）
  - `dry_run` 与 `apply` 的行为差异是否正确
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十五轮生产化验收）
5. 第二十六轮建议切片（按 PR-AA 编号）
