# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第二十三轮生产化增强验收）：

## 评审目标

1. 验证治理运行历史摘要能力是否满足生产值班可观测要求。
2. 验证摘要统计、最新运行、最新失败记录语义是否准确一致。
3. 验证摘要接口与治理运行链路（run/list/prune）契约一致性。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/summary`
  - `total_records/window_record_count` 是否与历史窗口一致
  - `succeeded_count/failed_count` 是否正确
  - `latest_run/latest_failed_run` 是否可用于快速定位
  - `malformed_line_count` 统计是否可靠
- 关联核验：
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第二十三轮生产化验收）
5. 第二十四轮建议切片（按 PR-AA 编号）
