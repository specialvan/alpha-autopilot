# V6 验收交接包（2026-04-28）

## 1. 本轮交接目标

完成 V6 `PR-AA-09` 到 `PR-AA-15` 的后端主链路、API 契约、最小 Workbench 访谈入口与可复核测试证据，形成可直接评审的完整 V6 交付包。

## 2. 本轮完成范围

### 2.1 P0 主链路（AA-09/10/11）

- 小说种子结构化提取：`NarrativeSeed` + `needs_review` + 关系图兼容输出
- 文本驱动自动人设参数化：`ParameterizedCharacterProfile` + override 优先
- 多路径并行推演：2~3 路独立演化、失败隔离、winner 留存排序

### 2.2 P1 交互增强（AA-12/13/14）

- 涌现式冲突探针：K 轮交互、冲突候选、六步绑定建议、风险标记
- 上帝视角事件注入：checkpoint 重算、前后排序对比、审计日志
- 角色访谈接口：声线回应、记忆依据、OOC/泄密风险标记

### 2.3 P2 群体记忆层（AA-15）

- GroupMemory 传播：群体事件 -> 成员行为约束
- `chapter_range` 过滤 + hidden 默认抑制
- propagation logs + reversible patches

### 2.4 API 与 Workbench 接入

新增/落地 V6 API：

- `POST /api/narrative/v6/seed/extract`
- `POST /api/narrative/v6/characters/parameterize`
- `POST /api/narrative/v6/simulations/parallel`
- `GET /api/narrative/v6/simulations/{id}`
- `POST /api/narrative/v6/conflicts/probe`
- `POST /api/narrative/v6/simulations/{id}/inject-event`
- `POST /api/narrative/v6/characters/{id}/interview`
- `POST /api/narrative/v6/group-memory/apply`
- `POST /api/narrative/v6/graph/memory/compact`
- `GET /api/narrative/v6/graph/memory/audit`
- `POST /api/narrative/v6/graph/memory/audit/snapshot`
- `GET /api/narrative/v6/graph/memory/audit/history`
- `GET /api/narrative/v6/graph/memory/audit/alerts`
- `GET /api/narrative/v6/observability`

Workbench 最小入口：

- 新增 `CharacterInterviewPanel`（V2 Workbench 页面可直接调用访谈 API）

### 2.5 V6.1 稳定性增强（T09/T10）

- simulation 存储支持按行数/文件体积触发轮转，归档到按日期分桶目录并可回放重载
- 新增 V6 runtime metrics 持久化与阈值告警（latency P95 / error rate / fallback rate）
- 路由层完成结构化埋点，覆盖 seed/parameterize/sim/get/probe/inject/interview/group-memory

### 2.6 V6.1 GraphRAG 增强（T11）

- 新增 deterministic GraphRAG 检索服务，支持 seed/relationship/group-memory 聚合检索与 fallback
- 新增 `POST /api/narrative/v6/graph/retrieve` 契约接口
- simulation 与 interview 路由支持自动注入 GraphRAG hints，结果可审计

### 2.7 V6.1 Cross-session stitching（T12）

- 新增持久化 `graph memory` 存储（JSONL），将 GraphRAG 命中按 query/route/chapter 记录为可检索历史
- `graph/retrieve`、`simulations/parallel`、`characters/{id}/interview` 三条路由接入跨会话检索拼接
- `GraphRAGRetrieveResponse` 新增 `history_recall_used` 与 `stitched_from_history_count` 审计字段
- 支持 history-only recall（无 seed 输入时也可召回有效历史命中），并保持 deterministic fallback 路径

### 2.8 V6.1 Stitching policy hardening（T13）

- graph memory 检索新增可配置策略：`max_age_hours`（TTL）、`chapter_window`（章节范围）、`source_weights`（来源权重）
- 默认策略落地到配置层：`v6_graph_memory_max_age_hours`、`v6_graph_memory_chapter_window`、`v6_graph_memory_source_weights_json`
- 增补 graph memory store 测试覆盖过期过滤、章节窗口过滤、来源权重排序，避免跨会话召回漂移

### 2.9 V6.1 Semantic-drift guard + memory compaction（T14）

- graph memory 检索新增 `min_token_overlap` 语义漂移阈值，降低弱相关 history 命中污染
- graph memory store 新增 `compact()`，可移除过期记录、重复记录并重写 JSONL 文件
- 新增 `POST /api/narrative/v6/graph/memory/compact` 运维入口，返回 `before/after/removed`

### 2.10 V6.1 Graph memory audit snapshots（T15）

- graph memory store 新增只读 `audit_snapshot()`，输出 total/active/expired/hidden/duplicate 计数
- 审计快照包含 chapter bounds、source route 分布、node type 分布、当前策略与 latest records
- 新增 `GET /api/narrative/v6/graph/memory/audit`，用于验收与排查 history recall 污染

### 2.11 V6.1 Graph memory audit snapshot persistence（T16）

- graph memory store 新增 `persist_audit_snapshot()` 与 `audit_history()`
- 审计快照写入 `artifacts/history/v6_graph_memory_audit.jsonl`，并按 `v6_graph_memory_audit_max_rows` 裁剪
- 新增 `POST /api/narrative/v6/graph/memory/audit/snapshot` 与 `GET /api/narrative/v6/graph/memory/audit/history`

### 2.12 V6.1 Graph memory audit trend alerts（T17）

- graph memory store 新增 `audit_trend_alerts()`，基于持久化审计历史计算趋势告警
- 支持 expired rate、duplicate groups、active rows drop 三类阈值告警
- 新增 `GET /api/narrative/v6/graph/memory/audit/alerts`，用于只读验收与后续 UI 展示

## 3. 关键文件

### 后端

- `backend/app/services/narrative_v6/schemas.py`
- `backend/app/services/narrative_v6/seed_extractor.py`
- `backend/app/services/narrative_v6/character_parameterizer.py`
- `backend/app/services/narrative_v6/parallel_simulation.py`
- `backend/app/services/narrative_v6/scoring.py`
- `backend/app/services/narrative_v6/conflict_probe.py`
- `backend/app/services/narrative_v6/event_injection.py`
- `backend/app/services/narrative_v6/character_interview.py`
- `backend/app/services/narrative_v6/group_memory.py`
- `backend/app/services/narrative_v6/graph_rag.py`
- `backend/app/services/narrative_v6/graph_memory_store.py`
- `backend/app/services/narrative_v6/state_store.py`
- `backend/app/services/narrative_v6/observability.py`
- `backend/app/core/config.py`
- `backend/app/api/routes/narrative_v6.py`
- `backend/app/main.py`
- `artifacts/history/v6_simulation_results.jsonl`（默认持久化回放存储）
- `artifacts/history/v6_simulation_archive/`（轮转归档分桶）
- `artifacts/history/v6_runtime_metrics.jsonl`（观测指标）
- `artifacts/history/v6_graph_memory.jsonl`（跨会话 graph memory 命中存储）

### 前端

- `ui-react/src/features/v2Workbench/components/CharacterInterviewPanel.tsx`
- `ui-react/src/pages/V2WorkbenchPage.tsx`
- `ui-react/src/api.ts`

### 测试

- `tests/test_narrative_seed_extractor.py`
- `tests/test_character_parameterizer.py`
- `tests/test_parallel_plot_simulation.py`
- `tests/test_emergent_conflict_probe.py`
- `tests/test_event_injection_checkpoint.py`
- `tests/test_character_interview.py`
- `tests/test_group_memory_layer.py`
- `tests/test_graph_rag_retrieval.py`
- `tests/test_v6_graph_memory_store.py`
- `tests/test_v6_state_store.py`
- `tests/test_narrative_v6_observability.py`
- `tests/test_narrative_v6_api.py`
- `tests/test_run_v6_acceptance_review.py`
- `ui-react/src/features/v2Workbench/characterInterviewPanel.test.tsx`
- `tests/test_run_layered_tests.py`

## 4. 验证证据（已执行）

1. `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q`
- 结果：`35 passed`（acceptance targeted gate）

2. `python scripts/run_layered_tests.py v6`
- 结果：`50 passed`

3. `python scripts/run_layered_tests.py v6 api v4 frontend`
- 结果：通过（V6 50 passed + API 24 passed + V4 38 passed + Frontend 18 passed）

4. `npm --prefix ui-react run build`
- 结果：`build success`

5. `python scripts/run_v6_acceptance_review.py`
- 结果：通过，报告路径：`artifacts/acceptance/v6-acceptance-20260430T163049Z.md`

6. `artifacts/v6_cycles/t12/v6-t12-20260428T145046Z.md`
- 结果：T12 任务级验收报告已落盘（含命令、计数、范围）

7. `artifacts/v6_cycles/t13/v6-t13-20260428T150732Z.md`
- 结果：T13 任务级验收报告已落盘（含策略硬化与回归计数）

8. `artifacts/v6_cycles/t14/v6-t14-20260430T160914Z.md`
- 结果：T14 任务级验收报告已落盘（含 drift guard、compaction 与回归计数）

9. `artifacts/v6_cycles/t15/v6-t15-20260430T161812Z.md`
- 结果：T15 任务级验收报告已落盘（含 audit snapshot 与回归计数）

10. `artifacts/v6_cycles/t16/v6-t16-20260430T162441Z.md`
- 结果：T16 任务级验收报告已落盘（含 audit snapshot persistence 与回归计数）

11. `artifacts/v6_cycles/t17/v6-t17-20260430T163112Z.md`
- 结果：T17 任务级验收报告已落盘（含 audit trend alerts 与回归计数）

## 5. 当前门禁结论

- `T01` 到 `T17`：全部 `ACCEPTED`
- V6 阶段验收结论：`GO`
- 下一执行建议：进入 `V6.1` 后续（graph memory audit UI/workbench surface）

## 6. 残余风险（非阻断）

- 当前推演/访谈为 deterministic-first，尚未接真实 LLM runtime 策略与成本门禁。
- GraphRAG 已完成 deterministic 接入，但尚未接入向量索引/远端检索基础设施。
- cross-session stitching 已引入 TTL/window/weight、语义漂移阈值、compaction、只读审计快照、审计历史持久化与趋势告警，尚未接入 Workbench 可视化。
- 观测指标目前以本地 JSONL 为主，尚未接入远端告警通道与生产灰度采样策略。

## 7. 一句话交接

V6 已从需求文档推进为“可运行动态故事世界推演系统”并完成 P0/P1/P2 全链路实现、门禁测试与最小前端入口，可直接进入外部验收评审或下一阶段增强。
