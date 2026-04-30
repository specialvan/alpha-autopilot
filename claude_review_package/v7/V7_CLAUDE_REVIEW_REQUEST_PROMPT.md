# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第九轮，生产化增强验收）：

## 评审目标

1. 验证 `auto-remediate` 是否达到生产可运维的一键治理标准。
2. 验证治理闭环（health/repair/prune）串联逻辑与可解释性。
3. 验证 dry-run 与实执行结果是否一致可靠。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `POST /api/narrative/v7/benchmark/versions/auto-remediate`
- `GET /api/narrative/v7/benchmark/maintenance/report`
- `GET /api/narrative/v7/benchmark/versions/health`
- `POST /api/narrative/v7/benchmark/versions/repair`
- `POST /api/narrative/v7/benchmark/versions/prune`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第九轮生产化验收）
5. 第十轮建议切片（按 PR-AA 编号）
