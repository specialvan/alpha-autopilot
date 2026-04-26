# V3 代码模块计划

## 1. 目标

把“留住读者”的顶层目标函数落成可计算模块，并接入现有章节拆解和工作台链路。

## 2. 建议目录结构

- `alpha_autopilot_v3/retention/`
- `alpha_autopilot_v3/generation_control/`
- `alpha_autopilot_v3/evaluation/`
- `alpha_autopilot_v3/feedback/`

## 3. 代码模块说明

### 3.1 `retention/`

职责：

- 定义留存目标函数
- 计算留存指标
- 输出留存解释信息

建议文件：

- `models.py`
- `target_function.py`
- `metrics.py`

### 3.2 `generation_control/`

职责：

- 把留存目标函数变成生成控制计划
- 输出情绪 / 节奏 / 爽点 / 悬念 / 冲突 / 钩子建议
- 生成 anti-pattern 警告

建议文件：

- `models.py`
- `mapping.py`
- `policy.py`

### 3.3 `evaluation/`

职责：

- 留存评分
- 章节吸引力评分
- 模板风险检测

建议文件：

- `retention_score.py`
- `template_risk.py`
- `attraction_score.py`

### 3.4 `feedback/`

职责：

- 回写用户反馈
- 回写策略权重
- 支持留存相关的动态调权

建议文件：

- `updater.py`
- `models.py`

## 4. 现有文件需要改动的部分

### 4.1 `alpha_autopilot_v3/decomposition/models.py`

需要扩展章节拆解记录字段：

- `retention_signal`
- `attraction_score`
- `hook_strength`
- `pace_pressure`
- `emotion_curve`
- `decision_tags`
- `control_suggestions`

### 4.2 `alpha_autopilot_v3/decomposition/pipeline.py`

需要增加：

- 留存指标计算
- 控制计划生成
- `workbench_context` 回写

### 4.3 `alpha_autopilot_v3/__init__.py`

需要导出 V3 新对象：

- `RetentionTargetFunction`
- `RetentionMetrics`
- `GenerationControlPlan`
- 对应构建函数

## 5. 接口对齐原则

- 先有目标函数，再有控制计划
- 先有评分，再有排序
- 先有解释，再有自动化
- 新字段必须是可选的，不能破坏旧路径

## 6. 测试补充建议

- `RetentionTargetFunction` 单测
- `RetentionMetrics` 单测
- `GenerationControlPlan` 单测
- pipeline 集成测试
- workbench context 回归测试

## 7. 一句话总结

> V3 的代码模块计划就是把“留住读者”拆成目标函数、评分、控制、反馈四层，并以最小破坏方式接入现有 pipeline。