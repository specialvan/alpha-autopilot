# START HERE

这是 `alpha-autopilot` 的快速启动入口。

## 给 Codex 的最短阅读顺序

1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `claude_review_package/README_FOR_CODEX.md`
3. `claude_review_package/codex_short_command_card.md`
4. `claude_review_package/task_launch_template.md`
5. `claude_review_package/new_requirement_intake_template.md`
6. `claude_review_package/new_requirement_execution_flow.md`

## 你需要先确认的三件事

- 这个任务属于 `Baseline`、`Increment` 还是 `Experimental`
- 它会不会影响 `v1/v2` 主线边界
- 它需不需要先补测试、先补文档、或者先加回滚

## 默认执行原则

- 一次只做一个目标
- 新功能默认进 `Increment`
- 实验性内容必须隔离
- 改完必须更新状态文档
- 不能让历史文档反向定义当前路线

## 如果是新需求

优先按这个顺序处理：

1. 填 `task_launch_template.md`
2. 必要时再填 `new_requirement_intake_template.md`
3. 按 `new_requirement_execution_flow.md` 执行
4. 按 `test_governance.md` 补测试
5. 按 `execution_governance.md` 收口

## 一句话

> 先判层级，再做变更；先保基线，再做增量；先补测试，再更新文档。