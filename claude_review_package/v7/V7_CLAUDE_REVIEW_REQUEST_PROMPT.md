# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第四轮，生产化增强验收）：

## 评审目标

1. 验证 PR-AA-26~39 的阶段产物是否达到可生产运维标准。
2. 验证 benchmark 版本资产的完整性与可审计性（校验、对比、导出、恢复）。
3. 验证 restore 的回滚保护策略是否足够稳健。
4. 验证新增 API 契约与测试覆盖是否一致。
5. 给出进入下一轮（线上准实时数据校准）的阻断项与优先级。

## 重点检查项

- `V7BenchmarkStore` 的 `rows_sha256` 校验逻辑
- tampered snapshot 的 restore 拒绝机制
- `backup_version` 备份与恢复流程的一致性
- `GET /api/narrative/v7/benchmark/versions/diff`
- `GET /api/narrative/v7/benchmark/audit/export`
- `tests/test_narrative_v7_modules.py` 与 `tests/test_narrative_v7_api.py` 是否覆盖关键失败路径

## 提交材料索引

- `claude_review_package/v7/V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md`
- `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`
- `backend/app/services/narrative_v7/*`
- `backend/app/api/routes/narrative_v7.py`
- `tests/test_narrative_v7_modules.py`
- `tests/test_narrative_v7_api.py`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第四轮生产化验收）
5. 第五轮建议切片（按 PR-AA 编号）
