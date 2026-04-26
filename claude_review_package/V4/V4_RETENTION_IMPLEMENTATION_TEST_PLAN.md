# V4 人物关系与性格驱动剧情生成测试计划

## 1. 测试目标

验证 `V4` 的人物关系、人物性格、外部压力和剧情推导链路是否符合预期，并且能和 `V3` 的留存目标函数稳定联动，同时不破坏 `v1/v2` 的稳定路径。

## 2. 测试范围

### 2.1 人物关系模型

验证：

- 是否能正确表达地位差、信息差、情感差
- 是否能表达利益冲突、控制 / 依赖、信任 / 背叛
- 是否能输出关系位移与冲突边界

### 2.2 人物性格模型

验证：

- 是否能表达人物在压力下的行动偏好
- 是否能推导同一事件下的不同剧情选择
- 是否能避免人物性格漂移

### 2.3 外部压力模型

验证：

- 是否能表达断粮、威胁、羞辱、限时、利益争夺、生死压力、关系破裂
- 是否能计算压力强度
- 是否能把压力作为剧情发动机信号

### 2.4 剧情推导链路

验证：

- 是否能从关系 + 性格 + 压力推导剧情候选
- 是否能输出多个自然长出来的桥段
- 是否能对候选进行吸引力和留存排序
- 是否能输出可解释的选择原因

### 2.5 V3 联动

验证：

- V4 结果是否能进入 V3 留存控制层
- V3 是否能正确挑选更留人的剧情候选
- V4 关闭后是否能回退到 V3 + V1/V2 路径

### 2.6 基线兼容性

验证：

- `v1/v2` 默认路径不受影响
- `V3` 留存目标函数仍然有效
- V4 新模块关闭后系统仍可运行

## 3. 推荐测试类型

### 3.1 单元测试

适合验证：

- 关系差值计算
- 性格决策偏好
- 压力强度计算
- 剧情候选生成
- 候选排序

### 3.2 集成测试

适合验证：

- V4 推导结果与 V3 留存排序联动
- V4 对 workbench context 的输出
- V4 模块之间的调用链

### 3.3 回归测试

适合验证：

- `v1/v2` 默认路径未受影响
- `V3` 生成控制层继续可用
- V4 关闭后系统仍可跑通

### 3.4 验收测试

适合验证：

- 剧情是否从“想出来”升级为“长出来”
- 是否能输出多个自然长出来的剧情候选
- 是否能看出人物关系、性格、压力共同推动剧情

## 4. 建议测试用例

### 4.1 关系样本

准备至少三类样本：

- 地位差明显
- 信息差明显
- 情感差明显

### 4.2 性格样本

准备至少三类样本：

- 暴躁 / 直接
- 隐忍 / 务实
- 退让 / 自保

### 4.3 压力样本

准备至少三类样本：

- 断粮 / 生存压力
- 羞辱 / 限时压力
- 利益争夺 / 关系破裂压力

### 4.4 断言点

每个样本至少检查：

- relation delta / tension
- personality decision bias
- pressure intensity
- plot candidate count
- selected candidate explanation
- retention score

## 5. 验收门槛

### 功能门槛

- 关系、性格、压力都能被稳定建模
- 剧情候选能稳定生成
- 候选能和 V3 留存排序联动
- workbench 能展示关键结果

### 稳定性门槛

- 现有 V3 行为不受影响
- 关闭 V4 后系统可回退
- 旧的 `v1/v2` 逻辑仍然可用

### 文档门槛

- V4 目录内规范、接口、测试计划已齐全
- Codex 入口已同步
- 主线状态文档已同步

## 6. 推荐执行顺序

1. 先跑关系模型单测
2. 再跑性格模型单测
3. 再跑压力模型单测
4. 再跑剧情候选集成测试
5. 最后跑 V3 联动与回归测试

## 7. 一句话总结

> 这批测试要证明：V4 能把“剧情自然长出来”落成可计算、可控制、可回写的能力，同时不破坏 V1/V2 和 V3 的稳定路径。

## 8. 需求到测试映射（修订版）

- 关系差值与张力计算：
  - `tests/test_alpha_autopilot_v4_modules.py`
- 性格偏好与压力响应：
  - `tests/test_alpha_autopilot_v4_modules.py`
- 压力模型与强度指数：
  - `tests/test_alpha_autopilot_v4_modules.py`
- 多候选生成与候选排序：
  - `tests/test_alpha_autopilot_v4_modules.py`
- V4 -> V3 桥接契约：
  - `tests/test_alpha_autopilot_v4_modules.py`
  - `backend/tests/test_narrative_v4_api.py`
- V4 关闭回滚：
  - `tests/test_alpha_autopilot_v4_modules.py`
  - `backend/tests/test_narrative_v4_api.py`

## 9. 建议执行命令（修订版）

1. `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q`
2. `python scripts/run_layered_tests.py v4`
3. `python scripts/run_layered_tests.py quality api import`
