# V8 Codex Review Request Prompt

请你认真阅读 Claude 对 v8 的评审结论，并把原来的 v8 方案改成更适合落地的 v8.1。

## 背景

当前项目是一个“小说内容生成推荐系统”的反派反馈控制核心，不是现实操控系统，也不是直接写正文的 writer 模块。

Claude 的核心判断是：

- 方向正确
- 但当前设计还不够工程化
- 不能直接进入实现
- 需要先做结构收紧和约束补强

## 请优先阅读

1. `claude_review_package/v8/V8_CLAUDE_REVIEW_SUMMARY.md`
2. `claude_review_package/v8/README.md`
3. 原始 v8 设计文件

## Claude 重点指出的问题

### 1. 状态账本太平

`StateLedger` 不能只是单一 delta 表。
它必须至少区分：

- relationship state
- narrative state
- psychological echo state
- hook / deferred payoff state

### 2. 刀法约束不够显式

`preferredKnives`、`secondaryKnives`、`forbiddenMoves` 不够。
还需要：

- knife compatibility graph
- scene restrictions
- target restrictions
- anti-conditions
- backfire conditions

### 3. 输出包太叙述化

`VillainFeedbackPacket` 需要更结构化，至少要区分：

- decision layer
- explanation layer
- state shift layer
- hook layer

### 4. 风味定义散落

风味相关字段不能到处分散。
需要明确哪个是稳定偏好，哪个是场景渲染，哪个只是人格外壳。

### 5. 场景模型太粗

`audience` 不能只是一个数组。
要区分观众角色，例如：

- witness
- judge
- transmitter
- buffer
- recovery node

### 6. 实施计划缺少验证层

在 controller 之前，必须补：

- schema validation
- knife compatibility tests
- state boundary tests
- same knife / different villain tests
- same villain / different scene tests

## 你要做什么

请把 v8 方案重构成更稳的 v8.1 版本，并明确指出：

1. 哪些字段保留
2. 哪些字段重命名或拆分
3. 哪些验证规则必须前置
4. 哪些 helper 必须先做
5. 测试顺序怎么调整
6. 计划顺序怎么改

## 输出要求

请按下面格式输出：

1. `v8.1 修订总览`
2. `保留项`
3. `需要拆分或新增的结构`
4. `必须前置的约束与验证`
5. `实施顺序修订`
6. `测试顺序修订`
7. `仍然保留的风险`

## 额外要求

- 不要继续沿用“只要字段够多就行”的思路
- 不要把风味当成纯文案层
- 不要把 controller 变成规则发现器
- 先把边界、约束、状态层次定稳，再谈实现
