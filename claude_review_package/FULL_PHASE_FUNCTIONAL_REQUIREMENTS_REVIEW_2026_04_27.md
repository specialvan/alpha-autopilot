# 全阶段功能需求全量评审（2026-04-27）

## 1. 评审目标

对 `alpha-autopilot` 的全阶段功能需求文档进行一次面向交付的全量评审，覆盖：

- Baseline：`v1/v2`
- Increment：`v3`
- 增量后续：`v4` 生产化推进

目标是确认：需求口径、阶段边界、验收门禁、当前执行状态是否一致，并给出可执行的修复清单与 Claude 复审入口。

---

## 2. 评审输入（本次实际读取）

1. `MASTER_ROADMAP.md`
2. `PRD.md`
3. `PROJECT_STATUS.md`
4. `V4_PRODUCTION_CYCLE_TASK_BOARD.md`
5. `THIRD_PHASE_ROADMAP.md`
6. `THIRD_PHASE_TASKS.md`
7. `V3_PHASE_CLOSEOUT_2026_04_24.md`
8. `V2/SECOND_PHASE_TASKS.md`
9. `V2/frontend_PRD.md`
10. `V2/frontend_PROJECT_STATUS.md`
11. `PHASE3_SCOPE_ALIGNMENT_2026_04_24.md`
12. `V4_REQUIREMENT_SUMMARY_AND_SCOPE.md`
13. `claude_review_package/V4/V4_REQUIREMENT_SUMMARY_AND_SCOPE.md`

---

## 3. 评审结论

**结论：有条件通过（需先修复 P1 阻断项）。**

当前代码与执行证据显示 `V4` 已进入生产周期推进（`T01`~`T04` 已验收，`T05` 待执行），但顶层需求主文档仍停留在 `v1/v2/v3` 三阶段口径，且存在同名需求文档双版本分叉，已影响“全阶段需求评审”的唯一口径与可审计性。

---

## 4. 阻断项（P1）

### P1-1 顶层需求主文档未纳入 V4 阶段，和当前执行状态冲突

- 证据：
  - `MASTER_ROADMAP.md:10` 仍定义 Increment 仅为 `v3`
  - `MASTER_ROADMAP.md:13-17` 仍定义项目仅三阶段（到第三阶段）
  - `PRD.md:92-102` 仍是 `v1 / v2 / v3` 并行策略
  - `PROJECT_STATUS.md:7-10` 明确当前已进入 `V4` 生产级推进且任务推进到 `T04 -> T05`
  - `V4_PRODUCTION_CYCLE_TASK_BOARD.md:12-17,26-27` 明确 `T04` 已验收、`T05` 待执行
- 影响：
  - 全阶段评审时会出现“主路标无 V4、执行已在 V4”的裁决冲突。
  - 新需求归属与验收门禁可能被误判，影响发布与回滚决策。
- 处置要求：
  - 将 `MASTER_ROADMAP.md` 与 `PRD.md` 升级为包含 V4 的权威口径（至少补“第四阶段或第三阶段后续增量 V4”章节）。
  - 在同一次提交中同步 `PROJECT_STATUS.md` 的引用关系，避免再次漂移。

### P1-2 同名 V4 需求文档存在双版本分叉（门禁条款文本不一致）

- 证据：
  - `V4_REQUIREMENT_SUMMARY_AND_SCOPE.md:178` 标题为“生产级工程产品硬门禁”
  - `claude_review_package/V4/V4_REQUIREMENT_SUMMARY_AND_SCOPE.md:178` 标题为“首发生产级可验收口径（修订版）”
  - 两份文档在第 10 节内容结构不同（根文档为 6 大硬门禁分组，评审包文档为 8 条验收口径）
- 影响：
  - Claude 评审时若读取不同路径，会得到不同验收基线。
  - 容易导致“通过/不通过”标准不一致，破坏审计可追溯性。
- 处置要求：
  - 选定唯一权威版本（建议 `claude_review_package/V4/...` 作为评审入口，root 文档为镜像或重定向）。
  - 增加“同名文档一致性检查”到评审脚本或发布前检查项。

---

## 5. 非阻断风险（P2 / P3）

### P2-1 第三阶段路线图同文档混合“进行中目标”和“已收尾状态”

- 证据：
  - `THIRD_PHASE_ROADMAP.md:50-65` 仍描述“当前阶段目标”
  - `THIRD_PHASE_ROADMAP.md:143-147` 同时声明“收尾结论 + 进入维护窗口”
  - `V3_PHASE_CLOSEOUT_2026_04_24.md:5,66-68` 已明确 V3 收口并限制范围外需求
- 影响：
  - 读者难以判断 V3 是“正在建设”还是“维护窗口”。
  - 可能引发重复开发或错误排期。
- 建议：
  - 将 `THIRD_PHASE_ROADMAP.md` 改为“历史收尾视图”，把“当前阶段目标”迁移到归档或标注为“已完成/转后续”。

### P2-2 前端阶段状态文档测试证据过旧

- 证据：
  - `V2/frontend_PROJECT_STATUS.md:31` 仍记录 `npm test -> 7 tests passed`
  - `PROJECT_STATUS.md:65` 已记录 `npm test -> 16 passed`
- 影响：
  - 全阶段评审时前端质量门禁口径不一致。
- 建议：
  - 统一前端测试口径（命令、测试数、日期）并回填最近一次稳定结果。

### P3-1 多份阶段文档职责边界清晰，但缺少“全阶段总览索引”

- 现状：
  - 文档足够多，但全阶段评审入口仍需人工拼接。
- 建议：
  - 增加 `FULL_PHASE_REQUIREMENTS_INDEX.md`，固定“读什么、按什么顺序读、冲突如何裁决”。

---

## 6. 全阶段覆盖判定（简表）

| 阶段 | 需求定义完整性 | 代码/测试证据 | 文档一致性 | 判定 |
| --- | --- | --- | --- | --- |
| V1 | 高 | 高 | 中 | 通过 |
| V2 | 高 | 高 | 中 | 通过（需状态文档对齐） |
| V3 | 高 | 高 | 中 | 通过（维护窗口） |
| V4 | 中高 | 高（T01-T04 已验收） | 低（存在双版本分叉） | 有条件通过 |

---

## 7. 修复优先级（建议按此顺序执行）

1. 修复 P1-1：更新 `MASTER_ROADMAP.md`、`PRD.md` 的全阶段口径（纳入 V4）。
2. 修复 P1-2：统一两份 `V4_REQUIREMENT_SUMMARY_AND_SCOPE.md` 为单一权威版本。
3. 修复 P2-1：清理 `THIRD_PHASE_ROADMAP.md` 的时态冲突。
4. 修复 P2-2：更新前端状态文档测试证据。

---

## 8. 提交给 Claude 的复审任务单

### 8.1 复审目标

请基于本文件与修复后的文档，对“全阶段功能需求一致性”进行复审，确认：

1. 顶层路线图是否已完整覆盖 `v1/v2/v3/v4`；
2. 全阶段验收门禁是否唯一且可执行；
3. 评审包与仓库主文档是否不存在同名分叉；
4. 需求、实现、测试、状态四者是否可相互追溯。

### 8.2 建议必跑命令

1. `python scripts/run_layered_tests.py`
2. `python scripts/run_v4_production_cycle.py T04`
3. `pytest tests/test_run_v4_production_cycle.py -q`
4. `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q`
5. `npm --prefix ui-react run test`
6. `npm --prefix ui-react run build`

### 8.3 复审输出格式

1. 结论：`通过 / 有条件通过 / 不通过`
2. 阻断项（P1）：文件 + 行号 + 证据
3. 非阻断项（P2/P3）：影响 + 建议
4. 命令执行记录与结果摘要
5. 是否允许进入下一生产任务（`T05`）

---

## 9. 一句话结论

当前仓库“实现与测试”已进入 V4 生产节奏，但“全阶段需求主文档”仍存在阶段缺口与同名分叉；先收敛文档口径，再做 Claude 复审，才能形成可审计的全阶段通过结论。
