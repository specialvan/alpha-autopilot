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
- [x] V7 生产化增强（feature flag 生效、异常处理、运行观测、benchmark 原子写）

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

## 生产化增强清单（第二轮）

- [x] 全局开关 `v7_enabled` 在路由层生效
- [x] 分项开关 `v7_opening_gate_enabled / v7_antipattern_guard_enabled / v7_deadlock_router_enabled` 生效
- [x] 统一路由执行包装：错误捕获 + 延迟统计 + http 状态归档
- [x] 观测接口 `/api/narrative/v7/observability`
- [x] benchmark 入库重复冲突 409、空样本 422
- [x] benchmark 文件写入改为原子替换（temp file -> replace）
- [x] benchmark 查询新增 `corridor_ready` 与 `warnings`
- [x] 新增生产化回归测试（feature flag / observability / duplicate conflict / empty payload）

## 生产化增强清单（第三轮）

- [x] Decision 路由规则外置：`decision_rules.default.json` + `DecisionRuleSet`
- [x] Decision 控制器接入规则热加载（默认文件 + 环境变量 `AA_V7_DECISION_RULES_JSON`）
- [x] 新增规则可视化接口：`GET /api/narrative/v7/decision/rules`
- [x] Benchmark 版本快照落盘（每次 ingest/retract/restore 记录可回放快照）
- [x] Benchmark 版本列表接口：`GET /api/narrative/v7/benchmark/versions`
- [x] Benchmark 版本恢复接口：`POST /api/narrative/v7/benchmark/restore/{version}`
- [x] observability 阈值支持环境变量覆写
- [x] observability 输出新增 `thresholds` 字段
- [x] 第三轮回归测试覆盖（rules/versions/restore/threshold snapshot）

## 生产化增强清单（第四轮）

- [x] Benchmark 快照增加完整性摘要 `rows_sha256`（防篡改审计）
- [x] Benchmark 版本记录增加 `integrity_status`（verified/unverified/failed）
- [x] restore 增加完整性校验失败拦截（tampered snapshot 拒绝恢复）
- [x] restore 增加恢复前备份版本 `backup_version`（可回滚保护）
- [x] Benchmark 版本差异对比能力（added/removed/activated/deactivated/mean_changed）
- [x] 差异接口：`GET /api/narrative/v7/benchmark/versions/diff`
- [x] 审计导出接口：`GET /api/narrative/v7/benchmark/audit/export`
- [x] 第四轮回归测试覆盖（diff/audit/integrity/restore-guard）

## 生产化增强清单（第五轮）

- [x] 版本生命周期治理：支持版本保留策略与清理
- [x] 版本清理接口：`POST /api/narrative/v7/benchmark/versions/prune`
- [x] 支持 `dry_run` 预演（先看候选，不执行删除）
- [x] 支持 `keep_last` 保留最近 N 个版本
- [x] 清理响应输出 kept/candidate/pruned 统计与版本列表
- [x] 第五轮回归测试覆盖（prune store/api）

## 生产化增强清单（第六轮）

- [x] 版本仓健康扫描能力（integrity + malformed 检测）
- [x] 健康扫描接口：`GET /api/narrative/v7/benchmark/versions/health`
- [x] 输出 failed_integrity / malformed 文件清单与计数
- [x] 第六轮回归测试覆盖（health scan store/api）

## 生产化增强清单（第七轮）

- [x] 版本仓自修复能力（repair）支持 failed/malformed 隔离
- [x] 自修复接口：`POST /api/narrative/v7/benchmark/versions/repair`
- [x] 支持 `dry_run` 预演与隔离目录输出
- [x] 输出 moved/candidate 统计与文件列表
- [x] 第七轮回归测试覆盖（repair store/api）

## 后续验收文档清单（提交 Claude 评审）

- [x] `V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md`（本次新增）
- [x] `V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`（已存在）
- [x] `V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`（本文件）
- [x] `CODEX_V7_GOVERNANCE_PACKAGE/*`（治理包全量）

## 当前验证结果

- [x] `pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
- [x] 结果：`30 passed`
- [x] `python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`
