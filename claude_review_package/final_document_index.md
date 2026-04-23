# 最终版文档清单

## 1. Mainline（主线依据）

以下文档应视为当前主线执行依据，Codex 默认优先读取：

- `CODEX_DEVELOPMENT_GOVERNANCE.md`
- `MASTER_ROADMAP.md`
- `PROJECT_STATUS.md`
- `README.md`
- `frontend_PRD.md`
- `frontend_PROJECT_STATUS.md`
- `SECOND_PHASE_TASKS.md`
- `THIRD_PHASE_ROADMAP.md`
- `THIRD_PHASE_TASKS.md`
- `TECH_BOTTLENECKS.md`
- `claude_review_package/README_FOR_CODEX.md`
- `claude_review_package/codex_run_card.md`
- `claude_review_package/package_manifest.md`
- `claude_review_package/archive_structure.md`

## 2. Increment（增量与审计）

以下文档用于增量推进、方向审计、文档治理与评审材料：

- `DOCS_DIRECTION_REVIEW.md`
- `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
- `ULTRAREVIEW_REPORT.md`
- `ULTRAREVIEW_REVIEW_SHARP.md`
- `CLAUDE_REVIEW_REPORT.md`
- `PR_COMPLETION_SUMMARY.md`
- `frontend_REVIEW_GUIDE.md`
- `frontend_DELIVERY_CHECKLIST.md`
- `claude_review_package\mainline\README.md`
- `claude_review_package\increment\README.md`

## 3. Experimental（实验探索）

以下内容如果出现，应视为实验层材料，不得直接覆盖主线：

- 临时算法探索
- 未冻结 schema 的方案草稿
- 未通过评估的候选策略
- 一次性分析脚本

## 4. Archive（历史归档）

以下内容建议归档后只读：

- 已被新总纲覆盖的旧评审报告
- 过期交付说明
- 历史阶段性产物
- 已失效的需求口径

## 5. Codex 默认执行规则

1. 先看治理规范
2. 再看运行指令卡
3. 再看主线文档
4. 需要追溯历史时再看归档
5. 新需求默认进入 `Increment`
6. 不能让评审文档反向定义当前主线

## 6. 一句话总结

主线负责“现在怎么做”，增量负责“下一步怎么演化”，归档负责“过去发生了什么”。