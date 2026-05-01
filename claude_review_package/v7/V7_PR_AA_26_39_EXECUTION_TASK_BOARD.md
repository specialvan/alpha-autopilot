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

## 生产化增强清单（第八轮）

- [x] 维护报告聚合能力（audit + health + recommendations）
- [x] 维护报告接口：`GET /api/narrative/v7/benchmark/maintenance/report`
- [x] 输出 severity 分级（ok/warn/critical）与建议动作
- [x] 第八轮回归测试覆盖（maintenance report store/api）

## 生产化增强清单（第九轮）

- [x] 一键治理能力：`auto-remediate`（health -> repair -> prune）
- [x] 一键治理接口：`POST /api/narrative/v7/benchmark/versions/auto-remediate`
- [x] 支持 dry_run + keep_last 策略联动
- [x] 输出治理前后健康快照与步骤执行结果
- [x] 第九轮回归测试覆盖（auto-remediate store/api）

## 生产化增强清单（第十轮）

- [x] SLA 阈值治理（failed/malformed/unverified/version count）支持环境变量配置
- [x] 告警摘要能力：`build_maintenance_alert`
- [x] 告警接口：`GET /api/narrative/v7/benchmark/maintenance/alert`
- [x] 输出告警级别与动作建议（`level` / `should_page` / `should_ticket` / `breaches`）
- [x] 第十轮回归测试覆盖（maintenance alert store/api）

## 生产化增强清单（第十一轮）

- [x] 告警事件持久化能力：`emit_maintenance_alert`
- [x] 告警事件历史查询能力：`list_maintenance_alerts`
- [x] 告警事件日志落盘：`_maintenance_alerts.jsonl`
- [x] 告警事件写入接口：`POST /api/narrative/v7/benchmark/maintenance/alert/emit`
- [x] 告警事件列表接口：`GET /api/narrative/v7/benchmark/maintenance/alerts`
- [x] 第十一轮回归测试覆盖（maintenance alert emit/list store/api）

## 生产化增强清单（第十二轮）

- [x] 告警日志生命周期治理：`prune_maintenance_alerts`
- [x] 告警日志清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/prune`
- [x] 支持 `dry_run` 预演（候选统计，不落盘删除）
- [x] 支持 `keep_last` 保留最近 N 条告警事件
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 第十二轮回归测试覆盖（maintenance alert prune store/api）

## 生产化增强清单（第十三轮）

- [x] 告警事件摘要聚合能力：`summarize_maintenance_alerts`
- [x] 告警摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/summary`
- [x] 输出窗口统计（`ok/warn/critical`）与动作统计（`page/ticket/breach`）
- [x] 输出 `latest_event`、`total_valid_events`、`malformed_line_count`
- [x] 支持 `limit` 聚合窗口，便于运维看板按窗口消费
- [x] 第十三轮回归测试覆盖（maintenance alert summary store/api）

## 生产化增强清单（第十四轮）

- [x] 告警 Digest 能力：`build_maintenance_alert_digest`
- [x] 告警 Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/digest`
- [x] 聚合输出：实时告警 + 历史摘要 + 告警新鲜度（stale）
- [x] 支持 `AA_V7_BENCH_ALERT_STALE_SECONDS` 告警新鲜度阈值
- [x] 输出推荐动作（`page_oncall/create_ticket/emit_fresh_alert/observe/clean_alert_log`）
- [x] 第十四轮回归测试覆盖（maintenance alert digest store/api）

## 生产化增强清单（第十五轮）

- [x] 告警导出能力：`export_maintenance_alerts`
- [x] 告警导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/export`
- [x] 导出结构：`digest + recent alerts`（单请求获取验收所需核心上下文）
- [x] 支持 `limit` 导出窗口，便于评审脚本/看板集成
- [x] 第十五轮回归测试覆盖（maintenance alert export store/api）

## 生产化增强清单（第十六轮）

- [x] 告警日志分页治理：`list_maintenance_alerts(limit, cursor)`
- [x] 告警列表接口升级：`GET /api/narrative/v7/benchmark/maintenance/alerts` 支持 `cursor`
- [x] 告警导出接口升级：`GET /api/narrative/v7/benchmark/maintenance/alerts/export` 支持 `cursor`
- [x] 告警归档分片能力：`archive_maintenance_alerts(keep_last, shard_size, dry_run)`
- [x] 告警归档接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/archive`
- [x] 归档输出 `archive_files / archive_shard_count / malformed_dropped_count` 等治理指标
- [x] 第十六轮回归测试覆盖（alert pagination + archive shard store/api）

## 生产化增强清单（第十七轮）

- [x] 归档分片索引能力：`list_maintenance_alert_archive_files`
- [x] 归档文件列表接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/archive/files`
- [x] 归档文件读取能力：`read_maintenance_alert_archive_file(file_name, limit, cursor)`
- [x] 归档文件读取接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/archive/read`
- [x] 归档读取支持分页治理（`cursor/next_cursor/has_more`）
- [x] 归档读取支持文件名安全约束（防路径穿越）
- [x] 第十七轮回归测试覆盖（archive files/read store/api）

## 生产化增强清单（第十八轮）

- [x] 告警自动归档策略能力：`auto_archive_maintenance_alerts`
- [x] 告警自动归档接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/auto-archive`
- [x] 环境变量策略治理：`AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT/KEEP_LAST/SHARD_SIZE`
- [x] 自动归档支持 `dry_run/apply` 双路径
- [x] 自动归档响应输出 `should_archive` 与 `archive` 明细，便于运维联动
- [x] 第十八轮回归测试覆盖（alert auto-archive store/api）

## 生产化增强清单（第十九轮）

- [x] 归档清理策略能力：`cleanup_maintenance_alert_archives`
- [x] 归档清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/archive/cleanup`
- [x] 环境变量清理治理：`AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS / AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES`
- [x] 清理策略支持 `dry_run/apply` 双路径
- [x] 清理输出 `candidate_count / removed_count / ttl_candidate_count / max_shard_candidate_count`
- [x] 第十九轮回归测试覆盖（archive cleanup policy store/api）

## 生产化增强清单（第二十轮）

- [x] 告警治理报告能力：`build_maintenance_alert_governance_report`
- [x] 治理报告接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/report`
- [x] 一键治理汇总能力：`run_maintenance_alert_governance`
- [x] 一键治理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run`
- [x] 输出策略快照 + 执行前后快照 + 步骤执行轨迹（`performed_steps`）
- [x] 第20轮回归测试覆盖（governance report/run store/api）

## 生产化增强清单（第二十一轮）

- [x] 治理执行幂等保护：`idempotency_key` + request fingerprint
- [x] 幂等复用语义：相同 key+同请求直接复用历史成功结果（不重复执行）
- [x] 幂等冲突语义：相同 key+不同请求返回冲突（409）
- [x] 治理运行失败记录：status/error_type/error_message/attempt 落盘
- [x] 治理重试语义：`retry_run_id` 仅允许针对 failed 记录重试并递增 attempt
- [x] 治理运行历史查询：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs`
- [x] 治理运行接口升级：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/run` 支持 `idempotency_key/retry_run_id`
- [x] 第21轮回归测试覆盖（governance idempotency + failure/retry history store/api）

## 生产化增强清单（第二十二轮）

- [x] 治理运行日志生命周期治理：`prune_maintenance_alert_governance_runs`
- [x] 治理运行日志清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条治理运行记录
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 运行日志排序稳定性增强（`generated_at/completed_at/run_id` 多键排序）
- [x] 第22轮回归测试覆盖（governance runs prune store/api）

## 生产化增强清单（第二十三轮）

- [x] 治理运行历史摘要能力：`summarize_maintenance_alert_governance_runs`
- [x] 治理运行摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/summary`
- [x] 摘要输出窗口统计（`succeeded_count / failed_count`）与脏行计数
- [x] 摘要输出 `latest_run` 与 `latest_failed_run`，便于值班排障
- [x] 第23轮回归测试覆盖（governance runs summary store/api）

## 生产化增强清单（第二十四轮）

- [x] 治理运行导出能力：`export_maintenance_alert_governance_runs`
- [x] 治理运行导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/export`
- [x] 导出结构：`summary + paged records`（单请求拉取评审与运维所需上下文）
- [x] 支持 `limit/cursor` 分页导出，兼容长窗口治理日志消费
- [x] 第24轮回归测试覆盖（governance runs export store/api）

## 生产化增强清单（第二十五轮）

- [x] 治理运行日志自动清理策略：`auto_prune_maintenance_alert_governance_runs`
- [x] 自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 第25轮回归测试覆盖（governance runs auto-prune store/api）

## 生产化增强清单（第二十六轮）

- [x] 治理运行健康 Digest 能力：`build_maintenance_alert_governance_runs_digest`
- [x] 治理运行 Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/digest`
- [x] 支持新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_RUNS_STALE_SECONDS`
- [x] 输出推荐动作（`retry_latest_failed_run/auto_prune_runs/execute_governance_run/observe`）
- [x] 第26轮回归测试覆盖（governance runs digest store/api）

## 生产化增强清单（第二十七轮）

- [x] 治理运行一键自愈能力：`auto_remediate_maintenance_alert_governance_runs`
- [x] 一键自愈接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/auto-remediate`
- [x] 自愈策略基于 digest 推荐动作执行（失败优先重试）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 第27轮回归测试覆盖（governance runs auto-remediate store/api）

## 生产化增强清单（第二十八轮）

- [x] 治理运行重试上限策略：`AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS`
- [x] 重试上限门禁：超过最大 attempt 返回 `retry_attempt_limit_exceeded`
- [x] 治理运行 Digest 升级动作：`escalate_failed_run`
- [x] Digest 输出重试预算字段：`retry_max_attempts/latest_failed_attempt/retry_exhausted`
- [x] auto-remediate 升级联动输出：`escalation_required/escalation_reason`
- [x] 路由错误码映射：重试超限返回 `422`
- [x] 第28轮回归测试覆盖（retry limit + escalation digest/remediate store/api）

## 生产化增强清单（第二十九轮）

- [x] 治理运行连续失败升级阈值策略：`AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK`
- [x] 治理运行摘要新增连续失败计数：`consecutive_failed_runs`
- [x] 治理运行 Digest 新增失败熔断字段：`escalation_failure_streak_limit/failure_streak_exhausted`
- [x] 失败升级动作增强：连续失败超阈值触发 `escalate_failed_run`（`consecutive_failure_streak_exhausted`）
- [x] auto-remediate 升级原因增强：`consecutive_failures_{n}_reached_limit_{limit}`
- [x] 第29轮回归测试覆盖（failure streak escalation digest/remediate store/api）

## 生产化增强清单（第三十轮）

- [x] 治理升级事件落盘能力：`emit_maintenance_alert_governance_escalation`
- [x] 治理升级事件分页查询能力：`list_maintenance_alert_governance_escalations`
- [x] 新增升级事件日志文件：`_maintenance_alert_governance_escalations.jsonl`
- [x] auto-remediate 升级路径自动发射 escalation event（`source=auto_remediate`）
- [x] 新增升级事件 API：`POST /governance/runs/escalation/emit`、`GET /governance/runs/escalations`
- [x] 第30轮回归测试覆盖（escalation emit/list + auto-remediate event store/api）

## 生产化增强清单（第三十一轮）

- [x] 治理升级事件摘要能力：`summarize_maintenance_alert_governance_escalations`
- [x] 治理升级事件导出能力：`export_maintenance_alert_governance_escalations`
- [x] 摘要输出 source/触发类型统计（`manual_emit/auto_remediate/retry_exhausted/failure_streak_exhausted`）
- [x] 新增升级事件摘要 API：`GET /governance/runs/escalations/summary`
- [x] 新增升级事件导出 API：`GET /governance/runs/escalations/export`
- [x] 升级事件排序稳定性增强（同秒事件稳定排序）
- [x] 第31轮回归测试覆盖（escalation summary/export store/api）

## 生产化增强清单（第三十二轮）

- [x] 治理升级事件日志生命周期治理：`prune_maintenance_alert_governance_escalations`
- [x] 治理升级事件清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条升级事件
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 第32轮回归测试覆盖（governance escalations prune store/api）

## 生产化增强清单（第三十三轮）

- [x] 治理升级事件日志自动清理策略：`auto_prune_maintenance_alert_governance_escalations`
- [x] 自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 第33轮回归测试覆盖（governance escalations auto-prune store/api）

## 生产化增强清单（第三十四轮）

- [x] 治理升级事件 Digest 能力：`build_maintenance_alert_governance_escalations_digest`
- [x] 治理升级事件 Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`
- [x] 支持升级事件新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS`
- [x] Digest 联动 runs-digest 推荐动作输出（`emit_escalation/auto_prune_escalations/observe`）
- [x] 输出 `summary + run_digest` 聚合上下文，便于值班单请求验收
- [x] 第34轮回归测试覆盖（governance escalations digest store/api）

## 生产化增强清单（第三十五轮）

- [x] 治理升级事件一键自愈能力：`auto_remediate_maintenance_alert_governance_escalations`
- [x] 一键自愈接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`
- [x] 自愈策略基于 escalation digest 推荐动作执行（`emit_escalation/auto_prune_escalations`）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 输出执行细节（`emitted/pruned/emitted_event/auto_prune`）便于值班审计
- [x] 第35轮回归测试覆盖（governance escalations auto-remediate store/api）

## 生产化增强清单（第三十六轮）

- [x] 治理升级事件发射冷却策略（cooldown）与重复防抖
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATIONS_EMIT_COOLDOWN_SECONDS`
- [x] 升级发射接口支持冷却旁路参数：`ignore_cooldown`
- [x] 发射响应新增抑制审计字段（`suppressed/suppression_reason/suppressed_by_event_id/cooldown_seconds`）
- [x] 防止同源同签名升级事件在冷却窗口内重复写入，降低告警风暴风险
- [x] 第36轮回归测试覆盖（governance escalation emit cooldown store/api）

## 生产化增强清单（第三十七轮）

- [x] 治理升级事件自愈运行历史落盘能力（remediation runs）
- [x] 自愈历史查询接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations`
- [x] 运行历史输出字段：`action/executed/emitted/pruned/emitted_event_id/auto_prune_*`
- [x] 支持 `limit/cursor` 分页消费与脏行计数（`malformed_line_count`）
- [x] 将 dry-run 与 apply 执行轨迹统一纳入审计闭环
- [x] 第37轮回归测试覆盖（governance escalations auto-remediation history store/api）

## 生产化增强清单（第三十八轮）

- [x] 治理升级事件自愈历史摘要能力：`summarize_maintenance_alert_governance_escalation_remediations`
- [x] 自愈历史摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/summary`
- [x] 治理升级事件自愈历史导出能力：`export_maintenance_alert_governance_escalation_remediations`
- [x] 自愈历史导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export`
- [x] 摘要输出窗口统计（`dry_run/apply/executed/emitted/pruned`）与 `latest_record`，并保留脏行计数
- [x] 导出支持 `limit/cursor` 分页，输出 `summary + records` 单请求验收上下文
- [x] 第38轮回归测试覆盖（governance escalation auto-remediation summary/export store/api）

## 生产化增强清单（第三十九轮）

- [x] 治理升级事件自愈历史日志清理能力：`prune_maintenance_alert_governance_escalation_remediations`
- [x] 自愈历史清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条自愈历史记录
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 清理后历史可回读校验（记录数量与排序保持稳定）
- [x] 第39轮回归测试覆盖（governance escalation auto-remediation prune store/api）

## 生产化增强清单（第四十轮）

- [x] 治理升级事件自愈历史自动清理策略：`auto_prune_maintenance_alert_governance_escalation_remediations`
- [x] 自愈历史自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 支持脏行触发清理与清理后回读校验（`malformed_line_count -> 0`）
- [x] 第40轮回归测试覆盖（governance escalation auto-remediation auto-prune store/api）

## 生产化增强清单（第四十一轮）

- [x] 治理升级事件自愈历史 Digest 能力：`build_maintenance_alert_governance_escalation_remediations_digest`
- [x] 自愈历史 Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest`
- [x] 支持自愈历史新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS`
- [x] Digest 联动自愈历史清理阈值策略（`above_prune_threshold` / `malformed_detected`）
- [x] 输出推荐动作（`run_auto_remediate_escalations/auto_prune_remediations/observe`）
- [x] 第41轮回归测试覆盖（governance escalation auto-remediation digest store/api）

## 生产化增强清单（第四十二轮）

- [x] 治理升级事件自愈历史一键自愈编排能力：`auto_remediate_maintenance_alert_governance_escalation_remediations`
- [x] 自愈历史编排接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate`
- [x] 编排策略基于 remediation digest 推荐动作执行（`run_auto_remediate_escalations/auto_prune_remediations/observe`）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 输出执行细节（`remediated_escalations/pruned_remediation_history/escalation_auto_remediate/remediation_auto_prune`）
- [x] 第42轮回归测试覆盖（governance escalation auto-remediation orchestrator store/api）

## 生产化增强清单（第四十三轮）

- [x] 治理升级事件自愈历史编排运行记录落盘能力（orchestrator runs）
- [x] 编排运行历史查询接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs`
- [x] 历史字段输出：`action/executed/remediated_escalations/pruned_remediation_history/digest_before_message/digest_after_message`
- [x] 支持 `limit/cursor` 分页消费与脏行计数（`malformed_line_count`）
- [x] 将 dry-run 与 apply 编排轨迹统一纳入审计闭环
- [x] 第43轮回归测试覆盖（governance escalation auto-remediation orchestrator runs store/api）

## 生产化增强清单（第四十四轮）

- [x] 编排运行历史摘要能力：`summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs`
- [x] 编排运行历史摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/summary`
- [x] 编排运行历史导出能力：`export_maintenance_alert_governance_escalation_remediation_auto_remediate_runs`
- [x] 编排运行历史导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/export`
- [x] 摘要输出窗口统计（`dry_run/apply/executed/remediated/pruned`）与 `latest_record`，并保留脏行计数
- [x] 导出支持 `limit/cursor` 分页，输出 `summary + records` 单请求验收上下文
- [x] 第44轮回归测试覆盖（orchestrator runs summary/export store/api）

## 生产化增强清单（第四十五轮）

- [x] 编排运行历史日志清理能力：`prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs`
- [x] 编排运行历史清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条编排运行记录
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 清理后历史可回读校验（记录数量与排序保持稳定）
- [x] 第45轮回归测试覆盖（orchestrator runs prune store/api）

## 生产化增强清单（第四十六轮）

- [x] 编排运行历史自动清理策略：`auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs`
- [x] 编排运行历史自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 支持脏行触发清理与清理后回读校验（`malformed_line_count -> 0`）
- [x] 第46轮回归测试覆盖（orchestrator runs auto-prune store/api）

## 生产化增强清单（第四十七轮）

- [x] 编排运行历史 Digest 能力：`build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest`
- [x] 编排运行历史 Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/digest`
- [x] 支持编排运行新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_STALE_SECONDS`
- [x] Digest 联动编排运行清理阈值策略（`above_prune_threshold` / `malformed_detected`）
- [x] 输出推荐动作（`run_auto_remediation_orchestrator/auto_prune_runs/observe`）
- [x] 第47轮回归测试覆盖（orchestrator runs digest store/api）

## 生产化增强清单（第四十八轮）

- [x] 编排运行历史一键自愈编排能力：`auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs`
- [x] 编排运行历史一键自愈接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate`
- [x] 编排策略基于 runs-digest 推荐动作执行（`run_auto_remediation_orchestrator/auto_prune_runs/observe`）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 输出执行细节（`remediated_orchestrator/pruned_run_history/orchestrator_auto_remediate/run_history_auto_prune`）
- [x] 第48轮回归测试覆盖（orchestrator runs auto-remediate store/api）

## 生产化增强清单（第四十九轮）

- [x] 编排运行历史自愈执行轨迹落盘能力（auto-remediate runs history）
- [x] 轨迹查询接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs`
- [x] 轨迹字段输出：`action/executed/remediated_orchestrator/pruned_run_history/digest_before_message/digest_after_message`
- [x] 支持 `limit/cursor` 分页消费与脏行计数（`malformed_line_count`）
- [x] 将 apply 执行轨迹纳入审计闭环并支持异常行容错读取
- [x] 治理运行同时间戳排序稳定性增强：`attempt` 作为 runs 排序补充键，避免最新失败 attempt 漂移
- [x] 第49轮回归测试覆盖（orchestrator-runs auto-remediate run-history store/api）

## 生产化增强清单（第五十轮）

- [x] 编排运行历史自愈执行轨迹摘要能力（auto-remediate runs history summary）
- [x] 摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/summary`
- [x] 编排运行历史自愈执行轨迹导出能力（auto-remediate runs history export）
- [x] 导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/export`
- [x] 摘要输出窗口统计（`dry_run/apply/executed/remediated_orchestrator/pruned_run_history`）与 `latest_record`，并保留脏行计数
- [x] 导出支持 `limit/cursor` 分页，输出 `summary + records` 单请求验收上下文
- [x] 第50轮回归测试覆盖（orchestrator-runs auto-remediate run-history summary/export store/api）

## 生产化增强清单（第五十一轮）

- [x] 编排运行历史自愈执行轨迹日志清理能力（auto-remediate runs history prune）
- [x] 清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条编排执行轨迹
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 清理后历史可回读校验（记录数量与排序保持稳定）
- [x] 第51轮回归测试覆盖（orchestrator-runs auto-remediate run-history prune store/api）

## 生产化增强清单（第五十二轮）

- [x] 编排执行轨迹历史自动清理策略（auto-prune）能力：`auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs`
- [x] 自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 支持脏行触发清理与清理后回读校验（`malformed_line_count -> 0`）
- [x] 第52轮回归测试覆盖（orchestrator-runs auto-remediate run-history auto-prune store/api）

## 生产化增强清单（第五十三轮）

- [x] 编排执行轨迹历史 Digest 能力：`build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_digest`
- [x] Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/digest`
- [x] 支持编排执行轨迹新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_STALE_SECONDS`
- [x] Digest 联动执行轨迹清理阈值策略（`above_prune_threshold` / `malformed_detected`）
- [x] 输出推荐动作（`run_auto_remediation_orchestrator_runs/auto_prune_runs/observe`）
- [x] 第53轮回归测试覆盖（orchestrator-runs auto-remediate run-history digest store/api）

## 生产化增强清单（第五十四轮）

- [x] 编排执行轨迹历史一键自愈能力：`auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs`
- [x] 一键自愈接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate`
- [x] 自愈策略基于 run-history digest 推荐动作执行（`run_auto_remediation_orchestrator_runs/auto_prune_runs/observe`）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 输出执行细节（`remediated_orchestrator_runs/pruned_run_history/orchestrator_runs_auto_remediate/run_history_auto_prune`）
- [x] 第54轮回归测试覆盖（orchestrator-runs auto-remediate run-history auto-remediate store/api）

## 生产化增强清单（第五十五轮）

- [x] 编排执行轨迹自愈执行历史落盘能力（auto-remediate runs history）
- [x] 执行历史查询接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs`
- [x] 执行历史字段输出：`action/executed/remediated_orchestrator_runs/pruned_run_history/digest_before_message/digest_after_message`
- [x] 支持 `limit/cursor` 分页消费与脏行计数（`malformed_line_count`）
- [x] 将 dry-run 与 apply 执行轨迹统一纳入审计闭环
- [x] 第55轮回归测试覆盖（orchestrator-runs auto-remediate run-history auto-remediate-runs history store/api）

## 生产化增强清单（第五十六轮）

- [x] 编排执行轨迹自愈执行历史摘要能力（auto-remediate-runs history summary）
- [x] 摘要接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/summary`
- [x] 编排执行轨迹自愈执行历史导出能力（auto-remediate-runs history export）
- [x] 导出接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/export`
- [x] 摘要输出窗口统计（`dry_run/apply/executed/remediated_orchestrator_runs/pruned_run_history`）与 `latest_record`，并保留脏行计数
- [x] 导出支持 `limit/cursor` 分页，输出 `summary + records` 单请求验收上下文
- [x] 第56轮回归测试覆盖（orchestrator-runs auto-remediate-runs history summary/export store/api）

## 生产化增强清单（第五十七轮）

- [x] 编排执行轨迹自愈执行历史日志清理能力（auto-remediate-runs history prune）
- [x] 清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/prune`
- [x] 支持 `dry_run/apply` 双路径（预演/执行）
- [x] 支持 `keep_last` 保留最近 N 条执行轨迹
- [x] 支持脏行统计与清理（`malformed_candidate_count / malformed_dropped_count`）
- [x] 清理后历史可回读校验（记录数量与排序保持稳定）
- [x] 第57轮回归测试覆盖（orchestrator-runs auto-remediate-runs history prune store/api）

## 生产化增强清单（第五十八轮）

- [x] 编排执行轨迹自愈执行历史自动清理策略（auto-prune）能力：`auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs`
- [x] 自动清理接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-prune`
- [x] 环境变量策略治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT/KEEP_LAST`
- [x] 自动清理支持 `dry_run/apply` 双路径
- [x] 自动清理输出 `should_prune` 与 `prune` 明细，便于值班联动
- [x] 支持脏行触发清理与清理后回读校验（`malformed_line_count -> 0`）
- [x] 第58轮回归测试覆盖（orchestrator-runs auto-remediate-runs history auto-prune store/api）

## 生产化增强清单（第五十九轮）

- [x] 编排执行轨迹自愈执行历史 Digest 能力：`build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_digest`
- [x] Digest 接口：`GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/digest`
- [x] 支持执行历史新鲜度阈值治理：`AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_AUTO_REMEDIATE_RUNS_STALE_SECONDS`
- [x] Digest 联动执行历史清理阈值策略（`above_prune_threshold` / `malformed_detected`）
- [x] 输出推荐动作（`run_auto_remediation_orchestrator_runs_auto_remediate_runs/auto_prune_runs/observe`）
- [x] 第59轮回归测试覆盖（orchestrator-runs auto-remediate-runs history digest store/api）

## 生产化增强清单（第六十轮）

- [x] 编排执行轨迹自愈执行历史一键自愈能力：`auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs`
- [x] 一键自愈接口：`POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate`
- [x] 自愈策略基于执行历史 digest 推荐动作执行（`run_auto_remediation_orchestrator_runs_auto_remediate_runs/auto_prune_runs/observe`）
- [x] 支持 `dry_run/apply` 双路径，并输出 `digest_before/digest_after`
- [x] 输出执行细节（`remediated_orchestrator_runs_auto_remediate_runs/pruned_run_history/orchestrator_runs_auto_remediate_runs_auto_remediate/run_history_auto_prune`）
- [x] 第60轮回归测试覆盖（orchestrator-runs auto-remediate-runs history auto-remediate store/api）

## 后续验收文档清单（提交 Claude 评审）

- [x] `V7_CLAUDE_REVIEW_ACCEPTANCE_SUBMISSION.md`（本次新增）
- [x] `V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`（已存在）
- [x] `V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`（本文件）
- [x] `CODEX_V7_GOVERNANCE_PACKAGE/*`（治理包全量）

## 当前验证结果

- [x] `pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
- [x] 结果：`105 passed`
- [x] `python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`
