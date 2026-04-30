# alpha-autopilot V7 融合开发计划 PR（Draft v1）

## 1. 文档定位

- 日期：2026-04-30
- 核心基线：`claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
- 融合来源：`claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
- 治理依据：`claude_review_package/CODEX_DEVELOPMENT_GOVERNANCE.md`、`claude_review_package/README_FOR_CODEX.md`、`PHASE3_SCOPE_ALIGNMENT_2026_04_24.md`
- 目标：在不破坏 `v1/v2` 基线与 `v3` 收口前提下，给出一版可执行、可回滚、可验收的 V7 开发计划 PR

## 2. 深度梳理结论（融合版）

### 2.1 两份 V7 文档互补关系

- 主文档（`V7_MAOSHEN...`）强在系统定位、100 条标题全量梳理、叙事 K 线交易语义、PR-AA-26~39 的上层架构。
- Claude 文档（`V7_DECISION...`）强在工程落地细节：NQM-V7 28 维定义、`H=0.78/L=0.52/T8=0.60` 阈值、R-01~R-10 路由、PR-AA-16~28 的 AC。
- 融合策略：采用“主文档编号 + Claude AC/阈值/路由细节”双轨融合，避免定位上浮而实现下沉。

### 2.2 100 条标题梳理统计（来自主文档第 6 章）

- P0：37 项（必须进入 V7 主链控制能力）
- P1：41 项（应进入 V7/V7.1）
- P2：17 项（工具化、辅助化优先）
- P3：5 项（知识库或 lint 插件优先）

### 2.3 能力簇收敛（100 条 -> 14 个工程 PR）

- 市场与卖点：6.1、6.12、6.23、6.33、6.65 -> PR-AA-27、31、39
- 开篇与钩子门禁：6.10、6.20、6.31、6.42、6.50、6.55、6.77、6.96 -> PR-AA-32、33
- NQM 指标与采样：6.6、6.30、6.68、6.80、6.87、6.100 -> PR-AA-28、34
- 冲突/反派/反转风控：6.36、6.47、6.51、6.71、6.95、6.97 -> PR-AA-37
- 死锁与破局路由：6.53、6.56、6.70、6.76、6.88 -> PR-AA-36
- 结构与节奏控制：6.4、6.22、6.29、6.34、6.40、6.60、6.74 -> PR-AA-35、38
- 文笔/POV/对话：6.8、6.13、6.21、6.37、6.54、6.72、6.99 -> PR-AA-28、37、38
- 拆书资产化：6.25、6.49、6.90、6.98 -> PR-AA-27、39

## 3. 编号策略与映射规则

- 主编号采用：PR-AA-26~39（以 `V7_MAOSHEN...` 为准）。
- 来源映射保留：在每个 PR 中记录 Claude 原编号（PR-AA-16~28）。
- 映射原则：`*_REVIEW_*` 文档用于审计与准入建议，不反向改写治理边界。

| 主编号（执行） | Claude 来源映射 | 说明 |
| --- | --- | --- |
| PR-AA-26 | 无直接对应（架构升级项） | `StoryState` 升级为 `NarrativeMarketState` 基座 |
| PR-AA-27 | PR-AA-16、PR-AA-23 | 市场供需基准 + 拆书入库参数化 |
| PR-AA-28 | PR-AA-18、25、26、27、28 | 28 维采样 + OHLCV 聚合 |
| PR-AA-29 | 阈值体系与路由规则汇总 | 支撑/阻力/止损/突破确认线 |
| PR-AA-30 | R-01~R-10 路由执行内核 | 决断反馈控制主引擎 |
| PR-AA-31 | A6 走廊与卖点契约增强 | IP 风味与商业承诺一致性 |
| PR-AA-32 | PR-AA-17、PR-AA-20 | 开篇门禁 + 十大毒点 |
| PR-AA-33 | PR-AA-19 | 章末钩子与期待债务 |
| PR-AA-34 | T6/T7/T5 相关议题增强 | 情绪满足与下注量代理 |
| PR-AA-35 | 结构套娃与循环议题增强 | 多周期叙事 K 线 |
| PR-AA-36 | PR-AA-22 | 死锁检测与破局路由 |
| PR-AA-37 | PR-AA-21、PR-AA-28 | 反派压迫/冲突层/反模式风控 |
| PR-AA-38 | 节奏与信息分配议题增强 | Pacing 控制器 |
| PR-AA-39 | PR-AA-23 + 素材库议题 | 基准资产管理与审计回放 |

## 4. 实施边界与主仓落点

### 4.1 分层与开关

- V7 全量能力默认进入 Increment 层，不写入 `v1/v2` 默认路径。
- 每个 PR 必须具备 feature flag、配置回切和模块回退路径。
- 每个 PR 交付时必须提供回滚清单（<=5 步）和基线回归验证结果。

### 4.2 代码结构（建议）

- `backend/app/services/narrative_v7/schemas.py`
- `backend/app/services/narrative_v7/nqm_sampler.py`
- `backend/app/services/narrative_v7/ohlcv.py`
- `backend/app/services/narrative_v7/threshold_band.py`
- `backend/app/services/narrative_v7/decision_controller.py`
- `backend/app/services/narrative_v7/opening_gate.py`
- `backend/app/services/narrative_v7/expectation_debt.py`
- `backend/app/services/narrative_v7/antipattern_registry.py`
- `backend/app/services/narrative_v7/deadlock_router.py`
- `backend/app/services/narrative_v7/benchmark_store.py`
- `backend/app/services/narrative_v7/benchmark_refit.py`
- `backend/app/api/routes/narrative_v7.py`
- `tests/test_narrative_v7_*.py`

### 4.3 配置项（建议新增）

- `v7_enabled`
- `v7_opening_gate_enabled`
- `v7_antipattern_guard_enabled`
- `v7_deadlock_router_enabled`
- `v7_sampler_timeout_ms`
- `v7_llm_judge_max_tokens`

## 5. 分阶段计划（按周）

| 阶段 | 日期（绝对） | 目标 | PR 范围 |
| --- | --- | --- | --- |
| S0 | 2026-05-01 ~ 2026-05-03 | 立项冻结与契约冻结 | PR-AA-26 设计评审、PR-AA-27 schema 评审 |
| S1 | 2026-05-04 ~ 2026-05-10 | 核心状态与基准参数入场 | PR-AA-26、27 |
| S2 | 2026-05-11 ~ 2026-05-17 | 采样与阈值能力闭环 | PR-AA-28、29 |
| S3 | 2026-05-18 ~ 2026-05-24 | 决断控制与开篇门禁 | PR-AA-30、32 |
| S4 | 2026-05-25 ~ 2026-05-31 | 钩子、死锁、反模式风控 | PR-AA-33、36、37 |
| S5 | 2026-06-01 ~ 2026-06-07 | 卖点/IP/情绪/循环/节奏增强 | PR-AA-31、34、35、38 |
| S6 | 2026-06-08 ~ 2026-06-14 | 资产化与验收收口 | PR-AA-39 + 全链回归 + 文档同步 |

## 6. PR 逐项详细计划（主执行清单）

### PR-AA-26 NarrativeMarketState 与 V7 控制系统基座

- 定位：V7 全链路契约底座，保证与现有 `StoryState` 兼容。
- 主要实现：新增 `NarrativeMarketState`、`NovelProjectState`、`DecisionState`、`ThresholdState` 数据模型。
- 文件落点：`backend/app/services/narrative_v7/schemas.py`、`backend/app/services/narrative_v2/state_builder.py` 兼容桥接。
- AC：兼容旧 `StoryState` 入参；序列化稳定；缺失 V7 字段时自动降级开环模式并打低置信标签。
- 测试：`tests/test_narrative_v7_state_schema.py`、`tests/test_narrative_v7_story_state_compat.py`。
- 回滚：关闭 `v7_enabled` -> 回退 `state_builder` 接口路由 -> 验证 v2/v6 smoke。
- 依赖：无（先行 PR）。

### PR-AA-27 BenchmarkParameterSet 对标小说逆向拆解参数集

- 定位：把“拆书笔记”升级为“可拟合阈值的参数资产”。
- 主要实现：YAML/JSON 双格式入库、JSON Schema 校验、`book_id` 唯一约束、样本撤回与阈值回滚。
- 文件落点：`benchmark_store.py`、`benchmark_refit.py`、`schemas.py`。
- AC：样本数 >= 5 时生成题材走廊参数（均值/σ）；入库后 T/A 层阈值可审计重算。
- 测试：`tests/test_narrative_v7_benchmark_schema.py`、`tests/test_narrative_v7_benchmark_rollback.py`。
- 回滚：停写入 -> 回切基准版本 -> 重放上一版本阈值快照。
- 依赖：PR-AA-26。

### PR-AA-28 NQMSampler 与 NarrativeMetricOHLCV

- 定位：V7 指标采样引擎与叙事 K 线底盘。
- 主要实现：28 维 NQM 采样、章节/场景/情节单元/卷级 OHLCV 聚合。
- 文件落点：`nqm_sampler.py`、`ohlcv.py`、`observability` 扩展。
- AC：P1/P2/P7 向量化无 LLM；T5/T7/T8/T9/T10 LLM-as-judge 单次 `max_tokens<=512`；28 维采样 <= 3 秒。
- 测试：`tests/test_narrative_v7_nqm_sampler.py`、`tests/test_narrative_v7_ohlcv_aggregate.py`。
- 回滚：采样开关关闭，回退到 v6 既有评分路径。
- 依赖：PR-AA-26、27。

### PR-AA-29 ThresholdBand 支撑位/阻力位/止损线

- 定位：把 NQM 从“评分”变成“可交易阈值判定”。
- 主要实现：按平台/题材/IP 风味生成阈值带；识别跌破支撑、缩量突破、放量跌破、回踩确认。
- 文件落点：`threshold_band.py`、`decision_rules.yaml`。
- AC：默认 `H=0.78/L=0.52` 可被题材参数覆写；`T8=0.60` 为独立门禁；阈值版本可追溯。
- 测试：`tests/test_narrative_v7_threshold_band.py`、`tests/test_narrative_v7_pattern_recognition.py`。
- 回滚：回切阈值配置版本；禁用动态拟合。
- 依赖：PR-AA-27、28。

### PR-AA-30 DecisionFeedbackController 决断反馈控制器

- 定位：V7 主控制器，执行 R-01~R-10 路由。
- 主要实现：输出 `NarrativeDecision`（开仓/加仓/减仓/止损/止盈/观望/反转确认/突破追随/回撤修复）；决断后反馈回写。
- 文件落点：`decision_controller.py`、`api/routes/narrative_v7.py`。
- AC：命中每条路由时产出可解释证据（命中指标、阈值、风险等级、下一观察指标）。
- 测试：`tests/test_narrative_v7_decision_routes.py`、`tests/test_narrative_v7_feedback_writeback.py`。
- 回滚：关闭控制器开关并返回“建议模式”输出，不阻断 v6。
- 依赖：PR-AA-28、29。

### PR-AA-31 SellingPointContract 与 IPFlavorVector

- 定位：把“留存”扩展为“卖点契约 + IP 风味一致性”。
- 主要实现：卖点契约模板、IP 风味向量、A6 走廊偏差判断与报警。
- 文件落点：`schemas.py`、`contract_guard.py`。
- AC：标题/简介/开篇承诺与正文兑现可对齐评估；A6 偏差 > 2σ 下沿触发风味丢失告警。
- 测试：`tests/test_narrative_v7_selling_contract.py`、`tests/test_narrative_v7_ip_flavor_corridor.py`。
- 回滚：A6 权重降为 0，不影响主流程。
- 依赖：PR-AA-27、29、30。

### PR-AA-32 OpeningGate 黄金 300 字与黄金三章诊断

- 定位：开篇硬门禁能力，吸收 Claude PR-AA-17/20。
- 主要实现：T8 综合评分、十大毒点检测、修复建议、override 日志。
- 文件落点：`opening_gate.py`、`opening_lint.py`、`narrative_v7.py`。
- AC：首章完成后再评估；`T8<0.60` 阻断后续生成；override 必记日志；修复前后评分入审计。
- 测试：`tests/test_narrative_v7_opening_gate.py`、`tests/test_narrative_v7_opening_toxic_lint.py`。
- 回滚：关闭开篇阻断，仅保留提示。
- 依赖：PR-AA-28、29、30。

### PR-AA-33 ExpectationDebt 与钩子/伏笔仓位管理

- 定位：把“钩子”从文案建议变成仓位风险控制。
- 主要实现：信息差/倒计时/伏笔持仓记录；章末 300 字 T4 检测；三类钩子建议。
- 文件落点：`expectation_debt.py`。
- AC：`T4=0` 时必须产出建议；拒绝建议可记录且不强制追加；输出仓位过重/过轻告警。
- 测试：`tests/test_narrative_v7_expectation_debt.py`。
- 回滚：关闭自动建议，仅输出诊断结果。
- 依赖：PR-AA-28、30、32。

### PR-AA-34 EmotionSatisfaction 与读者下注量代理

- 定位：情绪满足量化层，支撑 Volume 代理。
- 主要实现：安全感/掌控感/社交认证/随机奖励等维度评分；追读评论等行为代理映射。
- 文件落点：`emotion_satisfaction.py`、`volume_proxy.py`。
- AC：无线上真实行为时可使用对标模拟代理；输出可解释分解项。
- 测试：`tests/test_narrative_v7_emotion_satisfaction.py`、`tests/test_narrative_v7_volume_proxy.py`。
- 回滚：代理权重降级，不影响主决断链。
- 依赖：PR-AA-28、30。

### PR-AA-35 LoopStructure 与多级结构套娃 K 线

- 定位：长篇续航与多周期一致性控制。
- 主要实现：单元/卷/全书多周期循环定义；一级爽点、卷级期待、全书主题同向性检查。
- 文件落点：`loop_structure.py`。
- AC：支持三重循环（看点/人物/套路）；支持多级 K 线共振分析。
- 测试：`tests/test_narrative_v7_loop_structure.py`。
- 回滚：关闭多周期检查，仅保留章节级检查。
- 依赖：PR-AA-28、34。

### PR-AA-36 OutlineBacktest 与 DeadlockRouter

- 定位：写前回测 + 写中死锁破局。
- 主要实现：死锁判定（连续 3 章 `T2_slope<0.05 & T4<0.2 & P3<0.4`）；四级破局路由。
- 文件落点：`outline_backtest.py`、`deadlock_router.py`。
- AC：策略 1~3 自动执行；策略 4 作者确认；`deadlock_log` 完整记录触发快照与恢复结果。
- 测试：`tests/test_narrative_v7_deadlock_router.py`。
- 回滚：关闭自动路由，仅提示人工处理。
- 依赖：PR-AA-30、33。

### PR-AA-37 AntagonistPressure、ConflictLayer 与 Anti-Pattern 风控

- 定位：高风险叙事退化防线。
- 主要实现：T9 反派压迫指数、W5 三层冲突覆盖、反模式注册表（WARNING/ERROR/CRITICAL）。
- 文件落点：`antipattern_registry.py`、`antagonist_pressure.py`、`conflict_layer.py`。
- AC：CRITICAL 与硬性干预联动；5 章内 T9 跌幅超阈值触发降智预警。
- 测试：`tests/test_narrative_v7_antipattern_guard.py`、`tests/test_narrative_v7_antagonist_pressure.py`。
- 回滚：降级为 WARNING-only，不执行硬阻断。
- 依赖：PR-AA-28、29、30。

### PR-AA-38 PacingInformationFlow 节奏与信息分配控制器

- 定位：控制“快节奏爽点”与“长篇叙事深度”的平衡。
- 主要实现：铺垫/高潮比、三段给料、信息差分配、高潮后缓冲带检测。
- 文件落点：`pacing_controller.py`。
- AC：输出急涨/急跌/横盘/过热/回撤修复建议，并能追踪采纳后效果。
- 测试：`tests/test_narrative_v7_pacing_controller.py`。
- 回滚：关闭节奏约束，只保留可视化报告。
- 依赖：PR-AA-28、35。

### PR-AA-39 BenchmarkLibrary 拆书素材库与指标资产管理

- 定位：V7 长期护城河资产层。
- 主要实现：榜单样本、标题/简介/开篇、情绪内核、循环模板、反派模板入库；指标资产版本化。
- 文件落点：`benchmark_library.py`、`benchmark_store.py`。
- AC：每次拆解必须新增或修正至少 1 个可计算参数；支持版本回放与审计导出。
- 测试：`tests/test_narrative_v7_benchmark_library.py`。
- 回滚：冻结新入库，仅使用最后稳定版本。
- 依赖：PR-AA-27、28、31。

## 7. 验收门禁与证据模板（全 PR 通用）

- 单测门禁：受影响模块单测 100% 通过，不允许 `skip/xfail` 代替。
- 集成门禁：`/api/narrative/v7/*` 关键路由集成测试通过。
- 基线门禁：`v1/v2/v3/v6` 回归通过，证明默认路径不退化。
- 离线评估门禁：至少 1 个核心效果指标 + 1 个守护指标（稳定性/耗时/误判率）。
- 回滚门禁：feature flag 关闭、配置回切、模块回退路径都必须演练并记录。
- 文档门禁：`MASTER_ROADMAP.md`、`PROJECT_STATUS.md`、V7 任务板同批更新。

## 8. 风险与应对

- 编号冲突风险：统一以 PR-AA-26~39 执行，保留 Claude 映射字段。
- LLM 评判成本风险：限制 judge 指标数量与 token，上报独立成本指标。
- 误报阻断风险：开篇门禁、反模式、死锁均提供 override 且留审计日志。
- 风味漂移风险：A6 走廊在建书后冻结，阈值更新只允许走基准库版本变更。
- 资产污染风险：拆书入库必须 schema 校验、唯一约束、可撤回。

## 9. 本计划的执行顺序（一句话）

先建“状态与指标底盘”（26~30），再建“强门禁与风控路由”（32/33/36/37），再补“商业一致性与节奏情绪增强”（31/34/35/38），最后做“基准资产化闭环”（39）。
