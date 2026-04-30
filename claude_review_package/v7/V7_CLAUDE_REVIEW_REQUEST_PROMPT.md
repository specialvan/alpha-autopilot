# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第五轮，生产化增强验收）：

## 评审目标

1. 验证 V7 benchmark 资产层是否具备生产级完整性保障（hash 校验、tamper 拦截）。
2. 验证版本审计能力是否完整（versions/diff/audit/export）。
3. 验证版本生命周期治理是否可运维（versions/prune + dry_run + keep_last）。
4. 验证新增 API 契约与测试覆盖一致性。
5. 给出进入下一轮（线上数据联调）的阻断项与优先级。

## 重点检查项

- `rows_sha256` 与 `integrity_status` 的正确性
- restore 失败路径：`snapshot_integrity_failed` 与 `backup_version`
- `GET /api/narrative/v7/benchmark/versions/diff`
- `GET /api/narrative/v7/benchmark/audit/export`
- `POST /api/narrative/v7/benchmark/versions/prune`
- `tests/test_narrative_v7_modules.py` / `tests/test_narrative_v7_api.py` 是否覆盖关键路径

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
4. 可验收结论（是否通过第五轮生产化验收）
5. 第六轮建议切片（按 PR-AA 编号）
