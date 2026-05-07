# V6/V7 正式生产工程收口包（2026-05-05）

## 1. 收口目标

- 将 V6 / V7 从“任务板完成”收紧到“具备独立门禁、可快速关停、可回读验收证据”的状态。
- 保持 `v1/v2` baseline 默认链路不变，不让 V6 / V7 误伤既有默认推荐路径。

## 2. 本次补齐项

### 2.1 V6

- 新增全局开关 `v6_enabled`：`backend/app/core/config.py`
- `backend/app/api/routes/narrative_v6.py` 全路由接入统一开关检查，关闭时返回 `503 / v6_disabled`
- V6 仍保持 additive route boundary，仅暴露 `/api/narrative/v6/*` 与其观测接口

### 2.2 V7

- `scripts/run_layered_tests.py` 新增 `v7` layer
- 新增正式 gate 脚本：`scripts/run_v7_acceptance_review.py`
- 新增 gate 测试：`tests/test_run_v7_acceptance_review.py`
- `tests/test_run_layered_tests.py` 补齐 `v7` layer 覆盖

## 3. 最新验收证据

1. 变更级回归
- 命令：`python -m pytest tests/test_run_layered_tests.py tests/test_run_v7_acceptance_review.py tests/test_narrative_v6_api.py -q`
- 结果：`21 passed`

2. V7 正式 gate
- 命令：`python scripts/run_v7_acceptance_review.py`
- 报告：`artifacts/acceptance/v7-acceptance-20260505T072501Z.md`
- 关键结果：
  - `v7_targeted_gate`：`113 passed`
  - `v7_compile_gate`：通过
  - `layered_regression_gate`：`v7 107 passed` + `api 24 passed` + `frontend 19 passed`

3. V6 正式 gate
- 命令：`python scripts/run_v6_acceptance_review.py`
- 报告：`artifacts/acceptance/v6-acceptance-20260505T072535Z.md`
- 关键结果：
  - `v6_targeted_gate`：`38 passed`
  - `layered_regression_gate`：`v6 53 passed` + `api 24 passed` + `v4 38 passed` + `frontend 19 passed`
  - `frontend_build_gate`：通过

## 4. 回滚 / 关停路径

- V6：设置 `v6_enabled=false` 后重启服务，直接拒绝 `/api/narrative/v6/*` 与 `/api/narrative/v6/observability`
- V7：设置 `v7_enabled=false` 后重启服务，直接拒绝 `/api/narrative/v7/*`
- 两个版本都保持独立增量边界；当前 baseline 默认路径仍然是 `v1/v2`

## 5. 文档裁决说明

- `claude_review_package/v7/V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md` 的标题仍停留在“第 37 轮”，但正文实际已经连续记录到 `Round-61`
- 本收口包用于给出 2026-05-05 时点的正式门禁快照、回滚位与统一证据入口

## 6. 非阻断残余项

- V6 graph memory 与 V7 benchmark governance 仍以本地 JSONL / 文件工件为主，尚未接远端持久化与远端告警通道
- V7 governance 路由树已非常深，后续应优先冻结深度并做能力收敛，而不是继续递归扩展
- 本次收口没有扩大默认暴露面，也没有替换 `v1/v2` 默认行为
