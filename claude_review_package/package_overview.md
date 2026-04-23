# claude_review_package 目录总览

## 1. 这个包是做什么的

这个包的作用是把 `alpha-autopilot` 的开发治理、文档治理、测试治理、执行治理和新需求接入流程统一起来，方便 Codex 按一致规则推进后续开发。

## 2. 文件分层总览

### 2.1 治理与执行入口

#### `README.md`
包的总体说明，解释这个工程包为什么存在。

#### `README_FOR_CODEX.md`
给 Codex 的阅读顺序和执行提醒。

#### `codex_run_card.md`
Codex 的运行指令卡，告诉它每次开发前后应该做什么。

#### `package_manifest.md`
工程包清单，快速识别各层文件。

#### `archive_structure.md`
说明 mainline / increment / experimental / archive 的归档分层。

#### `final_document_index.md`
最终版文档清单，告诉你哪些文档属于主线、增量、实验或归档。

---

### 2.2 主线治理

#### `CODEX_DEVELOPMENT_GOVERNANCE.md`
最高层治理规范，定义 Baseline / Increment / Experimental 的开发边界。

#### `mainline/README.md`
主线文档索引，列出当前默认优先读取的主线依据。

#### `MASTER_ROADMAP.md`
项目总路线图，定义阶段目标和总体方向。

#### `PROJECT_STATUS.md`
项目真实进度状态，记录当前完成度和风险。

#### `README.md`
项目根目录总入口说明，作为主线背景与治理入口之一。

#### `frontend_PRD.md`
前端需求说明，定义 Dashboard / V2 Workbench 的前端边界。

#### `frontend_PROJECT_STATUS.md`
前端项目状态，记录前端真实进度。

#### `SECOND_PHASE_TASKS.md`
第二阶段任务拆解，属于 Baseline 稳定化收口过程。

#### `THIRD_PHASE_ROADMAP.md`
第三阶段路线图，属于 Increment 的质量层与价值进化接入路线。

#### `THIRD_PHASE_TASKS.md`
第三阶段任务清单，定义 v3 增量任务。

#### `TECH_BOTTLENECKS.md`
技术瓶颈与复盘，记录当前限制和改进方向。

---

### 2.3 增量与审计

#### `increment/README.md`
增量文档索引，告诉 Codex 哪些内容属于增量与审计材料。

#### `DOCS_DIRECTION_REVIEW.md`
文档方向一致性评审，确认是否存在方向漂移。

#### `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
更严格的方向漂移深审计，专门找口径漂移和阶段边界风险。

#### `ULTRAREVIEW_REPORT.md`
综合评审报告，偏总结性。

#### `ULTRAREVIEW_REVIEW_SHARP.md`
更尖锐的评审版本，偏 PR review 口吻。

#### `CLAUDE_REVIEW_REPORT.md`
历史评审报告，属于可追溯材料。

#### `PR_COMPLETION_SUMMARY.md`
旧交付或完成总结，偏历史记录。

#### `frontend_REVIEW_GUIDE.md`
前端评审说明，指导如何检查前端工作台。

#### `frontend_DELIVERY_CHECKLIST.md`
前端交付清单，记录交付文件和层级口径。

---

### 2.4 测试与执行治理

#### `test_governance.md`
测试治理说明，定义单元、集成、回归和验收测试。

#### `execution_governance.md`
执行治理说明，定义任务顺序、层级判断、完成标准和回滚处理。

#### `new_requirement_intake_template.md`
新增需求接入模板，用来判断一个需求属于哪一层、影响哪些部分。

#### `new_requirement_execution_flow.md`
新需求接入到执行的一页式流程，用来指导从提需求到收口的步骤。

#### `FAQ.md`
常见问题说明，回答治理包怎么用、什么时候重收敛、什么时候归档等。

---

### 2.5 文档运行辅助

#### `package_overview.md`
你正在看的这份目录总览，方便一次性理解整个包。

---

## 3. 谁应该读哪些文件

### Codex 默认先读
1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `README_FOR_CODEX.md`
3. `codex_run_card.md`
4. `final_document_index.md`
5. `new_requirement_intake_template.md`
6. `new_requirement_execution_flow.md`
7. `test_governance.md`
8. `execution_governance.md`

### 做主线开发时重点读
- `MASTER_ROADMAP.md`
- `PROJECT_STATUS.md`
- `README.md`
- `frontend_PRD.md`
- `frontend_PROJECT_STATUS.md`
- `SECOND_PHASE_TASKS.md`
- `THIRD_PHASE_ROADMAP.md`
- `THIRD_PHASE_TASKS.md`
- `TECH_BOTTLENECKS.md`

### 做审计或回看历史时再读
- `DOCS_DIRECTION_REVIEW.md`
- `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
- `ULTRAREVIEW_REPORT.md`
- `ULTRAREVIEW_REVIEW_SHARP.md`
- `CLAUDE_REVIEW_REPORT.md`
- `PR_COMPLETION_SUMMARY.md`

## 4. 一句话总结

这个包的核心作用是：把项目怎么做、怎么改、怎么测、怎么收口统一成一套能长期执行的规则。