# Claude 评审工程包（v8.1 修订版）

> 用途：把 `v8.1` 的“反派反馈控制工程”修订材料一次性整理给 Claude，确认这轮结构收紧是否已经解决上一轮打回的问题。

## 1. 本次评审对象

这是一个面向“小说内容生成推荐系统”的独立控制核心修订包，目标不是现实操控，也不是直接写正文，而是生成：

1. 不同反派如何基于自己的旧伤、信念、风味和场域理解出刀
2. 每次出刀后如何形成分层状态偏移
3. 如何把这些偏移写入长线账本，供后续内容生成或推荐系统复用

这次不是原始 `v8` 的再转发，而是已经吸收上一轮 Claude 评审意见后的 `v8.1` 修订版。

## 2. 这轮修订最重要的纠偏

请注意，上一版文档里有一个错误宿主假设：

- 之前误把实现宿主写成了其他线程里的 `packages/core`
- 那不是当前 `alpha-autopilot` 仓库的正确落点

当前 `v8.1` 已明确改为：

- 以当前仓库为唯一语境
- 以 `backend/app/services/narrative_v8/` 作为第一阶段建议宿主
- 保持独立 increment 控制核心，不直接接 `writer`、UI、CLI、持久化

## 3. 建议一起提交给 Claude 的文件

按重要程度排序：

1. 主实施计划
[2026-05-04-villain-feedback-control-engineering-plan.md](/D:/workspace/alpha-autopilot/codex-review/v8/2026-05-04-villain-feedback-control-engineering-plan.md)

2. Schema 草案
[2026-05-04-villain-feedback-control-schema.md](/D:/workspace/alpha-autopilot/codex-review/v8/2026-05-04-villain-feedback-control-schema.md)

3. 系统上下文总结
[2026-05-04-knife-system-context-summary.md](/D:/workspace/alpha-autopilot/codex-review/v8/2026-05-04-knife-system-context-summary.md)

4. 反派创作分析来源稿
[2026-05-04-villainess-blackening-spiral-analysis.md](/D:/workspace/alpha-autopilot/codex-review/v8/2026-05-04-villainess-blackening-spiral-analysis.md)

如果只想给最小评审集，至少发前 3 份。

## 4. 建议 Claude 的阅读顺序

1. 先读 `2026-05-04-knife-system-context-summary.md`
理解为什么系统要从“案例模仿”转向“刀法原语 + 人格参数 + 场域映射 + 长线状态”。
注意：这份文件是概念上下文；具体字段形状请以后面的 schema 文档为准。

2. 再读 `2026-05-04-villain-feedback-control-schema.md`
检查 `v8.1` 是否已经把：

- 分层状态账本
- 显式刀法约束
- 结构化输出包
- observer topology / power topology

这些边界定稳。

3. 最后读 `2026-05-04-villain-feedback-control-engineering-plan.md`
评估当前的任务顺序、验证门、测试策略、宿主路径和实施可执行性是否已经收口。

4. 如需追溯创作来源，再读 `2026-05-04-villainess-blackening-spiral-analysis.md`

## 5. 希望 Claude 重点复核的内容

请重点复核下面 6 点：

### 5.1 上一轮 P0 是否真正被解决

1. `StateLedger` 是否已经从扁平 delta 拆成 relationship / narrative / psychological / hook 四层
2. 刀法约束是否已经从松散字符串数组收紧成显式 constraint / compatibility 模型
3. `VillainFeedbackPacket` 是否已经从叙述性平铺结构收紧为 decision / explanation / state_shift / hook / flavor 分层输出

### 5.2 上一轮 P1 是否真正被解决

1. 风味是否已经收口到稳定 profile，而不再分散抢定义权
2. `TargetProfile` 是否已经补上 `defense_style / witness_sensitivity / identity_anchor`
3. `SceneContext` 是否已经补上观察者角色和权力拓扑
4. 实施顺序是否已经把验证层放到 controller 之前

### 5.3 宿主纠偏是否合理

1. 当前把第一阶段宿主放在 `backend/app/services/narrative_v8/` 是否比旧版错误的 `packages/core` 更符合当前仓库
2. 这个宿主选择是否足够独立，不会误伤现有 baseline/default path

### 5.4 差异化控制是否够硬

1. 同一把刀在不同反派手里，是否真的能避免“同一个反派换皮”
2. 同一个反派在不同 observer/power topology 下，是否会真正改变出刀选择

### 5.5 长线控制是否够稳

1. 状态账本现在的分层是否足够支撑长线伏笔、收网、误判、回收
2. hook 层是否和关系层、叙事层边界清楚

### 5.6 实施计划是否已经具备工程收口感

1. 是否还有会在实现时把业务规则重新塞回 controller 的风险
2. 是否还缺关键测试门或中间验证门

### 5.7 这轮重点风险是否真的封死

1. selector 是否已经明确是“先硬过滤、后对幸存项打分”的控制器，而不是“按偏好排序”的打分器
2. `rejected_knives` 是否已经足够结构化，能区分硬过滤失败和低分淘汰
3. `anti_conditions`、`observer_requirements`、`forbidden_moves` 是否都已经被定义为硬过滤
4. no-fit 时是否有明确 fallback，而且 fallback 在结构上不会伪装成一把主刀
5. controller 是否仍然只负责编排，没有把 ledger/constraint 规则又混回去
6. `FlavorRender` 是否已经明确要求影响结构化输出，并通过显式结构字段声明影响面，而不只是改文案语气

## 6. 希望 Claude 输出的报告格式

建议 Claude 按下面格式返回：

1. `总体判断`
现在的 `v8.1` 是否已经从“概念正确但不够工程化”推进到“可以作为下一轮实现基线”。

2. `仍然存在的关键问题`
继续按严重度列 `P0 / P1 / P2`。

3. `Schema 是否已收口`
重点看状态分层、约束显式化、observer topology、structured packet。

4. `实施计划是否已收口`
重点看宿主、任务顺序、验证门、差异化测试。

5. `还需要补的地方`
如果还有残缺，请直接指出最该补的 1 到 3 个点。

6. `是否建议进入实现`
明确回答：

- 可以进入第一阶段实现
- 还需要再做一轮文档修订

## 7. 可直接复制发给 Claude 的提示词

```text
请你作为架构评审和工程设计评审，复核这组 v8.1 修订文档。

背景说明：
这不是第一次评审。上一轮你已经指出了几个关键问题，包括：
1. StateLedger 太扁平
2. 刀法约束不够显式
3. VillainFeedbackPacket 太叙述化
4. SceneContext 缺 observer topology / power structure
5. plan 里 validation gate 不足
6. selector 有退化成“打分器”的风险
7. ledger 虽然分层，但应用逻辑有混回 controller 的风险
8. FlavorRender 有退化成文案层的风险

这次 v8.1 已经按这些意见做了结构收紧。
另外，上一版有一个错误线程污染：把实现宿主误写成了其他项目里的 packages/core。当前版本已纠正为当前仓库语境下的 Python 独立 increment 模块，建议宿主是 backend/app/services/narrative_v8/。

请按下面顺序阅读：
1. codex-review/v8/2026-05-04-knife-system-context-summary.md
2. codex-review/v8/2026-05-04-villain-feedback-control-schema.md
3. codex-review/v8/2026-05-04-villain-feedback-control-engineering-plan.md
4. codex-review/v8/2026-05-04-villainess-blackening-spiral-analysis.md（如需追溯创作来源再读）

请重点复核：
1. v8.1 是否已经真正解决上一轮 P0/P1 问题
2. 状态账本是否已经足够分层
3. 刀法约束是否已经足够显式
4. 输出包是否已经足够结构化
5. observer topology / power topology 是否已足够进入第一阶段实现
6. 当前 Python 宿主选择是否合理
7. 实施计划顺序是否已经把 validation 放在 controller 之前
8. 差异化测试是否足够防止“所有反派一个味”
9. selector 是否已经被定义成“硬过滤 + 幸存候选打分”的控制器
10. no-fit fallback 是否在结构上允许“没有主刀”，而不是用假刀占位
11. controller 是否仍然只是 orchestrator，而没有偷藏 ledger / constraint 规则
12. FlavorRender 是否已经要求改变结构化输出，并显式声明改了哪些结构面，而不是只改措辞

请按下面格式输出：
1. 总体判断
2. 仍然存在的关键问题（按 P0/P1/P2）
3. Schema 是否已收口
4. 实施计划是否已收口
5. 还需要补的地方
6. 是否建议进入实现

如果你认为还有地方不够稳，请直接给出替代方案，不要只给抽象意见。
```

## 8. 一句话说明

> 这是已经按上一轮意见做过结构收紧的 `v8.1` 修订包，请你重点判断：它现在是否已经从“方向对但还不够工程化”推进到“可以作为第一阶段实现基线”。
