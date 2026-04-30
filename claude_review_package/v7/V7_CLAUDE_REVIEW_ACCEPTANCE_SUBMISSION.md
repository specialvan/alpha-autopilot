# V7 Claude 评审验收提交清单（第十七轮生产化）

- 日期：2026-04-30
- 提交目标：请求 Claude 对 V7 阶段 `PR-AA-26~39` 第十七轮生产化增强做验收（维护告警归档索引 + 归档读取分页治理）

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

## 3. 测试清单

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 执行命令：`pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 结果：`52 passed`
5. 编译检查：`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 4. 评审重点建议

- `GET /benchmark/maintenance/alerts/archive/files` 的归档索引输出是否稳定可用
- `GET /benchmark/maintenance/alerts/archive/read` 的分页读取语义（cursor/next_cursor/has_more）是否正确
- 归档读取接口的文件名安全约束（路径穿越拦截）是否生效
- 归档索引/读取与归档分片接口之间的数据一致性是否可追踪
- 接口契约、异常路径与测试证据是否一致
