# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第十一轮，生产化增强验收）：

## 评审目标

1. 验证维护告警事件持久化能力是否达到生产可运维标准。
2. 验证告警事件写入与列表查询接口契约是否稳定可用。
3. 验证告警事件与实时告警摘要字段语义的一致性。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/maintenance/alert/emit`
- `GET /api/narrative/v7/benchmark/maintenance/alerts`
- `GET /api/narrative/v7/benchmark/maintenance/alert`
- `GET /api/narrative/v7/benchmark/maintenance/report`
- `GET /api/narrative/v7/benchmark/versions/health`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第十一轮生产化验收）
5. 第十二轮建议切片（按 PR-AA 编号）
