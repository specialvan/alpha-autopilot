# V6 开发验收清单（PR-AA-09 ~ PR-AA-15）

## 0. 使用方式

- 该清单用于 V6 开发验收与评审门禁。
- 需求基线：`claude_review_package/V6/V6_MIROFISH_PR_REQUIREMENTS.md`
- 任务执行基线：`claude_review_package/V6/V6_IMPLEMENTATION_TASK_BOARD.md`

## 1. 全局门禁（必须通过）

- [x] 分层合规：变更停留在 `Increment`，未污染 Baseline 默认行为
- [x] V6 能力可关闭/可降级/可回滚
- [x] 所有 LLM 路径有 deterministic/mock fallback
- [x] 主链路失败隔离：单路径失败不拖垮整次模拟
- [x] 写入 Story Bible 的动作均需人工确认
- [x] 文档、测试、状态证据一致
- [x] simulation 状态支持持久化回放（默认 JSONL 存储）
- [x] simulation 持久化支持按行/按体积轮转与分桶归档回放
- [x] V6 runtime 指标支持 `P95/error/fallback` 阈值告警与快照查询
- [x] GraphRAG 检索支持 deterministic fallback 且可注入 simulation/interview 证据链
- [x] GraphRAG 检索支持跨会话 history stitching，返回 `history_recall_used` 与 `stitched_from_history_count` 可审计字段
- [x] cross-session graph memory 支持 TTL、章节窗口与来源权重可配置策略（防止无限记忆污染）
- [x] graph memory 支持语义漂移阈值过滤与可调用 compaction 维护入口
- [x] graph memory 支持只读 audit snapshot，输出规模、来源、类型、章节范围与策略摘要
- [x] graph memory audit snapshot 支持 JSONL 持久化与历史读取
- [x] graph memory audit history 支持趋势告警（expired rate、duplicate groups、active row drop）

## 2. PR-AA-09 验收项（P0）

- [x] `NarrativeSeed` schema 字段完整（characters/relationship/world_rules/plot_events/open_threads）
- [x] long text 分块抽取与合并可用
- [x] `relationship_triples` 可转换为 RelationshipGraph 兼容边
- [x] `needs_review` 收纳低置信度字段
- [x] 无真实 LLM 环境可通过 deterministic 测试

## 3. PR-AA-10 验收项（P0）

- [x] 可从 `NarrativeSeed` 生成合法 `ParameterizedCharacterProfile`
- [x] slider 范围与 function_type 枚举合法
- [x] 声线/欲望/触发条件含 evidence
- [x] author override 优先生效且保留日志
- [x] 可被并行推演和角色访谈直接消费

## 4. PR-AA-11 验收项（P0）

- [x] 同一输入稳定输出 2~3 条独立路径
- [x] 每条路径拥有独立 state、评分、关系变化与风险标记
- [x] winner 默认遵循留存评分并保留解释
- [x] 单路径失败被隔离并记录
- [x] `decision_summary` 可序列化给 Workbench

## 5. PR-AA-12 验收项（P1）

- [x] K 轮交互日志完整
- [x] 至少输出 1 个冲突候选
- [x] 候选含关系/性格/压力触发解释
- [x] 未经确认不写入正式故事状态

## 6. PR-AA-13 验收项（P1）

- [x] 支持 checkpoint 注入并从中续算
- [x] 注入后评分与排序变化可对比
- [x] 宏观结构违规输出风险标记
- [x] 注入审计日志可追溯

## 7. PR-AA-14 验收项（P1）

- [x] 可选角色发起访谈并生成回答
- [x] 输出 transcript 与记忆依据
- [x] OOC 与泄密风险可标注
- [x] 默认不污染正式设定

## 8. PR-AA-15 验收项（P2）

- [x] 群体记忆影响成员行为约束
- [x] `chapter_range` 与 `hidden` 过滤生效
- [x] 传播日志与可撤销补丁可导出
- [x] RelationshipGraph 向后兼容

## 9. 回归门禁

- [x] `python scripts/run_layered_tests.py v6 api v4 frontend` 通过
- [x] V6 专项测试全通过
- [x] 关键 API 合约测试通过
- [x] `npm --prefix ui-react run build` 通过

## 10. 结论块

- [x] `GO`
- [ ] `GO WITH CONDITIONS`
- [ ] `NO-GO`

复核记录模板：

- 结论：
- 阻断项：
- 条件项：
- 验证命令：
- 证据路径：
