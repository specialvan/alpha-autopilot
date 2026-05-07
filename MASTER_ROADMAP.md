# alpha-autopilot 总路线图文档

## 1. 项目总定位

`alpha-autopilot` 是一个面向小说章节推荐与写作辅助的研究型系统，目标是把“模型黑箱前的提示词工程”与“特征矩阵推荐”结合起来，形成一个可解释、可迭代、可验证、可进化的章节规划系统。

当前采用三层治理结构：

- **Baseline**：`v1/v2`，稳定收口，只允许修复和兼容性维护
- **Increment**：`v3`~`v6`，质量层、推荐增强与动态推演能力，独立推进、可灰度、可回滚
- **Experimental**：探索性方案，必须与主线隔离

项目演进分为四个阶段：

- 第一阶段：原型闭环
- 第二阶段：稳定化与扩展
- 第三阶段：读者留存目标函数与生成控制层
- 第四阶段：动态故事世界推演（V6）

---

## 2. 第一阶段 原型闭环

### 2.1 阶段目标

验证系统能否形成稳定的最小闭环。

### 2.2 定位说明

这一阶段对应的是当前基线能力的形成过程。已完成内容仍然属于 Baseline 的基础能力集合，但后续只允许维护，不允许继续扩张为新主线。

### 2.3 核心问题

- 状态建模能不能成立
- 特征评分能不能成立
- 候选推荐能不能成立
- 推荐预览能不能成立
- 训练与反馈闭环能不能成立
- 前后端能不能联动
- 工程文档能不能完整

### 2.3 已完成内容

#### 后端原型
- `StoryState` 叙事状态模型
- `CharacterState` 角色状态模型
- `FeatureMatrix` 特征矩阵
- `ChapterPlanner` 候选推演器
- 推荐结果工程化输出
- 推荐预览接口
- 训练接口
- 反馈接口
- 版本管理
- 训练日志
- FastAPI 项目结构

#### 前端工作台
- 总览面板
- 叙事状态面板
- 特征矩阵面板
- 章节建议摘要模块
- 推荐调参模块
- 推荐结果面板
- 训练结果展示区
- 反馈闭环入口
- React 联动
- 后端 API 接入
- 本地回退数据

#### 工程交付材料
- 后端 PRD
- 前端 PRD
- 项目进度表
- 技术瓶颈文档
- 评审说明
- 交付清单
- 总评审包
- 迁移接口草案
- 集成目录树与模块职责说明

### 2.4 第一阶段产出

- 可运行的小说章节推荐研究原型
- 可解释的推荐与训练闭环
- 可视化前端工作台
- 可审查、可复盘的工程文档链路

### 2.5 第一阶段验收标准

- 能运行推荐预览
- 能运行训练并生成版本快照
- 能提交反馈并记录日志
- 能通过前端查看章节建议和调参结果
- 能形成完整的本地开发闭环

---

## 3. 第二阶段 稳定化与扩展

### 3.1 阶段目标

把第一阶段的原型闭环推进到更稳定、更大规模、更接近生产可用的工程形态。

### 3.2 治理说明

这一阶段以 Baseline 稳定化为主，同时为 `v3` 增量层预留接入位。这里的“扩展”不等于随意增功能，而是指在不破坏基线的前提下补齐契约、评估和稳定性。

### 3.2 关键任务

#### 3.2.1 数据与样本升级
- 扩充拆解样本数量
- 增加题材样本
- 增加风格样本
- 增加阶段样本
- 增加失败样本和边界样本
- 建立样本版本管理

#### 3.2.2 契约冻结与接口稳定
- 冻结 `StoryState` schema
- 冻结推荐结果 schema
- 冻结训练与反馈请求响应格式
- 统一前后端字段命名
- 统一错误码与返回结构

#### 3.2.3 评估体系增强
- 增加章节质量评分
- 增加风格一致性评分
- 增加节奏适配评分
- 增加采纳率统计
- 增加预览命中率统计
- 增加泛化测试

#### 3.2.4 章节生成链路增强
- 推荐结果转章节大纲
- 摘要转章节结构模板
- 章节结构转分段建议
- 生成后的修订建议
- 生成后的审稿建议

#### 3.2.5 工程化与稳定性
- 样本、版本、日志、反馈持久化
- 增加异步任务
- 增加错误处理
- 增加回滚能力
- 增加接口测试
- 增加回归测试
- 增加部署脚本

#### 3.2.6 前端继续升级
- 训练结果历史对比
- 版本切换
- 推荐预览对比
- 调参滑块化
- 反馈结果可视化
- 章节建议模板切换
- 风险提示和审稿提示

### 3.3 第二阶段产出

- 更稳定的章节推荐引擎
- 更强的数据泛化能力
- 更明确的评估标准
- 更可维护的工程结构
- 更接近生产可用的写作辅助系统

### 3.4 第二阶段验收标准

- 样本规模明显提升
- 推荐结果在更多题材下稳定
- 评估体系具备可对比性
- 训练与反馈过程可持续
- 前后端联动更顺畅
- 文档与接口契约保持一致

---

## 4. 第三阶段 读者留存目标函数与生成控制层

### 4.1 阶段目标

让系统在保持结构正确、风格一致、世界观约束的前提下，把“留住读者继续阅读”作为顶层目标函数，并将该目标真实驱动主决策链路。

### 4.2 治理说明

这一阶段对应 `v3` 增量层的核心目标。它不替代 `v2` 主工作台，而是通过受控接入把留存目标函数和生成控制层叠加到主线。

范围锚点：

- 当前权威范围：读者留存目标函数、生成控制层、以及对 recommendation/training/workbench 的受控接入。
- 历史表述“推荐价值自适应进化”仅作为背景，不覆盖当前第三阶段范围。
- `v1/v2` 保持默认基线路径，`v3` 接入必须可降级、可回滚。

### 4.3 核心问题

- 如何把留存目标函数从文档定义落成可计算、可解释的决策信号
- 如何让情绪、节奏、爽点、悬念、冲突、钩子等标签从描述字段升级为决策变量
- 如何在不破坏基线的前提下，把控制层渐进接入规则/搜索/评估与训练/工作台链路
- 如何避免模板化过拟合，同时保留结构、风格、事实护栏

### 4.4 关键任务

#### 4.4.1 目标函数与控制层
- 定义留存目标函数
- 定义生成控制层输入输出
- 定义标签到决策的映射

#### 4.4.2 训练链路接入
- 定义 V3 projection -> 训练输入映射
- 让训练链路区分 approved / provisional / rejected
- 增加训练批次 summary

#### 4.4.3 上下文 API 正式化
- 定义真实章节 context contract
- 提供章节级 state mapping
- 提供章节级 compare baseline

#### 4.4.4 workbench 展示联动
- workbench 接 reverse-outline 结果
- workbench 接 style DNA
- workbench 接 checkpoint / admission
- workbench 接留存目标与生成控制建议

#### 4.4.5 Corpus QC
- 批量质量报告
- label drift / style drift 检查
- 低质量样本筛除
- 留存风险检查

### 4.5 第三阶段产出

- `RetentionTargetFunction` 与可解释的留存代理指标
- `GenerationControlPolicy` 与标签决策映射
- recommendation / training / workbench 的受控接入结果
- 可回滚的增量开关与验证证据
- 留存风险与模板化风险的 QC 报告

### 4.6 第三阶段验收标准

- 留存目标函数已经进入主决策链路，且可解释其对最终 action 排序/选择的影响
- 生成控制标签已从展示字段升级为决策变量
- `v1/v2` 默认路径未被破坏，`v3` 可关闭、可降级、可回滚
- workbench 可查看留存与控制层信号
- 训练链路可消费 V3 projection 并输出稳定批次摘要

---

## 5. 总体阶段关系

### 第一阶段回答

> 这套系统能不能跑通？

### 第二阶段回答

> 这套系统能不能在不破坏基线的前提下稳定收口并为增量接入做好准备？

### 第三阶段回答

> 这套系统能不能把“留住读者”变成显式目标函数，并稳定驱动主决策链路？

---

## 6. 推荐推进顺序

### 先做第一阶段
完成原型闭环和工程交付。

### 再做第二阶段
扩充样本、冻结契约、增强评估、强化工程稳定性。

### 最后做第三阶段
建立留存目标函数与生成控制层，并以受控方式接入主链路。

---

## 7. 最终目标

把 `alpha-autopilot` 从一个研究原型，逐步演进为一个能够持续自我优化的写作辅助与章节推荐系统。

---

## 8. 第四阶段（V6）动态故事世界推演

### 8.1 阶段目标

在不破坏 `v1/v2` 基线路径前提下，把系统从“静态章节推荐”升级为“可审计、可干预、可回放的多路径故事世界推演”。

### 8.2 执行顺序

1. P0：`PR-AA-09`~`PR-AA-11` 打通最小主链路（文本 -> seed -> 人设参数 -> 并行推演 -> winner）
2. P1：`PR-AA-12`~`PR-AA-14` 增强冲突探针、事件注入与角色访谈
3. P2：`PR-AA-15` 补齐群体/派系记忆层

### 8.3 2026-04-28 状态

- P0/P1/P2 已全部完成并通过专项测试
- `T01` 到 `T08` 已全部 `ACCEPTED`
- 阶段执行与验收证据见 `claude_review_package/V6/` 文档包

## 9. V8.2 Standalone Villain Feedback Control Core (2026-05-05)

- Layer classification: `Increment`, standalone, default-off by architecture.
- Host alignment: `backend/app/services/narrative_v8/`.
- Scope position:
  - adjacent to the phase-3 generation-control direction
  - wired only into the `v2` workbench context enrichment path behind `v8_workbench_enabled`
  - not wired into baseline recommendation routes or dashboard defaults
  - intended as a reusable control core for later consumers
- Current state:
  - `V8.1` schema/selector/controller baseline has been tightened into a `V8.2` runtime that now includes helper-owned `fallbacks.py`, `transition_policy.py`, and `transitions.py`
  - `SceneContext.current_control_state`, `VillainFeedbackPacket.transition`, `BuildVillainFeedbackOutput.next_control_state`, and `BuildVillainFeedbackOutput.build_followup_scene(...)` are now aligned as the standalone control-surface handoff
  - transition upgrades are now gated by explicit observer-topology and public-trace rules instead of a single soft upgrade window
  - the guarded `/api/v2/workbench/contexts` consumer now adopts both `next_control_state` and `followup_scene` through `v8_preview`, summarized through `workbench_bridge.py`
  - differential, transition, fallback, controller, integration, and benchmark-matrix tests are in place
  - layered regression entry and acceptance-report script are in place and cover the expanded V8 helper surface
- Mainline decision:
  - not a mainline candidate yet because only a guarded `v2` workbench consumer is wired; broader API/UI/writer/storage rollout remains out of scope
  - baseline rollback risk remains low because non-workbench default paths do not call V8 and the workbench caller is gated by `v8_workbench_enabled`
