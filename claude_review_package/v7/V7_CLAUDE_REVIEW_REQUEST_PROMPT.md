# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十四轮生产化增强验收）：

## 评审目标

1. 验证治理运行导出能力是否满足生产评审与运维消费要求。
2. 验证导出接口分页契约与数据一致性。
3. 验证导出数据与治理运行历史/摘要语义一致。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/export`
  - 分页契约：`limit/cursor/next_cursor/has_more`
  - 统计契约：`total_records/malformed_line_count`
  - 聚合契约：`summary + records` 是否可直接消费
- 关联一致性核验：
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/summary`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十四轮生产化验收）
5. 第二十五轮建议切片（按 PR-AA 编号）
