# V7 PR-AA-26~39 可执行任务板（Codex 执行版）

- 日期：2026-04-30
- 阶段：V7
- 执行策略：先骨架闭环，再按 PR 迭代加深
- 约束：checklist 未完成不停止

## 总览

- [x] 任务板建立并与 `V7_DEVELOPMENT_PLAN_PR_2026_04_30.md` 对齐
- [x] V7 代码目录创建：`backend/app/services/narrative_v7/`
- [x] V7 API 路由创建：`/api/narrative/v7/*`
- [x] V7 配置开关入场：`backend/app/core/config.py`
- [x] V7 单元与 API 测试补齐：`tests/test_narrative_v7_*.py`

## PR-AA-26 NarrativeMarketState 基座

- [x] `NovelProjectState` / `NarrativeMarketState` schema
- [x] `DecisionState` / `ThresholdBand` schema
- [x] 与旧 `StoryState` 的兼容输入路径（通过 dict story_state）
- [x] 单测覆盖（schema 与 API 入参）

## PR-AA-27 BenchmarkParameterSet 参数集

- [x] `BenchmarkParameterSet` schema
- [x] `V7BenchmarkStore` 入库能力
- [x] `book_id` 去重保护
- [x] 撤回样本 `retract` 能力
- [x] query 聚合均值/方差与阈值回推

## PR-AA-28 NQMSampler 与 OHLCV

- [x] `NQMSampler` 首版实现
- [x] 28+ 维指标采样输出（P/T/W/A）
- [x] `NarrativeMetricOHLCV` 输出
- [x] `/sample` API 接入
- [x] 采样基础测试覆盖

## PR-AA-29 ThresholdBand 阈值带

- [x] `ThresholdBandEngine` 实现
- [x] H/L 分区判定
- [x] 形态识别（breakdown/breakout/range）
- [x] `/thresholds/preview` API 接入

## PR-AA-30 DecisionFeedbackController

- [x] `DecisionFeedbackController` 实现
- [x] R-01~R-10 路由首版规则
- [x] `NarrativeDecision` 输出结构
- [x] `/decision` API 接入

## PR-AA-31 SellingPointContract + IPFlavor

- [x] `SellingPointContractGuard` 实现
- [x] 合同存在性与 A6 对齐检查
- [x] `/contract/evaluate` API 接入

## PR-AA-32 OpeningGate 开篇门禁

- [x] `OpeningGate` 实现
- [x] T8 评分实现
- [x] 十大毒点检测实现
- [x] override 日志标记实现
- [x] `/opening-gate` API 接入

## PR-AA-33 ExpectationDebt 章末钩子守卫

- [x] `ExpectationDebtManager` 实现
- [x] T4 章末钩子密度检查
- [x] 三类钩子建议生成
- [x] `/hook-guard` API 接入

## PR-AA-34 EmotionSatisfaction

- [x] `EmotionSatisfactionScorer` 实现
- [x] 情绪维度分解评分
- [x] volume 代理值计算
- [x] `/emotion/score` API 接入

## PR-AA-35 LoopStructure

- [x] `LoopStructureAnalyzer` 实现
- [x] 多单元趋势分析
- [x] 循环标签健康建议
- [x] `/loop/analyze` API 接入

## PR-AA-36 DeadlockRouter

- [x] `DeadlockRouter` 实现
- [x] 连续三章死锁判定（T2/T4/P3）
- [x] 策略路由选择实现
- [x] `/deadlock/check` API 接入

## PR-AA-37 Anti-Pattern 风控

- [x] `AntiPatternRegistry` 实现
- [x] WARNING/ERROR/CRITICAL 分级
- [x] 反派降智/POV/逻辑崩坏等首版规则
- [x] `/antipattern/check` API 接入

## PR-AA-38 PacingInformationFlow

- [x] `PacingInformationFlowController` 实现
- [x] overheat/dragging/volatile 判定
- [x] 节奏修复建议输出
- [x] `/pacing/evaluate` API 接入

## PR-AA-39 BenchmarkLibrary 资产层

- [x] `BenchmarkLibrary` 门面实现
- [x] ingest/query/retract 统一接口
- [x] benchmark API 全链打通

## 代码与测试交付清单

- [x] `backend/app/services/narrative_v7/` 全模块骨架
- [x] `backend/app/api/routes/narrative_v7.py`
- [x] `backend/app/main.py` 路由接入
- [x] `backend/app/core/config.py` V7 配置项
- [x] `tests/test_narrative_v7_modules.py`
- [x] `tests/test_narrative_v7_api.py`

## 后续验收文档清单（提交 Claude 评审）

- [x] `V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md`（本次新增）
- [x] `V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`（已存在）
- [x] `V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`（本文件）
- [x] `CODEX_V7_GOVERNANCE_PACKAGE/*`（治理包全量）
