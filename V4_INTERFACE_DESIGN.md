# V4 人物关系与性格驱动剧情生成接口设计

## 1. 设计目标

V4 的接口设计目标是把“剧情如何自然长出来”拆成三个可计算输入：

- 人物关系
- 人物性格
- 外部压力

并输出两个核心结果：

- 剧情候选列表
- 可解释的桥段与留存建议

同时必须和 `V3` 的留存目标函数与生成控制层联动。

## 2. 顶层模块划分

建议新增 V4 模块：

- `alpha_autopilot_v4/relations/`
- `alpha_autopilot_v4/personality/`
- `alpha_autopilot_v4/pressure/`
- `alpha_autopilot_v4/plot_generation/`
- `alpha_autopilot_v4/integration/`

## 3. 核心对象设计

### 3.1 人物关系对象

#### `RelationshipProfile`

描述两个或多个角色之间的关系差值与冲突边界。

建议字段：

- `source_character`
- `target_character`
- `status_gap`：地位差
- `info_gap`：信息差
- `emotion_gap`：情感差
- `interest_conflict`
- `control_dependency`
- `trust_state`
- `betrayal_risk`
- `relationship_velocity`
- `tension_score`

#### 作用

- 表达关系是否静止
- 表达关系是否具备剧情生长空间
- 表达这段关系最可能出现的冲突形式

### 3.2 人物性格对象

#### `PersonalityProfile`

描述角色在压力下的动作偏好。

建议字段：

- `character_id`
- `impulsiveness`
- `calmness`
- `resilience`
- `directness`
- `pragmatism`
- `idealism`
- `assertiveness`
- `avoidance`
- `self_protection`
- `sacrifice_tendency`
- `risk_appetite`
- `conflict_style`
- `decision_bias`

#### 作用

- 推导同一事件下不同角色会做出什么不同选择
- 避免人物性格漂移
- 支持压力下的行为预测

### 3.3 外部压力对象

#### `PressureProfile`

描述当前剧情环境中的外部压力源。

建议字段：

- `pressure_type`
- `intensity`
- `time_limit`
- `resource_scarcity`
- `threat_level`
- `humiliation_level`
- `competition_level`
- `survival_pressure`
- `relationship_break_pressure`
- `pressure_direction`

#### 作用

- 推动人物必须做出动作
- 放大冲突
- 提高剧情爆发概率

### 3.4 剧情候选对象

#### `PlotCandidate`

描述一个从人物关系、性格和压力推导出来的剧情走向。

建议字段：

- `candidate_id`
- `triggering_relationships`
- `triggering_personalities`
- `triggering_pressures`
- `predicted_action`
- `predicted_turning_point`
- `predicted_conflict_type`
- `predicted_payoff_type`
- `retention_score`
- `tension_score`
- `explanation`
- `risk_flags`

### 3.5 剧情推导结果对象

#### `PlotGenerationResult`

输出整个推导流程的结果。

建议字段：

- `source_context`
- `relationship_profiles`
- `personality_profiles`
- `pressure_profile`
- `plot_candidates`
- `selected_candidate`
- `selection_reason`
- `v3_retention_context`
- `generation_notes`

## 4. 核心接口设计

### 4.1 关系分析接口

#### `analyze_relationships()`

输入：

- 角色集合
- 角色关系上下文
- 当前剧情阶段

输出：

- `RelationshipProfile[]`

职责：

- 计算地位差 / 信息差 / 情感差
- 识别关系位移空间
- 输出冲突边界

### 4.2 性格分析接口

#### `analyze_personalities()`

输入：

- 角色集合
- 角色性格基础数据
- 当前压力上下文

输出：

- `PersonalityProfile[]`

职责：

- 识别角色的压力下选择偏好
- 识别是否存在性格漂移风险
- 输出动作决策倾向

### 4.3 压力分析接口

#### `analyze_pressure()`

输入：

- 剧情上下文
- 当前事件
- 外部威胁 / 时间 / 资源 / 关系状态

输出：

- `PressureProfile`

职责：

- 识别当前压力类型
- 评估压力强度
- 提供剧情发动机信号

### 4.4 剧情推导接口

#### `generate_plot_candidates()`

输入：

- `RelationshipProfile[]`
- `PersonalityProfile[]`
- `PressureProfile`
- `V3` 留存上下文

输出：

- `PlotCandidate[]`

职责：

- 根据关系差生成冲突候选
- 根据性格生成动作分支
- 根据压力放大极端选择
- 生成多个自然长出来的剧情候选

### 4.5 候选排序接口

#### `rank_plot_candidates()`

输入：

- `PlotCandidate[]`
- `V3` 留存目标函数
- 章节阶段
- 题材信息

输出：

- 排序后的 `PlotCandidate[]`
- 选中候选

职责：

- 用 `V3` 的留存目标函数筛选最优候选
- 避免只选“自然但不抓人”的桥段

## 5. 与 V3 的联动接口

### 5.1 输入联动

V4 推导完成后，必须把以下内容送给 V3：

- 剧情候选列表
- 候选留存分数
- 候选钩子强度
- 候选冲突强度
- 候选模板风险

### 5.2 输出联动

V3 负责：

- 选择哪个候选更留人
- 决定章节节奏与结尾钩子
- 决定是否需要压缩 / 拉长 / 延迟揭示

### 5.3 原则

- V4 负责“长出来”
- V3 负责“留不留人”
- V1/V2 负责“稳不稳”

## 6. 数据流建议

1. 读入剧情上下文
2. 识别角色关系
3. 识别角色性格
4. 识别外部压力
5. 推导剧情候选
6. 候选打分与解释
7. 用 V3 进行留存排序
8. 输出最终建议

## 7. 兼容与回滚

### 兼容原则

- V4 只作为增量层，不替代 V3
- V4 的候选可以不开启
- V4 的模块可以独立关闭

### 回滚原则

- 关闭 V4 后，系统仍可回到 V3 + V1/V2 路径
- V4 的数据结构不能强制主线依赖
- V4 的评分不能写死到主线默认行为里

## 8. 设计边界

### 允许

- 结构化关系分析
- 性格驱动选择分析
- 压力驱动剧情推导
- 多候选桥段生成
- 与 V3 联动排序

### 不允许

- 直接用固定模板替代推导
- 不解释地给一个结果
- 脱离关系 / 性格 / 压力硬编剧情
- 把 V4 当成主线唯一入口

## 9. 一句话总结

> V4 的接口设计要把“人物关系、人物性格、外部压力”变成可计算输入，把“自然长出来的剧情候选”变成可排序输出，并把最终选择权交给 V3 的留存目标函数。