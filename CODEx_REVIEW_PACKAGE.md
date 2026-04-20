# Codex 评审提交包说明

## 1. 项目概览

本提交包包含 `alpha-autopilot` 的后端原型、前端工作台原型，以及面向 `novel-fusion-autopilot` 的章节推荐智能核心研究材料。

项目核心路线是：

> 以爆款拆解为先验，以特征矩阵为核心，以状态推演为中枢，以反馈闭环为进化机制。

## 2. 提交目标

本轮提交的目标不是完成最终产品，而是交付一套可审查、可扩展、可复盘的工程原型。

重点验证：

- 特征矩阵能否承载爆款拆解经验
- 状态推演能否驱动章节推荐
- 训练日志与版本管理能否形成闭环
- 前后端文档是否满足工程交付要求

## 3. 提交内容

### 后端原型
- `alpha_autopilot/narrative.py`
- `alpha_autopilot/feature_matrix.py`
- `alpha_autopilot/planner.py`
- `alpha_autopilot/trainer.py`
- `alpha_autopilot/versioning.py`
- `alpha_autopilot/training_log.py`
- `train.py`
- `recommend.py`
- `samples.json`

### 前端原型
- `ui/index.html`
- `ui/styles.css`

### 文档
- `PRD.md`
- `PROJECT_STATUS.md`
- `TECH_BOTTLENECKS.md`
- `frontend_PRD.md`
- `frontend_PROJECT_STATUS.md`
- `frontend_TECH_BOTTLENECKS.md`
- `frontend_REVIEW_GUIDE.md`
- `frontend_DELIVERY_CHECKLIST.md`

## 4. 评审重点

### 后端
- 训练流程是否可追踪
- 版本快照是否可回滚
- 推荐结果是否可解释
- 样本扩展机制是否清晰
- 反馈闭环是否完整

### 前端
- 是否清晰表达模型状态
- 是否保留版本、日志和反馈区
- 是否具备后续接入真实接口的结构空间
- 是否与后端术语保持一致

## 5. 已知限制

- 当前样本量仍偏少
- 推荐动作空间还不够大
- 前端仍是静态原型
- 评估标准尚处于早期收敛阶段

## 6. 后续计划

1. 持续扩充拆解样本
2. 丰富题材与风格标签
3. 加强训练日志字段
4. 细化版本管理
5. 接入真实 API
6. 整合进 `novel-fusion-autopilot`

## 7. 交付结论

本提交包已经满足“可以交给 Codex 评审”的基本要求，具备：

- 结构化工程原型
- 完整文档链路
- 版本与日志机制
- 前后端统一叙事
- 明确的后续迭代方向
