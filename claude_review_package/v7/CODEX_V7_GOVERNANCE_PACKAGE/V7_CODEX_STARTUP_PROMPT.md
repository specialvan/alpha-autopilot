# V7 Codex Startup Prompt

你正在 `alpha-autopilot` 的 V7 开发上下文中工作。请严格遵守以下顺序：

1. 先读取 `V7_START_HERE.md` 与 `V7_CODEX_DEVELOPMENT_GOVERNANCE.md`。
2. 明确需求属于 Baseline / Increment / Experimental 哪一层。
3. 新功能默认进入 Increment，不得默认改写 `v1/v2` 基线。
4. 需求必须映射到 `PR-AA-26 ~ PR-AA-39` 或其子任务。
5. 执行前补齐：影响面、测试计划、回滚路径。
6. 执行后补齐：测试证据、评估证据、回滚演练、文档同步。
7. 如发生文档冲突，优先治理规范，再总路线图，再 V7 计划文档。

输出要求：

- 先给层级判断与风险判断。
- 再给最小安全执行方案。
- 最后给验证证据与可回滚结论。
