# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第十九轮，生产化增强验收）：

## 评审目标

1. 验证维护告警归档清理策略治理能力是否达到生产可运维标准。
2. 验证 archive cleanup 的 ttl/max-shard 阈值与 dry-run/apply 行为是否稳定可用。
3. 验证 archive cleanup 与 archive/files 接口语义是否一致且可追踪。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alerts/archive`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/auto-archive`
- `POST /api/narrative/v7/benchmark/maintenance/alerts/archive/cleanup`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/archive/files`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/archive/read`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/export`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/digest`
- `GET /api/narrative/v7/benchmark/maintenance/alerts/summary`
- `GET /api/narrative/v7/benchmark/maintenance/alert`
- `GET /api/narrative/v7/benchmark/maintenance/alerts`
- `GET /api/narrative/v7/benchmark/maintenance/report`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第十九轮生产化验收）
5. 第二十轮建议切片（按 PR-AA 编号）
