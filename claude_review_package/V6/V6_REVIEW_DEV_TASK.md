# 给 Codex 的 V6 评审与开发任务说明

## 任务名称

V6 动态故事世界推演升级（Dynamic Narrative Simulation）

## 任务背景

在 `v1/v2` 稳定基线、`V3` 留存目标函数、`V4` 关系-性格-压力因果链、`V5` 结构化增强（PR-AA-01~08）基础上，V6 要把系统从“静态推荐”推进为“可运行故事世界推演”。

本轮重点不是新增一个按钮，而是打通：

> 文本种子 -> 可运行角色世界 -> 多路径推演 -> 留存排序 -> 作者干预 -> 访谈与群体记忆。

## 任务目标

- 用 `PR-AA-09` 到 `PR-AA-15` 形成可拆分、可评审、可验收的执行链路
- 先完成 P0 主链路（09/10/11），再做 P1（12/13/14），最后 P2（15）
- 保持 `V2 Workbench` 为承载层，不重建孤立界面
- 所有 LLM 能力必须有 deterministic/mock fallback
- 所有写入正式设定的动作都必须人工确认

## 归属层判断

### 归属层

- [ ] Baseline
- [x] Increment
- [ ] Experimental

### 判断依据

- V6 是 V3/V4/V5 的增量扩展，不是基线替换
- 新增能力影响推演和决策层，需可灰度、可回滚
- 需求目标明确，非探索性试验

## 需要重点评审的 7 个能力切片

1. PR-AA-09：小说种子信息结构化提取器
2. PR-AA-10：文本驱动自动人设参数化
3. PR-AA-11：多路径情节并行推演
4. PR-AA-12：涌现式冲突探针
5. PR-AA-13：上帝视角事件注入与重算
6. PR-AA-14：角色访谈接口
7. PR-AA-15：群体/派系记忆层

## 评审门禁（阻断级）

以下任一不满足即阻断：

1. 绕开 `V3` 留存排序，winner 由不可解释规则直接决定
2. 多路径推演共享中间状态，导致路径污染
3. 低置信度抽取结果默认写入正式 Story Bible
4. 事件注入后无审计日志、无重算前后差异
5. 访谈内容默认进入正史
6. 缺 deterministic/mock 测试路径
7. 破坏 `v1/v2` 默认推荐与 `V2 Workbench` 现有流程

## 影响范围

### 代码

- `backend/app/services/narrative_v6/`（新增）
- `backend/app/api/routes/narrative_v6.py`（新增）
- `backend/app/main.py`（路由接入）
- `tests/test_narrative_*_v6*.py`（新增）
- `scripts/run_layered_tests.py`（新增 v6 layer）

### 文档

- `claude_review_package/V6/*`
- `claude_review_package/README_FOR_CODEX.md`
- `claude_review_package/package_manifest.md`
- `claude_review_package/final_document_index.md`
- `PROJECT_STATUS.md`（记录 V6 真实状态与证据）

## 设计边界

### 允许做的事

- 在 `narrative_v6` 命名空间新增 schema、服务与 API
- 用 mock/deterministic 方式先打通 P0 主链路
- 将模拟结果作为 Workbench 可消费报告输出
- 通过开关/降级保持基线可回退

### 不允许做的事

- 不允许让 V6 直接改写 `v1/v2` 默认行为
- 不允许把访谈内容默认写入正式设定
- 不允许把 GraphRAG 基础设施作为 P0 阻断项
- 不允许在无审计日志情况下写入持久世界状态

## 回滚策略

- 一级：关闭 V6 入口（路由级或 feature flag 级）
- 二级：回退至 V4/V3 决策链路
- 三级：关闭事件注入/访谈等高风险能力，仅保留只读推演
- 回滚后必须验证 `v1/v2` 与 `V2 Workbench` 默认路径

## 验收标准（阶段）

### V6-A（P0）

- 章节文本 -> NarrativeSeed -> ParameterizedCharacterProfile -> 3 路推演 -> winner
- 单路径失败不拖垮整次模拟
- Workbench/前端可消费 `decision_summary`

### V6-B（P1）

- 冲突探针可输出候选
- 支持事件注入后重算和审计
- 角色访谈可输出 transcript 和风险标记

### V6-C（P2）

- 群体记忆可影响成员行为约束
- 章节范围过滤与 hidden 过滤生效
- 传播日志与可撤销补丁可追溯

## Codex 执行要求

1. 先读治理与 V6 主需求文档
2. 先做 PR 切片与任务板，再做实现
3. 每个切片先补 deterministic 测试，再落代码
4. 每个切片必须有回滚说明
5. 每轮完成后回写状态文档与验收证据

## 一句话

> V6 的目标是把“推荐建议”升级为“可审计、可干预、可回放的动态故事世界推演”，且全过程不破坏基线默认行为。
