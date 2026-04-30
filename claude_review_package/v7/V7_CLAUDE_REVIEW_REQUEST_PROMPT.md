# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第十轮，生产化增强验收）：

## 评审目标

1. 验证 `maintenance/alert` 的 SLA 阈值治理是否达到生产可运维标准。
2. 验证告警分级与动作建议（page/ticket）是否可执行。
3. 验证阈值环境变量配置是否具备可控性与回滚性。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alert`
- `GET /api/narrative/v7/benchmark/maintenance/report`
- `POST /api/narrative/v7/benchmark/versions/auto-remediate`
- `POST /api/narrative/v7/benchmark/versions/repair`
- `POST /api/narrative/v7/benchmark/versions/prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第十轮生产化验收）
5. 第十一轮建议切片（按 PR-AA 编号）
