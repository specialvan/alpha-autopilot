# V4 代码模块拆解计划

## 1. 目标

把 V4 的“人物关系 + 人物性格 + 外部压力 -> 剧情自然长出来”的能力拆成可实现、可测试、可回滚的代码模块，并与 V3 留存控制层联动。

## 2. 顶层模块结构

建议新增模块：

- `alpha_autopilot_v4/relations/`
- `alpha_autopilot_v4/personality/`
- `alpha_autopilot_v4/pressure/`
- `alpha_autopilot_v4/plot_generation/`
- `alpha_autopilot_v4/integration/`
- `alpha_autopilot_v4/qc/`

## 3. 模块职责

### 3.1 `relations`

职责：

- 表达人物之间的关系差值
- 计算关系冲突边界
- 输出关系位移信号

建议文件：

- `models.py`
- `analyzer.py`
- `scoring.py`

核心对象：

- `RelationshipProfile`
- `RelationshipDelta`
- `RelationshipTensionResult`

### 3.2 `personality`

职责：

- 表达人物的压力下行动偏好
- 计算相同行为在不同性格下的选择偏差
- 输出人物决策倾向

建议文件：

- `models.py`
- `analyzer.py`
- `decision_policy.py`

核心对象：

- `PersonalityProfile`
- `DecisionBias`
- `ActionPreference`

### 3.3 `pressure`

职责：

- 表达断粮、威胁、羞辱、限时、利益争夺、生死压力等压力源
- 计算压力强度
- 给剧情推导提供发动机信号

建议文件：

- `models.py`
- `analyzer.py`
- `pressure_index.py`

核心对象：

- `PressureProfile`
- `PressureSource`
- `PressureIntensity`

### 3.4 `plot_generation`

职责：

- 基于关系、性格、压力推导剧情候选
- 生成多个自然长出来的桥段
- 为 V3 输出候选排序前的剧情素材

建议文件：

- `models.py`
- `generator.py`
- `candidate_builder.py`
- `candidate_ranker.py`
- `cardinality.py`

核心对象：

- `PlotCandidate`
- `PlotGenerationResult`
- `PlotLineage`

### 3.5 `integration`

职责：

- 与 V3 留存目标函数联动
- 将 V4 结果接入 workbench / API / 训练链路
- 控制 V4 是否启用

建议文件：

- `v4_v3_bridge.py`
- `workbench_adapter.py`
- `pipeline.py`

核心对象：

- `V4IntegrationPayload`
- `V4ToV3BridgeResult`

### 3.6 `qc`

职责：

- 检查剧情候选是否过度模板化
- 检查人物关系是否静止
- 检查性格是否漂移
- 检查压力是否不足

建议文件：

- `template_risk.py`
- `stability_check.py`
- `drift_check.py`

核心对象：

- `PlotQCRule`
- `PlotQCSummary`

## 4. 关键数据流

### 输入

- 人物集合
- 角色关系上下文
- 人物性格数据
- 当前事件与外部压力
- 当前章节阶段
- V3 留存目标上下文

### 处理

1. 识别人物关系
2. 识别人物性格
3. 识别外部压力
4. 推导动作空间
5. 生成多个剧情候选
6. QC 过滤与解释
7. V3 留存排序
8. 输出最终建议

### 输出

- 剧情候选列表
- 选中候选
- 选择原因
- 留存排序结果
- 卡文诊断信号
- workbench 可展示结构

## 5. 与现有 V3 的接入点

### 5.1 输入接入

V4 使用 V3 提供：

- 留存目标函数
- 生成控制层
- 节奏 / 情绪 / 爽点 / 悬念 / 冲突 / 钩子约束

### 5.2 输出接入

V4 向 V3 输出：

- 剧情候选
- 候选张力分数
- 候选留存分数
- 候选模板风险
- 候选解释信息

### 5.3 联动原则

- V4 负责“怎么长出来”
- V3 负责“哪个更留人”
- V1/V2 负责“别把系统搞坏”

## 6. 推荐实现顺序

### 第一批

- `relations/models.py`
- `personality/models.py`
- `pressure/models.py`
- `plot_generation/models.py`

### 第二批

- `relations/analyzer.py`
- `personality/decision_policy.py`
- `pressure/analyzer.py`
- `plot_generation/generator.py`

### 第三批

- `plot_generation/candidate_ranker.py`
- `integration/v4_v3_bridge.py`
- `qc/template_risk.py`

### 第四批

- workbench / API / frontend 接入
- 回归测试与门禁

## 7. 测试建议

### 单元测试

- 关系差值计算
- 性格选择推导
- 压力强度计算
- 剧情候选生成
- 候选排序

### 集成测试

- V4 推导结果与 V3 留存排序联动
- V4 对 workbench context 的输出
- V4 关闭后是否可回滚到 V3

### 回归测试

- `v1/v2` 默认路径不受影响
- `V3` 留存控制继续可用
- V4 模块关闭后系统仍能跑通

## 8. 风险点

- 不要直接把关系 / 性格 / 压力写死成固定模板
- 不要把剧情候选变成单一硬编码答案
- 不要让 V4 的 QC 规则过死，导致再次模板化
- 不要越过 V3 留存目标直接选剧情
- 不要把 V4 做成主线强依赖

## 9. 一句话总结

> V4 的代码模块应该拆成“关系、性格、压力、剧情推导、V3 联动、QC”六层，先把剧情候选长出来，再交给 V3 做留存排序。