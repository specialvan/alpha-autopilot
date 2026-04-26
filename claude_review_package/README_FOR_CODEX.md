# 给 Codex 的执行说明

本工程包是 `alpha_autopilot` 后续开发的唯一治理入口之一。Codex 执行前必须先确认：

## 唯一优先级来源

- 详细执行顺序只在本文件定义。
- `codex_run_card.md` 和 `codex_short_command_card.md` 只做引用，不新增、不覆盖、不分叉执行顺序。
- 如与其他文档冲突，以本文件和 `CODEX_DEVELOPMENT_GOVERNANCE.md` 为准。

## 目录化阶段文档

- `claude_review_package/V3/`：V3 相关文档
- `claude_review_package/V4/`：V4 相关文档

每个目录只放本阶段文档，避免阶段混用。

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
19. `claude_review_package\CODEx_REVIEW_DEV_TASK.md`
20. `claude_review_package\CODEx_V3_REVIEW_INSTRUCTIONS.md`
21. `claude_review_package\V3\V3_READER_RETENTION_DEV_SPEC.md`
22. `claude_review_package\V3\V3_READER_RETENTION_INTERFACE_DESIGN.md`
23. `claude_review_package\V3\V3_RETENTION_IMPLEMENTATION_TEST_PLAN.md`
24. `claude_review_package\V3\V3_READER_RETENTION_CODE_MODULE_PLAN.md`
25. `claude_review_package\V4\V4_REQUIREMENT_SUMMARY_AND_SCOPE.md`
26. `claude_review_package\V4\V4_RELATIONSHIP_GENERATION_SPEC.md`
27. `claude_review_package\V4\V4_INTERFACE_DESIGN.md`
28. `claude_review_package\V4\V4_CODE_MODULE_PLAN.md`
29. `claude_review_package\V4\V4_REVIEW_DEV_TASK.md`
30. `claude_review_package\V4\V4_RETENTION_IMPLEMENTATION_TEST_PLAN.md`
31. `claude_review_package\V4\V4_ACCEPTANCE_HANDOFF_2026_04_25.md`
32. `claude_review_package\V4\V4_CLAUDE_ACCEPTANCE_REVIEW_TASK_2026_04_25.md`
33. `claude_review_package\REVIEW_EVIDENCE_RESPONSE.md`
34. `MASTER_ROADMAP.md`
35. `PROJECT_STATUS.md`
36. `THIRD_PHASE_ROADMAP.md`
37. `V2/SECOND_PHASE_TASKS.md`
38. `THIRD_PHASE_TASKS.md`
39. `V2/frontend_PRD.md`
40. `V2/frontend_PROJECT_STATUS.md`
41. `V2/TECH_BOTTLENECKS.md`
42. `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`

## 变更原则

- 先判断变更属于 Baseline、Increment 还是 Experimental
- 只做单一目标，不跨层级扩张
- 任何新功能默认进入 Increment
- 实验性内容不得影响主线默认行为
- 改完必须同步状态文档

## 口径原则

- `v1/v2` = Baseline，稳定收口
- `v3` = Increment，留存目标函数与生成控制层
- `v4` = Increment，人物关系与性格驱动剧情生成
- Experimental = 独立探索
- `Dashboard` = Baseline 展示层
- `V2 Workbench` = Increment 决策层

## 归档原则

- `mainline` 只放主线依据文档
- `increment` 只放增量与审计材料
- `experimental` 只放探索材料
- `archive` 只放历史和过期材料

## 执行顺序

1. 先读 `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. 再读本文件
3. 再读 `package_manifest.md`
4. 判定任务属于 `Baseline`、`Increment` 还是 `Experimental`
5. 锁定单一目标，默认不跨层级扩张
6. 按任务类型执行，默认只动对应层级内容
7. 完成后更新对应状态文档，必要时补充风险或归档说明

## 重要提醒

如果遇到文档冲突，以治理规范和总路线图为准，不要用局部文档改写主线定义。
