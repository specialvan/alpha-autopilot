# V7 Claude 评审验收提交清单（第五轮生产化）

- 日期：2026-04-30
- 提交目标：请求 Claude 对 V7 阶段 `PR-AA-26~39` 第五轮生产化增强做验收（版本完整性、审计导出、差异对比、版本清理治理）

## 1. 需求与计划文档

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 治理文档工程包

1. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/README.md`
2. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_START_HERE.md`
3. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_CODEX_DEVELOPMENT_GOVERNANCE.md`
4. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_REQUIREMENT_INTAKE_TEMPLATE.md`
5. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_REQUIREMENT_EXECUTION_FLOW.md`
6. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_TEST_GOVERNANCE.md`
7. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_EXECUTION_GOVERNANCE.md`
8. `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/V7_SKILL_MAPPING.md`

## 3. 代码提交范围

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `backend/app/services/narrative_v7/benchmark_library.py`
4. `backend/app/api/routes/narrative_v7.py`
5. `tests/test_narrative_v7_modules.py`
6. `tests/test_narrative_v7_api.py`

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`26 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 评审重点建议

- benchmark 快照完整性校验与 tamper 拦截是否可靠
- 版本差异对比与审计导出是否满足治理追溯
- 版本清理（prune）能力是否安全可控（dry_run + keep_last）
- 新增接口契约与测试覆盖是否一致
