# V7 Claude Review Request Prompt

请对以下提交做 V7 阶段评审（第一轮，骨架验收）：

## 评审目标

1. 验证 PR-AA-26~39 的代码骨架映射是否完整。
2. 验证 R-01~R-10 路由规则是否满足最小可用控制闭环。
3. 验证治理文档工程包是否足以支撑后续迭代验收。
4. 给出进入第二轮（生产化加深）的阻断项与优先级。

## 重点检查项

- `NarrativeMarketState`、`NQMSampler`、`ThresholdBand`、`DecisionFeedbackController`
- `OpeningGate`、`ExpectationDebt`、`DeadlockRouter`、`AntiPatternRegistry`
- `BenchmarkStore`/`BenchmarkLibrary` 的入库、查询、撤回闭环
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
4. 可验收结论（是否通过第一轮骨架验收）
5. 第二轮建议切片（按 PR-AA 编号）
