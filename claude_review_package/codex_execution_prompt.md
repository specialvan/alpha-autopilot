# Codex 执行提示（历史简版）

本文件仅作为执行入口的简版说明和历史记录。若与 `codex_final_startup_prompt.md` 存在任何冲突，以 `codex_final_startup_prompt.md` 为准。

## 规则顺序

1. `v1/v2` 为 Baseline，只做收口和维护。
2. `v3` 为 Increment，所有新功能优先进入这里。
3. Experimental 必须隔离，不得污染主线。
4. 每次只处理一个清晰目标。
5. 变更后必须同步更新相关状态文档。

## 执行顺序

1. 先读 `CODEX_DEVELOPMENT_GOVERNANCE.md`、`README_FOR_CODEX.md`、`codex_run_card.md`、`final_document_index.md`、`package_overview.md`、`new_requirement_intake_template.md`、`new_requirement_execution_flow.md`、`test_governance.md`、`execution_governance.md`、`MASTER_ROADMAP.md`、`PROJECT_STATUS.md`。
2. 先填写 `new_requirement_intake_template.md`，再看 `new_requirement_execution_flow.md`。
3. 判定需求属于 Baseline / Increment / Experimental。
4. 确认是否进入开发，若进入则只做最小改动。
5. 补测、更新文档、验证可回滚、收口。

## 变更原则

- 不改变主线边界时，只做局部更新。
- 改变主线边界时，重写相关治理文档。
- 仅做实验探索时，隔离到 Experimental。
- 历史材料只归档，不直接拿来定义当前路线。

## 输出要求

执行结束后，说明以下内容：

- 修改了哪些文档。
- 解决了什么入口或路径问题。
- 还有哪些未完成的治理项。
- 下一步应该推进什么。
