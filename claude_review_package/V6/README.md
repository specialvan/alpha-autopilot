# V6 文档入口（动态故事世界推演）

## 1. 作用

`V6/` 目录是下一轮动态故事世界推演的执行入口，负责把 `V6_MIROFISH_PR_REQUIREMENTS.md` 落成可直接执行的评审、拆 PR、任务排期与验收门禁材料。

## 2. 权威需求基线

- 主需求文档：`claude_review_package/V6/V6_MIROFISH_PR_REQUIREMENTS.md`
- 治理上位文档：`claude_review_package/CODEX_DEVELOPMENT_GOVERNANCE.md`
- 执行入口文档：`claude_review_package/README_FOR_CODEX.md`

## 3. 本目录执行文档

1. `V6_MIROFISH_PR_REQUIREMENTS.md`：V6 主需求、范围、PR-AA-09~15 详细验收标准
2. `V6_REVIEW_DEV_TASK.md`：给 Codex/Claude 的本轮评审与开发任务单
3. `V6_PR_SPLIT_PLAN.md`：PR 拆分、依赖顺序、并行策略与回滚口径
4. `V6_IMPLEMENTATION_TASK_BOARD.md`：单任务推进任务板（按 T01~T17 串行）
5. `V6_DEVELOPMENT_ACCEPTANCE_CHECKLIST.md`：开发验收清单（按 PR 验收）
6. `V6_ACCEPTANCE_HANDOFF_2026_04_28.md`：V6 全量验收交接与证据汇总
7. `V6_CLAUDE_ACCEPTANCE_REVIEW_TASK_2026_04_28.md`：外部验收评审任务单

## 4. 默认执行顺序

1. 先读 `V6_MIROFISH_PR_REQUIREMENTS.md`
2. 再读 `V6_REVIEW_DEV_TASK.md`
3. 再读 `V6_PR_SPLIT_PLAN.md`
4. 按 `V6_IMPLEMENTATION_TASK_BOARD.md` 进入单任务执行
5. 每轮交付用 `V6_DEVELOPMENT_ACCEPTANCE_CHECKLIST.md` 做门禁
6. 先看 `V6_ACCEPTANCE_HANDOFF_2026_04_28.md` 核对证据
7. 需要外部复核时使用 `V6_CLAUDE_ACCEPTANCE_REVIEW_TASK_2026_04_28.md`

## 5. 边界提醒

- `v1/v2` 基线路径不被 V6 直接替换
- V6 新能力默认进入 `Increment`，必须可降级、可回滚
- 未经作者确认的模拟结果/访谈内容，不写入正式 Story Bible
