# 最终版文档清单

## 1. 这份清单的定位

这是一份面向执行的索引。它告诉 Codex 哪些文档应视为当前有效口径，以及在文档结论冲突时先读什么、后读什么。

## 2. 层级顺序

从高到低，文档优先级依次为：

1. `mainline`
2. `increment`
3. `experimental`
4. `archive`

同层级内，优先选择更接近最终执行、更新更明确、且能直接回答当前问题的文件。

## 3. 冲突裁决

当不同文档的评审结论不一致时，按以下规则裁决：

1. `CODEX_DEVELOPMENT_GOVERNANCE.md` 永远优先于其他文档。
2. 主线文档优先于增量、实验和归档文档。
3. 增量文档中的评审结论只负责推动收敛，不得覆盖主线结论。
4. 如果多个评审文档彼此冲突，优先采用更接近最终裁决、表述更明确、且直接服务当前事项的那一份。
5. 如果仍无法裁决，以 `CODEX_DEVELOPMENT_GOVERNANCE.md` 加上最新主线状态文档为准。

## 4. Mainline

以下文件是当前默认执行依据：

- `CODEX_DEVELOPMENT_GOVERNANCE.md`
- `MASTER_ROADMAP.md`
- `PROJECT_STATUS.md`
- `README.md`
- `V2/frontend_PRD.md`
- `V2/frontend_PROJECT_STATUS.md`
- `V2/SECOND_PHASE_TASKS.md`
- `THIRD_PHASE_ROADMAP.md`
- `THIRD_PHASE_TASKS.md`
- `V2/TECH_BOTTLENECKS.md`
- `claude_review_package/README_FOR_CODEX.md`
- `claude_review_package/codex_run_card.md`
- `claude_review_package/package_manifest.md`
- `claude_review_package/archive_structure.md`

## 5. Increment

以下文件属于增量、评审、审计与交付收敛材料：

- `DOCS_DIRECTION_REVIEW.md`
- `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
- `ULTRAREVIEW_REPORT.md`
- `ULTRAREVIEW_REVIEW_SHARP.md`
- `V1/CLAUDE_REVIEW_REPORT.md`
- `V1/PR_COMPLETION_SUMMARY.md`
- `V2/frontend_REVIEW_GUIDE.md`
- `V2/frontend_DELIVERY_CHECKLIST.md`
- `claude_review_package/V4/V4_ACCEPTANCE_HANDOFF_2026_04_25.md`
- `claude_review_package/V4/V4_CLAUDE_ACCEPTANCE_REVIEW_TASK_2026_04_25.md`
- `claude_review_package/mainline/README.md`
- `claude_review_package/increment/README.md`

## 6. Experimental

以下内容只在需要探索方案时参考，不能作为默认执行口径：

- 临时算法探索
- 未冻结 schema 的方案草稿
- 未通过评估的候选策略
- 一次性分析脚本

## 7. Archive

以下内容只用于追溯和审计，不参与当前裁决：

- 被新主线覆盖的旧评审报告
- 过期交付说明
- 历史阶段性产物
- 已失效的需求口径

## 8. 默认阅读顺序

Codex 默认按以下顺序阅读：

1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `README_FOR_CODEX.md`
3. `codex_run_card.md`
4. `final_document_index.md`
5. `new_requirement_intake_template.md`
6. `new_requirement_execution_flow.md`
7. `test_governance.md`
8. `execution_governance.md`

## 9. 一句话规则

主线回答“现在怎么做”，增量回答“如何收敛”，实验回答“能不能试”，归档回答“以前发生了什么”。
