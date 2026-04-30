# V7 Claude 评审验收提交清单（第三十六轮生产化）
- 日期：2026-05-01
- 提交目标：请对 V7 阶段 `PR-AA-26~39` 第三十六轮生产化增强进行验收（治理升级事件发射冷却与重复防抖）。

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

## 3. 第三十六轮能力增强

1. 新增治理升级事件发射冷却策略（cooldown）与重复防抖。
2. 新增策略环境变量：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_EMIT_COOLDOWN_SECONDS`。
3. 升级发射接口支持冷却旁路参数：`ignore_cooldown`。
4. 发射响应新增抑制审计字段：`suppressed/suppression_reason/suppressed_by_event_id/cooldown_seconds`。
5. 防止同源同签名升级事件在冷却窗口内重复写入，降低告警风暴风险。

## 4. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`96 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 建议评审重点

1. cooldown 抑制判定是否仅命中“同源+同签名+冷却窗口内”的重复发射。
2. 抑制响应字段与已有日志事件是否可审计追溯。
3. `ignore_cooldown=true` 是否可安全旁路并生成新事件。
4. 冷却策略是否不会误伤跨源事件（manual_emit vs auto_remediate）。