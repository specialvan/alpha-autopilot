# V3 读者留存代码模块计划

## 1. 目标

为 `V3` 追加读者留存目标函数与生成控制层，确保系统从“结构正确”升级为“更能留住读者继续阅读”。

本次改动必须满足：

- 不破坏 `v1/v2` 基线
- 不把项目改成纯模板生成器
- 让情绪、节奏、爽点、悬念、冲突、钩子等标签真正参与决策
- 支持后续评估、反馈和工作台联动

## 2. 推荐模块拆分

### 2.1 `alpha_autopilot_v3/retention/`

负责留存目标函数与代理指标。

#### 建议文件
- `__init__.py`
- `models.py`
- `target_function.py`
- `metrics.py`

#### 职责
- 定义留存目标函数
- 定义章节吸引力 / 继续阅读意愿代理指标
- 定义题材 / 阶段的动态权重
- 定义标签到留存信号的映射

---

### 2.2 `alpha_autopilot_v3/generation_control/`

负责把目标函数转成生成决策。

#### 建议文件
- `__init__.py`
- `models.py`
- `policy.py`
- `mapping.py`

#### 职责
- 接收章节上下文、标签、阶段、风险约束
- 输出情绪、节奏、爽点、钩子、冲突推进建议
- 决定当前段落是否加压、延迟揭示、提前回收、加钩子
- 把标签从描述字段升级为决策变量

---

### 2.3 `alpha_autopilot_v3/evaluation/`

负责留存导向评估。

#### 建议文件
- `__init__.py`
- `retention_score.py`
- `attraction_score.py`
- `template_risk.py`

#### 职责
- 评估章节是否抓人
- 评估是否过于模板化
- 评估情绪/节奏/爽点是否合理
- 为控制层提供排序信号

---

### 2.4 `alpha_autopilot_v3/feedback/`

负责反馈回写与策略更新。

#### 建议文件
- `__init__.py`
- `models.py`
- `updater.py`

#### 职责
- 根据采纳结果和效果调整权重
- 将反馈写回留存目标函数和控制策略
- 支持策略版本化与回滚

---

## 3. 现有文件建议改动

### 3.1 `alpha_autopilot_v3/decomposition/models.py`

#### 建议新增字段
- `retention_signal`
- `attraction_score`
- `hook_strength`
- `pace_pressure`
- `emotion_curve`
- `decision_tags`
- `control_suggestions`

#### 目的
让拆解记录不只是解释章节，还能作为生成控制输入。

---

### 3.2 `alpha_autopilot_v3/decomposition/pipeline.py`

#### 当前职责
- 章节拆解
- checkpoint 生成
- admission 判定
- workbench context 组装

#### 建议变化
把它保持为 orchestration 层，新增对以下模块的调用：
- 留存评估
- 生成控制策略
- 反馈信号组装

#### 不建议
- 不要把所有留存逻辑继续塞进 `pipeline.py`
- 不要把 `pipeline.py` 变成“大杂烩”

---

### 3.3 workbench / API / frontend

#### 建议同步字段
- 留存目标值
- 章节吸引力
- 情绪曲线建议
- 节奏建议
- 爽点布局建议
- 钩子强度建议
- 模板风险提示

#### 目的
让 `V3` 能在工作台中被查看、解释和逐步接入。

## 4. 开发顺序建议

### Phase 1
建立 `retention` 模块

- 定义留存目标函数
- 定义代理指标
- 定义标签映射

### Phase 2
建立 `generation_control` 模块

- 定义控制策略
- 定义输入输出模型
- 让标签影响生成建议

### Phase 3
建立 `evaluation` 模块

- 定义吸引力评分
- 定义模板风险检测
- 定义章节留存评估

### Phase 4
建立 `feedback` 模块

- 定义反馈回写
- 定义权重更新
- 定义策略版本化

### Phase 5
接入现有链路

- `decomposition/pipeline.py`
- workbench API
- 前端展示
- 训练输入映射

## 5. 测试建议

### 单元测试
- 留存目标函数
- 标签映射
- 控制策略输出
- 模板风险检测

### 集成测试
- pipeline -> retention -> control
- workbench context 输出
- 反馈回写

### 回归测试
- `v1/v2` 默认路径不受影响
- 现有拆解与 admission 行为不变

### 验收测试
- 输出是否更偏向“留人”而不是“套模板”
- 是否保留结构约束
- 是否能解释策略变化

## 6. 风险控制

- 不要把留存目标做成单一硬编码分数
- 不要删结构约束
- 不要让 `V3` 取代 `v2`
- 不要把实验方案写成默认路径

## 7. 一句话总结

> `V3` 的代码改动应当围绕四件事展开：留存目标函数、生成控制层、留存评估、反馈回写；其余链路以渐进接入方式支持，不破坏 `v1/v2` 基线。