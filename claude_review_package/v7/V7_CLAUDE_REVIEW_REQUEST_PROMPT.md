# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十二轮生产化增强验收）：

## 评审目标

1. 验证治理运行日志生命周期治理能力是否达到生产可运维标准。
2. 验证治理运行日志清理接口在 `dry_run/apply` 两条路径下的契约一致性。
3. 验证脏行统计与清理语义是否准确可靠。
4. 验证历史排序稳定性修复是否有效。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune`
  - `keep_last` 保留窗口是否正确
  - `dry_run` 是否仅返回候选，不落盘删除
  - `apply` 是否正确落盘并输出 `pruned_count`
  - `malformed_candidate_count/malformed_dropped_count` 是否语义一致
- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - 清理前后 `total_records` 与窗口数据是否匹配
  - 记录排序是否稳定（失败+重试紧邻场景）

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十二轮生产化验收）
5. 第二十三轮建议切片（按 PR-AA 编号）
