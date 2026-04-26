# Codex 最终启动提示

你正在处理 `alpha-autopilot` 项目。以下内容是当前唯一权威口径；如果任何其他启动提示、执行提示或历史文档与本文件冲突，以本文件为准。

## 先读文档

先阅读以下文件：

1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `claude_review_package/README_FOR_CODEX.md`
3. `claude_review_package/codex_run_card.md`
4. `claude_review_package/final_document_index.md`
5. `claude_review_package/package_overview.md`
6. `claude_review_package/new_requirement_intake_template.md`
7. `claude_review_package/new_requirement_execution_flow.md`
8. `claude_review_package/test_governance.md`
9. `claude_review_package/execution_governance.md`
10. `MASTER_ROADMAP.md`
11. `PROJECT_STATUS.md`

## 规则顺序

1. `v1/v2` 是 Baseline，只允许收口和维护。
2. `v3` 是 Increment，所有新功能优先进入这里。
3. Experimental 必须隔离，不能污染主线。
4. 每次只做一个清晰目标。
5. 不能跨层级扩展。
6. 改完必须更新相关状态文档。

## 新需求处理顺序

1. 先填 `new_requirement_intake_template.md`。
2. 再看 `new_requirement_execution_flow.md`。
3. 判定需求属于 Baseline / Increment / Experimental。
4. 决定是否进入开发。
5. 做最小改动。
6. 补测。
7. 更新文档。
8. 验证可回滚。
9. 收口。

## 变更原则

- 如果不改变主线边界，只做局部更新。
- 如果改变主线边界，要重新收敛治理文档。
- 如果只是实验探索，隔离到 Experimental。
- 如果是历史材料，归档，不要拿来定义当前路线。

## 一句话口径

先判层级，再做变更；先保基线，再做增量；先补测试，再更新文档；先确认可回滚，再允许推进。
