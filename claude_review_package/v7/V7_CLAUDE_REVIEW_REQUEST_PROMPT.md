# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十五轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件一键自愈（`escalations/auto-remediate`）接口契约与执行语义。
2. 验证 auto-remediate 对 escalation digest 推荐动作的执行一致性。
3. 验证 `dry_run` 与 `apply` 两条路径在副作用与返回快照上的一致性。
4. 验证执行结果字段（`executed/emitted/pruned`）与实际日志变化匹配。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`
  - 动作字段：`action/executed/emitted/pruned`
  - 审计字段：`emitted_event/auto_prune/digest_before/digest_after`
  - 语义字段：`dry_run/message`
- 关联核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalation/emit`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十五轮生产化验收）
5. 第三十六轮建议切片（按 PR-AA 编号）