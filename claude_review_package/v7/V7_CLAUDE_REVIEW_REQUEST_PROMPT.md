# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第三轮，生产化增强验收）：

## 评审目标

1. 验证 PR-AA-26~39 的代码骨架映射是否完整并可持续演进。
2. 验证 R-01~R-10 路由规则外置后是否保持可解释与可控。
3. 验证 benchmark 资产层是否支持版本快照、列表查询与恢复回放。
4. 验证 observability 阈值配置化是否满足生产运维需求。
5. 给出进入下一轮（实战数据校准）的阻断项与优先级。

## 重点检查项

- `DecisionRuleSet` 与 `DecisionFeedbackController` 的规则加载与默认回退行为
- `V7BenchmarkStore` / `BenchmarkLibrary` 的 ingest/retract/version/restore 闭环
- `GET /api/narrative/v7/decision/rules`
- `GET /api/narrative/v7/benchmark/versions`
- `POST /api/narrative/v7/benchmark/restore/{version}`
- observability 的 `thresholds` 输出与阈值判定逻辑
- API 契约一致性与测试覆盖完整性
- 任务板 checklist 是否与代码实际一致

## 提交材料索引

- `claude_review_package/v7/V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md`
- `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`
- `claude_review_package/v7/CODEX_V7_GOVERNANCE_PACKAGE/*`
- `backend/app/services/narrative_v7/*`
- `backend/app/api/routes/narrative_v7.py`
- `tests/test_narrative_v7_modules.py`
- `tests/test_narrative_v7_api.py`

## 输出要求

请按以下结构输出：

1. 阻断问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三轮生产化验收）
5. 第四轮建议切片（按 PR-AA 编号）
