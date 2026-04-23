# 给 Codex 的执行说明

本工程包是 `alpha-autopilot` 后续开发的唯一治理入口之一。Codex 执行前必须先确认：

## 阅读顺序

1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `claude_review_package\README.md`
3. `claude_review_package\SHORT_NAV.md`
4. `claude_review_package\START_HERE.md`
5. `claude_review_package\FINAL_FILE_TREE.md`
6. `claude_review_package\package_manifest.md`
7. `claude_review_package\archive_structure.md`
8. `claude_review_package\codex_run_card.md`
9. `claude_review_package\final_document_index.md`
10. `claude_review_package\package_overview.md`
11. `claude_review_package\codex_final_startup_prompt.md`
12. `claude_review_package\codex_short_command_card.md`
13. `claude_review_package\task_launch_template.md`
14. `claude_review_package\new_requirement_document_update_rules.md`
15. `claude_review_package\test_governance.md`
16. `claude_review_package\execution_governance.md`
17. `claude_review_package\new_requirement_intake_template.md`
18. `claude_review_package\new_requirement_execution_flow.md`
19. `MASTER_ROADMAP.md`
20. `PROJECT_STATUS.md`
21. `THIRD_PHASE_ROADMAP.md`
22. `SECOND_PHASE_TASKS.md`
23. `THIRD_PHASE_TASKS.md`
24. `frontend_PRD.md`
25. `frontend_PROJECT_STATUS.md`
26. `TECH_BOTTLENECKS.md`
27. `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`

## 变更原则

- 先判断变更属于 Baseline、Increment 还是 Experimental
- 只做单一目标，不跨层级扩张
- 任何新功能默认进入 Increment
- 实验性内容不得影响主线默认行为
- 改完必须同步状态文档

## 口径原则

- `v1/v2` = Baseline，稳定收口
- `v3` = Increment，质量层与推荐增强层
- Experimental = 独立探索
- `Dashboard` = Baseline 展示层
- `V2 Workbench` = Increment 决策层

## 归档原则

- `mainline` 只放主线依据文档
- `increment` 只放增量与审计材料
- `experimental` 只放探索材料
- `archive` 只放历史和过期材料

## 重要提醒

如果遇到文档冲突，以治理规范和总路线图为准，不要用局部文档改写主线定义。