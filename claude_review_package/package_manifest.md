# 工程包清单

## 1. 用途

本清单用于快速识别 `alpha-autopilot` 文档包中的各类文件，并统一它们在决策中的层级与优先级。它不是历史记录，也不是评审记录；它的作用是给 Codex 一个稳定、可执行的读取顺序。更细的执行顺序见 `final_document_index.md`，入口说明见 `package_overview.md`。

## 2. 文档层级

文档按以下顺序分层，层级越靠前，裁决优先级越高：

1. `mainline`
2. `increment`
3. `experimental`
4. `archive`

### 2.1 `mainline`

主线文档，代表当前应执行的正式口径、治理规则、阶段目标和状态。出现与其他层级冲突时，`mainline` 优先。

本包中下列文件也按主线口径读取：

- `README_FOR_CODEX.md`
- `codex_run_card.md`
- `package_manifest.md`
- `final_document_index.md`
- `package_overview.md`
- `archive_structure.md`

### 2.2 `increment`

增量文档，包含评审、审计、收敛建议、交付总结和方向性校准材料。它们用于推动主线收敛，但不能反向覆盖主线结论。

### 2.3 `experimental`

实验文档，只能作为探索材料使用，不能作为默认执行依据，也不能覆盖主线或增量中的正式结论。

### 2.4 `archive`

归档文档，仅供追溯和审计，不参与默认决策。

## 3. 裁决规则

当文档结论冲突时，按以下顺序裁决：

1. 先看 `CODEX_DEVELOPMENT_GOVERNANCE.md`，它定义总规则。
2. 再看 `mainline` 中与当前事项最直接相关的文件。
3. 再看 `increment` 中最新且最接近当前事项的收敛性文档。
4. `experimental` 只能补充思路，不能推翻前述结论。
5. `archive` 只用于追溯，不能参与当前裁决。

如果两份同层级文档冲突：

1. 以更明确、更接近最终执行的文档为准。
2. 以更新、更完整、且明确指向最终口径的文档为准。
3. 仍无法裁决时，回到 `CODEX_DEVELOPMENT_GOVERNANCE.md` 和当前主线状态文档。

## 4. 当前清单

### 4.1 `mainline`

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
- `claude_review_package/final_document_index.md`
- `claude_review_package/package_overview.md`
- `claude_review_package/archive_structure.md`

### 4.2 `increment`

- `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
- `ULTRAREVIEW_REPORT.md`
- `ULTRAREVIEW_REVIEW_SHARP.md`
- `claude_review_package/V4/V4_ACCEPTANCE_HANDOFF_2026_04_25.md`
- `claude_review_package/V4/V4_CLAUDE_ACCEPTANCE_REVIEW_TASK_2026_04_25.md`
- `archive_structure.md`

### 4.3 `experimental`

- 暂无默认实验文档。

### 4.4 `archive`

- 历史评审
- 旧交付
- 过期口径
- 已被更高优先级文档覆盖的材料

## 5. 使用说明

1. 新增文档先判断层级，再进入清单。
2. 评审材料默认进入 `increment`，除非它已经失效或只剩追溯价值。
3. 任何试验性内容都不应写成默认执行口径。
4. 如果一份文档与多个层级都有关，按最高优先级的层级归类。
