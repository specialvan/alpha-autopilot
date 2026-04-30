# V7 Claude 评审验收提交清单（第三十五轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十五轮生产化增强进行验收（治理升级事件一键自愈能力）。

## 1. 需求与计划文档

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 代码提交范围

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `backend/app/services/narrative_v7/benchmark_library.py`
4. `backend/app/api/routes/narrative_v7.py`
5. `tests/test_narrative_v7_modules.py`
6. `tests/test_narrative_v7_api.py`

## 3. 第三十五轮能力增强

1. 新增治理升级事件一键自愈能力：`auto_remediate_maintenance_alert_governance_escalations`。
2. 新增一键自愈 API：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`。
3. 自愈策略基于 escalation digest 推荐动作执行（`emit_escalation/auto_prune_escalations`）。
4. 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`。
5. 输出执行细节（`emitted/pruned/emitted_event/auto_prune`）便于值班审计。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`94 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. `auto-remediate` 在 `emit_escalation` 与 `auto_prune_escalations` 两条动作分支的执行一致性。
2. `dry_run` 预演路径是否保证无副作用且返回动作建议与摘要快照。
3. apply 路径下 `executed/emitted/pruned` 与实际日志变更是否一致。
4. `digest_before/digest_after` 是否可用于值班审计追踪。