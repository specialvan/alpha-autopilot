# V7 Claude 评审验收提交清单（第三轮生产化）

- 日期：2026-04-30
- 提交目标：请求 Claude 对 V7 阶段 `PR-AA-26~39` 第三轮生产化增强做验收（规则外置、版本快照/恢复、可观测阈值配置）

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
2. `backend/app/services/narrative_v7/nqm_sampler.py`
3. `backend/app/services/narrative_v7/ohlcv.py`
4. `backend/app/services/narrative_v7/threshold_band.py`
5. `backend/app/services/narrative_v7/decision_controller.py`
6. `backend/app/services/narrative_v7/decision_rules.py`
7. `backend/app/services/narrative_v7/decision_rules.default.json`
8. `backend/app/services/narrative_v7/opening_gate.py`
9. `backend/app/services/narrative_v7/expectation_debt.py`
10. `backend/app/services/narrative_v7/deadlock_router.py`
11. `backend/app/services/narrative_v7/antipattern_registry.py`
12. `backend/app/services/narrative_v7/emotion_satisfaction.py`
13. `backend/app/services/narrative_v7/loop_structure.py`
14. `backend/app/services/narrative_v7/pacing_controller.py`
15. `backend/app/services/narrative_v7/benchmark_store.py`
16. `backend/app/services/narrative_v7/benchmark_library.py`
17. `backend/app/services/narrative_v7/benchmark_refit.py`
18. `backend/app/services/narrative_v7/contract_guard.py`
19. `backend/app/services/narrative_v7/common.py`
20. `backend/app/services/narrative_v7/__init__.py`
21. `backend/app/services/narrative_v7/observability.py`
22. `backend/app/api/routes/narrative_v7.py`
23. `backend/app/main.py`
24. `backend/app/core/config.py`

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`20 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 评审重点建议

- PR-AA-26~39 的结构映射是否完整
- R-01~R-10 路由优先级是否合理，且规则外置后是否保持行为可控
- T8/T4/T9/W5/W6/A6 关键门禁是否具备最小可用性
- Benchmark 入库/撤回/版本快照/恢复是否满足审计回放要求
- feature flag、错误码与 observability（含阈值配置）是否达到生产级可运维要求
- 下一轮生产化增强的阻断项与优先级
