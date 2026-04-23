# 文档归档分层方案

## 1. 目标

将项目文档按照主次关系分为四层，避免总纲、当前状态、增量执行与历史评审互相混写。

## 2. 分层定义

### 2.1 mainline

用于放置唯一主线依据文档。

建议包含：
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

### 2.2 increment

用于放置 `v3` 增量相关的执行说明、评审与任务补充。

建议包含：
- `DOCS_DIRECTION_DRIFT_AUDIT_DEEP.md`
- `ULTRAREVIEW_REPORT.md`
- `ULTRAREVIEW_REVIEW_SHARP.md`

### 2.3 experimental

用于放置实验性方案、候选设想、临时探索材料。

原则：
- 不得作为主线依据
- 不得直接驱动生产级变更

### 2.4 archive

用于放置历史评审、旧交付、过期口径、已被新总纲覆盖的材料。

原则：
- 只读
- 不再作为 Codex 默认执行输入

## 3. 迁移原则

- 总纲文档留在主线
- 当前状态文档留在主线
- 过期评审和交付材料进入 archive
- 不确定归属的文档先放 increment，不直接进入 archive

## 4. Codex 执行规则

Codex 默认只读取：
1. `mainline`
2. `increment`

只有在需要追溯历史时，才读取 `archive`。

## 5. 一句话总结

把“当前应该执行什么”与“历史发生过什么”彻底分开。