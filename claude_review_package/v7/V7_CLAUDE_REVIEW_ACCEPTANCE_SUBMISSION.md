# V7 Claude 评审验收提交清单（第三十三轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十三轮生产化增强进行验收（治理升级事件日志自动清理策略）。

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

## 3. 第三十三轮能力增强

1. 新增治理升级事件日志自动清理策略：`auto_prune_maintenance_alert_governance_escalations`。
2. 新增自动清理 API：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`。
3. 支持 `dry_run/apply` 双路径，便于先验收再执行。
4. 支持策略化阈值环境变量：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT` 与 `AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_KEEP_LAST`。
5. 输出 `should_prune` 与 `prune` 详情，便于值班联动与审计。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`90 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. `escalations/auto-prune` 的 `dry_run/apply` 语义是否清晰且可复现。
2. 策略阈值是否按环境变量正确生效（trigger/keep_last）。
3. `total_events/malformed_line_count/should_prune` 与 `prune` 明细口径是否一致。
4. 自动清理后 `GET /escalations` 结果是否与保留策略一致。