# V3 读者留存目标函数与生成控制接口设计

## 1. 设计目标

V3 的接口设计目标是把“留住读者”从抽象愿景变成可计算、可控制、可回写的系统能力。

它至少要完成三件事：

- 定义留存目标函数
- 定义生成控制层接口
- 定义与工作台 / 训练 / 评估的接入方式

## 2. 顶层模块划分

建议新增 V3 模块：

- `alpha_autopilot_v3/retention/`
- `alpha_autopilot_v3/generation_control/`
- `alpha_autopilot_v3/evaluation/`
- `alpha_autopilot_v3/feedback/`

## 3. 核心对象设计

### 3.1 留存目标函数对象

#### `RetentionTargetFunction`

描述系统的留存优先目标。

建议字段：

- `name`
- `primary_objective`
- `priority_order`
- `guardrails`
- `dynamic_weights`
- `explainability_notes`

#### 作用

- 统一系统对“什么更能留住读者”的定义
- 为生成控制层提供目标约束

### 3.2 留存指标对象

#### `RetentionMetrics`

描述某章节 / 某候选文本的留存倾向。

建议字段：

- `chapter_attraction_score`
- `continue_reading_intent`
- `emotional_drive`
- `pacing_drive`
- `suspense_drive`
- `conflict_drive`
- `hook_strength`
- `template_risk`
- `evidence`

#### 作用

- 提供候选排序输入
- 识别模板化风险
- 支持反馈闭环

### 3.3 生成控制计划对象

#### `GenerationControlPlan`

描述如何根据留存目标调整生成策略。

建议字段：

- `target_function`
- `retention_metrics`
- `focus_mode`
- `emotional_curve`
- `pacing_curve`
- `suspense_curve`
- `conflict_curve`
- `hook_strategy`
- `anti_pattern_warnings`
- `decision_tags`
- `suggestions`

#### 作用

- 把留存目标函数转成具体控制建议
- 让标签真正影响生成决策

### 3.4 章节输出增强对象

建议在现有章节拆解记录里扩展：

- `retention_signal`
- `attraction_score`
- `hook_strength`
- `pace_pressure`
- `emotion_curve`
- `decision_tags`
- `control_suggestions`

## 4. 核心接口设计

### 4.1 目标函数接口

#### `build_retention_target_function()`

输入：无或基础配置

输出：`RetentionTargetFunction`

职责：

- 建立留存优先目标
- 设置 guardrails
- 设置目标说明

### 4.2 留存评分接口

#### `build_retention_metrics(record)`

输入：

- 章节拆解记录

输出：

- `RetentionMetrics`

职责：

- 计算章节吸引力
- 计算继续阅读意愿代理值
- 识别模板化风险

### 4.3 生成控制接口

#### `build_generation_control_plan(record)`

输入：

- 章节拆解记录
- 留存目标函数
- 留存指标

输出：

- `GenerationControlPlan`

职责：

- 决定章节生成倾向
- 输出节奏、冲突、钩子、悬念建议
- 生成 anti-pattern 风险提示

### 4.4 候选排序接口

#### `rank_by_retention()`

输入：

- 多个候选章节 / 候选段落
- 留存目标函数
- 留存指标

输出：

- 排序结果

职责：

- 选择最能留人的候选
- 防止回到模板化输出

## 5. 与现有 pipeline 的联动

### 5.1 输入联动

`pipeline` 需要接收：

- 章节文本
- 章节阶段
- 题材信息
- 前后章节上下文

### 5.2 中间联动

`pipeline` 需要在拆解后补充：

- 留存指标
- 控制计划
- 决策标签

### 5.3 输出联动

最终 `workbench_context` 中必须包含：

- 留存分数
- 钩子强度
- 模板风险
- 生成控制建议

## 6. 与 V1/V2 的关系

### V1/V2

- 提供稳定结构与工作台能力
- 作为 V3 的基线输入

### V3

- 追加留存目标函数
- 追加生成控制层
- 作为 V4 的排序和约束层

### 原则

- V3 不改写 V1/V2 默认路径
- V3 只追加，不推翻
- V3 的输出要可关闭、可降级、可回滚

## 7. 回滚与兼容

- 关闭留存控制后，pipeline 仍可输出原始拆解结果
- 留存评分失败时，不阻断基础工作台
- 新字段必须可选，不得强制依赖

## 8. 设计边界

### 允许

- 留存评分
- 节奏 / 情绪 / 爽点 / 悬念 / 冲突控制
- 模板风险检测
- 控制计划输出

### 不允许

- 把留存做成单一模板规则
- 把评分做成不可解释黑箱
- 把控制建议写死成固定话术

## 9. 一句话总结

> V3 的接口设计要把“留住读者”变成可计算对象，把生成控制变成可解释建议，并且能和现有工作台与训练链路无缝联动。