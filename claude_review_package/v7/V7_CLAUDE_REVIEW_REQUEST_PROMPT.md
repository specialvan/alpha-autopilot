# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第十五轮，生产化增强验收）：

## 评审目标

1. 验证维护告警导出能力是否达到生产可运维标准。
2. 验证导出接口（digest + recent alerts）是否稳定可用且可直接集成。
3. 验证导出接口与 digest/summary/list 接口语义是否一致且可追踪。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

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
4. 可验收结论（是否通过第十五轮生产化验收）
5. 第十六轮建议切片（按 PR-AA 编号）
