# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第六轮，生产化增强验收）：

## 评审目标

1. 验证 benchmark 版本仓健康扫描能力是否达到可运维标准。
2. 验证生命周期治理闭环（restore/diff/audit/prune/health）是否完整。
3. 验证高风险失败路径（tamper、malformed）是否可被识别并告警。
4. 验证新增 API 契约与测试证据一致性。

## 重点检查项

- `GET /api/narrative/v7/benchmark/versions/health`
- `POST /api/narrative/v7/benchmark/versions/prune`
- `GET /api/narrative/v7/benchmark/versions/diff`
- `GET /api/narrative/v7/benchmark/audit/export`
- `tests/test_narrative_v7_modules.py` / `tests/test_narrative_v7_api.py` 中 health/prune/integrity 路径

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第六轮生产化验收）
5. 第七轮建议切片（按 PR-AA 编号）
