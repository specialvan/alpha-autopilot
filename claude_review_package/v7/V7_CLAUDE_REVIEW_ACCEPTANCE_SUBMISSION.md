# V7 Claude 评审验收提交清单（第二十七轮生产化）

- 日期：2026-04-30
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第二十七轮生产化增强进行验收（治理运行一键自愈）

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

## 3. 第二十七轮能力增量

1. 新增治理运行一键自愈能力：`auto_remediate_maintenance_alert_governance_runs`。
2. 新增一键自愈接口：
   `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
3. 自愈策略基于 Digest 推荐动作执行，优先处理最新失败运行（`retry_latest_failed_run`）。
4. 支持 `dry_run/apply` 双路径。
5. 输出 `digest_before/digest_after`，便于比对自愈前后状态。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`74 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. 一键自愈动作选择是否与 Digest 推荐动作一致。
2. 失败重试路径是否稳定（`retry_run_id` 正确绑定最新失败记录）。
3. `dry_run` 与 `apply` 语义是否清晰且可解释。
4. 自愈前后 Digest 对比是否满足值班复盘需求。
