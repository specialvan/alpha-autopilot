# novel-fusion-autopilot 集成目录树 + 模块职责说明

> 目标：将 `alpha-autopilot` 的小说章节推荐原型，以最小耦合方式接入 `novel-fusion-autopilot`，形成可扩展、可评审、可迭代的章节智能推荐子系统。

## 1. 集成原则

1. **先契约，后实现**
   - 先冻结数据结构和接口边界，再实现内部逻辑。

2. **先适配，后融合**
   - 保留 `alpha-autopilot` 作为独立研究原型，`novel-fusion-autopilot` 作为主工程容器。

3. **先闭环，后扩展**
   - 优先打通“输入 -> 推演 -> 推荐 -> 反馈 -> 更新”的最小闭环。

4. **先可解释，后智能化**
   - 优先保留特征矩阵和权重解释能力，避免黑盒化过早侵入。

---

## 2. 建议集成目录树

```text
novel-fusion-autopilot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── recommendation.py
│   │   │   │   ├── training.py
│   │   │   │   └── feedback.py
│   │   │   ├── schemas/
│   │   │   │   ├── story.py
│   │   │   │   ├── recommendation.py
│   │   │   │   ├── training.py
│   │   │   │   └── feedback.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── services/
│   │   │   ├── narrative/
│   │   │   │   ├── state_builder.py
│   │   │   │   ├── feature_matrix.py
│   │   │   │   ├── planner.py
│   │   │   │   ├── trainer.py
│   │   │   │   ├── feedback.py
│   │   │   │   └── versioning.py
│   │   │   ├── storage/
│   │   │   └── telemetry/
│   │   ├── db/
│   │   └── domain/
│   │       ├── story.py
│   │       ├── recommendation.py
│   │       └── training.py
│   └── tests/
│       ├── test_dashboard_api.py
│       ├── test_recommendation_api.py
│       ├── test_narrative_planner.py
│       ├── test_training_pipeline.py
│       └── test_feedback_loop.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── dashboard.ts
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── types/
│   │   └── utils/
│   └── public/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── research/
│   └── delivery/
└── artifacts/
    ├── matrix_snapshots/
    ├── training_logs/
    └── sample_sets/
```

---

## 3. 模块职责说明

### 3.1 `backend/app/api/routes/dashboard.py`

#### 职责
- 提供前端仪表盘的统一数据入口。
- 聚合叙事状态、推荐结果、训练日志、版本信息。

#### 典型接口
- `GET /api/dashboard`

#### 输出内容
- 当前矩阵版本
- 样本数量
- 反馈命中率
- 叙事状态摘要
- 推荐结果 Top-K
- 最近训练日志

---

### 3.2 `backend/app/api/routes/recommendation.py`

#### 职责
- 提供章节推荐能力。
- 输入当前故事状态，输出候选推进策略。

#### 典型接口
- `POST /api/recommendation`

#### 输入
- `StoryState`
- 风格标签
- 题材标签
- 平台约束

#### 输出
- 推荐动作
- 推荐分数
- 解释说明
- 状态增量建议

---

### 3.3 `backend/app/api/routes/training.py`

#### 职责
- 接收拆解样本。
- 启动训练任务。
- 返回训练结果与版本信息。

#### 典型接口
- `POST /api/training`
- `GET /api/training/{version}`

#### 输出
- 训练完成状态
- 权重快照
- 样本计数
- 版本号

---

### 3.4 `backend/app/api/routes/feedback.py`

#### 职责
- 接收人工反馈或结果反馈。
- 驱动特征矩阵增量更新。

#### 典型接口
- `POST /api/feedback`

#### 输入
- 推荐结果 ID
- 采纳情况
- 质量评分
- 文本复盘意见

#### 输出
- 更新是否成功
- 新版本号（如触发版本化）

---

### 3.5 `backend/app/services/narrative/state_builder.py`

#### 职责
- 将文本、摘要、角色卡、世界观卡等输入，构建结构化叙事状态。

#### 输入来源
- 章节摘要
- 历史上下文
- 角色设定
- 风格标签

#### 输出
- `StoryState`

---

### 3.6 `backend/app/services/narrative/feature_matrix.py`

#### 职责
- 保存特征矩阵权重。
- 负责评分和反馈更新。

#### 核心能力
- 候选特征打分
- 权重更新
- 版本快照生成

---

### 3.7 `backend/app/services/narrative/planner.py`

#### 职责
- 根据故事状态生成候选章节推进策略。
- 对候选方案做排序。

#### 输出
- Top-K 推荐方案
- 每个方案的特征明细和解释

---

### 3.8 `backend/app/services/narrative/trainer.py`

#### 职责
- 使用拆解样本训练初始矩阵。
- 维护训练历史。

#### 输入
- 爆款拆解样本集

#### 输出
- 训练后的矩阵
- 训练日志
- 版本快照信息

---

### 3.9 `backend/app/services/narrative/feedback.py`

#### 职责
- 将推荐结果与真实效果做对照。
- 将偏差写回训练循环。

#### 关键点
- 人工反馈优先
- 自动反馈作为辅助
- 反馈须可审计

---

### 3.10 `backend/app/services/narrative/versioning.py`

#### 职责
- 管理矩阵版本。
- 生成可回滚快照。
- 保存训练轮次信息。

#### 关键数据
- 版本号
- 创建时间
- 样本数
- 权重摘要
- 备注

---

### 3.11 `backend/app/services/storage/`

#### 职责
- 存储样本集、训练日志、版本快照、反馈记录。
- 为后续数据库或对象存储提供抽象层。

---

### 3.12 `backend/app/services/telemetry/`

#### 职责
- 提供训练与推荐过程的可观测性。
- 记录耗时、错误、命中率、权重变化趋势。

---

## 4. 前端对应职责

### 4.1 `frontend/src/api/dashboard.ts`
- 对接 `/api/dashboard`
- 统一前端数据模型
- 支持本地回退数据

### 4.2 `frontend/src/components/`
- 仪表盘组件化展示
- 分区显示状态、矩阵、推荐、日志、反馈

### 4.3 `frontend/src/stores/`
- 管理当前章节、版本、筛选条件、推荐结果

### 4.4 `frontend/src/types/`
- 冻结前后端共享数据结构

---

## 5. 推荐的接入顺序

### 阶段 1 冻结契约
- 先冻结 `StoryState`、`RecommendationResult`、`MatrixSnapshot` 等结构

### 阶段 2 建服务骨架
- 在 `novel-fusion-autopilot` 中建立 narrative 服务目录

### 阶段 3 接仪表盘 API
- 先让前端可读后端汇总数据

### 阶段 4 接推荐与训练
- 再打通推荐和训练接口

### 阶段 5 接反馈闭环
- 最后接入人工复盘和自动反馈

---

## 6. 交付标准

如果该目录树与职责拆分被采用，则说明 `novel-fusion-autopilot` 已具备以下条件：

- 可承接 `alpha-autopilot` 的研究结果
- 可逐步替换为正式实现
- 可同时支持前端展示与后台训练
- 可形成持续迭代的章节智能推荐子系统

---

## 7. 备注

本目录树为建议结构，实际落地时可结合 `novel-fusion-autopilot` 现有目录命名规则做轻微调整，但应尽量保持接口语义不变。
