# Codex 最终启动提示词

你正在处理 `alpha-autopilot` 项目。请严格按照以下治理方式执行：

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

## 默认规则

- `v1/v2` 是 Baseline，只允许收口和维护
- `v3` 是 Increment，所有新增功能优先进入这里
- Experimental 必须隔离，不能污染主线
- 每次只做一个清晰目标
- 不要跨层级扩张
- 改完必须更新相关状态文档

## 新需求处理顺序

1. 先填 `new_requirement_intake_template.md`
2. 再看 `new_requirement_execution_flow.md`
3. 判定属于 Baseline / Increment / Experimental
4. 决定是否进入开发
5. 做最小改动
6. 补测试
7. 更新文档
8. 验证可回滚
9. 收口

## 变更原则

- 如果不改变主线边界，只做局部更新
- 如果改变主线边界，要重新收敛治理文档
- 如果只是实验探索，隔离到 Experimental
- 如果是历史材料，归档，不要拿来定义当前路线

## 一句话要求

> 先判层级，再做变更；先保基线，再做增量；先补测试，再更新文档；先确认可回滚，再允许推进。