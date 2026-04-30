# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第七轮，生产化增强验收）：

## 评审目标

1. 验证 benchmark 版本仓巡检与自修复能力是否达到生产可运维标准。
2. 验证生命周期治理闭环（restore/diff/audit/prune/health/repair）是否完整。
3. 验证 failed/malformed 快照的检测与隔离行为是否可靠。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/versions/health`
- `POST /api/narrative/v7/benchmark/versions/repair`
- `POST /api/narrative/v7/benchmark/versions/prune`
- `GET /api/narrative/v7/benchmark/versions/diff`
- `GET /api/narrative/v7/benchmark/audit/export`
- `tests/test_narrative_v7_modules.py` / `tests/test_narrative_v7_api.py` 的 repair/health 路径

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第七轮生产化验收）
5. 第八轮建议切片（按 PR-AA 编号）
