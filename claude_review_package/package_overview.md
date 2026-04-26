# claude_review_package 目录总览

## 1. 这个包的作用

`claude_review_package` 用来把开发治理、文档治理、测试治理和执行治理放进同一个入口，方便 Codex 按统一顺序读文档、判层级、做裁决。

## 2. 核心层级

本包中的文档分为四层，优先级从高到低依次是：

1. `mainline`
2. `increment`
3. `experimental`
4. `archive`

### 2.1 `mainline`

当前默认执行依据。主线文档回答“现在怎么做”，任何冲突都优先看这里。

### 2.2 `increment`

增量与评审材料。它们回答“哪里需要收敛”和“下一步如何演化”，但不能覆盖主线结论。

### 2.3 `experimental`

实验与探索材料。它们只提供候选思路，不是默认口径。

### 2.4 `archive`

历史和失效材料。它们只用于追溯，不参与当前决策。

## 3. 冲突裁决原则

如果不同文档的评审结论冲突，按下面顺序裁决：

1. 先看 `CODEX_DEVELOPMENT_GOVERNANCE.md`。
2. 再看当前问题所属的主线文档。
3. 再看最相关、最明确、最接近最终执行的增量评审文档。
4. 如果仍冲突，以更新后的主线状态文档为准。

也就是说，评审可以提出修正，但不能反向定义主线。

## 4. 你通常先读什么

`package_overview.md` 只是入口说明，完整默认顺序与 `final_document_index.md` 保持一致：

1. `CODEX_DEVELOPMENT_GOVERNANCE.md`
2. `README_FOR_CODEX.md`
3. `codex_run_card.md`
4. `final_document_index.md`
5. `new_requirement_intake_template.md`
6. `new_requirement_execution_flow.md`
7. `test_governance.md`
8. `execution_governance.md`

## 5. 这份总览和另外两份索引的关系

- `package_manifest.md` 是清单视角，强调分类和层级。
- `final_document_index.md` 是执行视角，强调默认阅读顺序和裁决优先级。
- `package_overview.md` 是入口视角，强调这个包为什么存在、先看什么、冲突怎么判。

三份文件必须保持同一套层级定义和同一套冲突裁决原则。
