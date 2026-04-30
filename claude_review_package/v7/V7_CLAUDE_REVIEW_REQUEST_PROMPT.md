# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第八轮，生产化增强验收）：

## 评审目标

1. 验证 benchmark 维护报告能力是否达到生产可运维标准。
2. 验证生命周期治理闭环（restore/diff/audit/prune/health/repair/report）是否完整。
3. 验证建议分级（ok/warn/critical）是否合理、可执行。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/report`
- `GET /api/narrative/v7/benchmark/versions/health`
- `POST /api/narrative/v7/benchmark/versions/repair`
- `POST /api/narrative/v7/benchmark/versions/prune`
- `GET /api/narrative/v7/benchmark/versions/diff`
- `GET /api/narrative/v7/benchmark/audit/export`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第八轮生产化验收）
5. 第九轮建议切片（按 PR-AA 编号）
