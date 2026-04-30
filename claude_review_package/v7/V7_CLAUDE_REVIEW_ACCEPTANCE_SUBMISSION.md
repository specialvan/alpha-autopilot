# V7 Claude 评审验收提交清单（第四轮生产化）

- 日期：2026-04-30
- 提交目标：请求 Claude 对 V7 阶段 `PR-AA-26~39` 第四轮生产化增强做验收（版本完整性校验、差异对比、审计导出、恢复回滚保护）

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
2. `backend/app/services/narrative_v7/decision_controller.py`
3. `backend/app/services/narrative_v7/decision_rules.py`
4. `backend/app/services/narrative_v7/decision_rules.default.json`
5. `backend/app/services/narrative_v7/benchmark_store.py`
6. `backend/app/services/narrative_v7/benchmark_library.py`
7. `backend/app/services/narrative_v7/observability.py`
8. `backend/app/services/narrative_v7/__init__.py`
9. `backend/app/api/routes/narrative_v7.py`
10. `tests/test_narrative_v7_modules.py`
11. `tests/test_narrative_v7_api.py`

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`24 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 评审重点建议

- 规则外置后 R-01~R-10 路由行为是否稳定可控
- benchmark 快照 `rows_sha256` 完整性校验是否可靠
- restore 的 tamper 拦截与 `backup_version` 保护是否满足生产回滚要求
- 版本差异对比（added/removed/activated/deactivated/mean_changed）是否满足审计追踪
- 审计导出接口是否足以支撑后续离线验收与治理归档
