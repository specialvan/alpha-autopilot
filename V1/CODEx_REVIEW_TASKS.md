# Codex 评审任务单

## 任务名称

评审 `alpha-autopilot` 小说章节智能推荐引擎原型的工程交付完整性与可扩展性。

## 评审目标

确认该项目是否满足以下目标：

1. 可作为小说章节推荐引擎的研究原型
2. 可形成后续迁移到 `novel-fusion-autopilot` 的中间层
3. 可被 Codex 复核其代码结构、文档结构与工程边界
4. 可支撑后续样本扩展、版本管理、训练日志积累

## 评审范围

### 后端
- `alpha_autopilot/narrative.py`
- `alpha_autopilot/feature_matrix.py`
- `alpha_autopilot/planner.py`
- `alpha_autopilot/trainer.py`
- `alpha_autopilot/versioning.py`
- `alpha_autopilot/training_log.py`
- `train.py`
- `recommend.py`
- `samples.json`

### 前端
- `ui/index.html`
- `ui/styles.css`

### 文档
- `PRD.md`
- `PROJECT_STATUS.md`
- `V2/TECH_BOTTLENECKS.md`
- `V2/frontend_PRD.md`
- `V2/frontend_PROJECT_STATUS.md`
- `V2/frontend_TECH_BOTTLENECKS.md`
- `V2/frontend_REVIEW_GUIDE.md`
- `V2/frontend_DELIVERY_CHECKLIST.md`
- `V1/CODEx_REVIEW_PACKAGE.md`
- `V1/DELIVERY_TREE.md`

## 核心检查项

### 1. 架构合理性
- 状态层、特征层、推演层、反馈层是否分离清晰
- 前后端文档和代码是否口径一致

### 2. 可追踪性
- 训练日志是否可追踪
- 版本快照是否可回溯
- 样本变更是否可记录

### 3. 可解释性
- 推荐结果是否有评分与解释
- 特征矩阵是否便于人工理解

### 4. 可扩展性
- 是否能继续加入题材标签
- 是否能继续扩大候选动作
- 是否能接入真实 API

### 5. 工程交付完整性
- 文档是否齐全
- 目录树是否明确
- 是否已经形成可交付的评审包

## 评审建议输出

Codex 评审后建议输出：

- 通过 / 有条件通过 / 不通过
- 需要修复的结构问题
- 推荐的下一轮迭代项
- 是否适合整合进 `novel-fusion-autopilot`
