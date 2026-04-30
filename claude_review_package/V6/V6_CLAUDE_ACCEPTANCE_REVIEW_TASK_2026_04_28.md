# V6 Claude 验收评审任务单（2026-04-28）

## 1. 评审目标

请对 V6 当前交付进行验收评审，重点验证以下内容：

1. V6 主链路已可运行：文本 -> seed -> 人设参数 -> 并行推演 -> winner
2. V6 路径未破坏 `v1/v2` 与 `V2 Workbench` 默认行为
3. 所有新增 LLM 相关能力具备 deterministic/mock fallback
4. 模拟结果具备可审计字段与失败隔离能力
5. GraphRAG 检索支持跨会话 history stitching 且审计字段可观测
6. stitching policy（TTL/window/source weight）可配置且在检索中生效
7. graph memory 具备 semantic-drift guard 与 compaction 维护入口
8. graph memory audit snapshot 可只读复核规模、分布与策略状态
9. graph memory audit snapshot 可持久化并读取历史
10. graph memory audit history 可输出趋势告警

## 2. 输入文档（按顺序）

1. `claude_review_package/README_FOR_CODEX.md`
2. `claude_review_package/V6/V6_MIROFISH_PR_REQUIREMENTS.md`
3. `claude_review_package/V6/V6_REVIEW_DEV_TASK.md`
4. `claude_review_package/V6/V6_ACCEPTANCE_HANDOFF_2026_04_28.md`
5. `claude_review_package/V6/V6_DEVELOPMENT_ACCEPTANCE_CHECKLIST.md`
6. `PROJECT_STATUS.md`

## 3. 必跑命令

1. `pytest tests/test_narrative_seed_extractor.py tests/test_character_parameterizer.py tests/test_parallel_plot_simulation.py tests/test_emergent_conflict_probe.py tests/test_event_injection_checkpoint.py tests/test_character_interview.py tests/test_group_memory_layer.py tests/test_graph_rag_retrieval.py tests/test_v6_graph_memory_store.py tests/test_v6_state_store.py tests/test_narrative_v6_observability.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py -q`
2. `python scripts/run_layered_tests.py v6 api v4 frontend`
3. `npm --prefix ui-react run build`

可选一键命令：

- `python scripts/run_v6_acceptance_review.py`

## 4. 必查代码入口

### 后端

- `backend/app/services/narrative_v6/schemas.py`
- `backend/app/services/narrative_v6/seed_extractor.py`
- `backend/app/services/narrative_v6/character_parameterizer.py`
- `backend/app/services/narrative_v6/parallel_simulation.py`
- `backend/app/services/narrative_v6/scoring.py`
- `backend/app/services/narrative_v6/state_store.py`
- `backend/app/services/narrative_v6/graph_rag.py`
- `backend/app/services/narrative_v6/observability.py`
- `backend/app/services/narrative_v6/conflict_probe.py`
- `backend/app/services/narrative_v6/event_injection.py`
- `backend/app/services/narrative_v6/character_interview.py`
- `backend/app/services/narrative_v6/group_memory.py`
- `backend/app/api/routes/narrative_v6.py`
- `backend/app/services/narrative_v6/graph_memory_store.py`
- `backend/app/core/config.py`

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
- `tests/test_narrative_v6_observability.py`
- `tests/test_narrative_v6_api.py`
- `tests/test_run_v6_acceptance_review.py`
- `ui-react/src/features/v2Workbench/characterInterviewPanel.test.tsx`

## 5. 阻断判定标准（P1）

以下任一满足则 `NO-GO`：

1. 并行路径存在中间状态污染
2. winner 无法追溯评分依据
3. 任一关键 API 缺 deterministic 路径
4. 单路径失败导致整体 500 或全量失败
5. 低置信度字段默认写入正式设定
6. Graph retrieval 无法在跨会话 history-only 输入下稳定召回
7. graph memory 超窗/过期记录仍参与排序
8. compaction 后重复/过期记录仍污染历史召回
9. audit snapshot 缺少来源/类型/策略字段导致无法复核召回污染
10. audit snapshot 无持久化历史导致无法复核趋势变化
11. audit alerts 无法识别过期率、重复组或 active rows 突降

## 6. 非阻断项（P2/P3）

以下可记为后续项，不作为当前阻断：

- GraphRAG 尚未纳入 P0
- P1/P2 能力未全部落地
- Workbench UI 入口仅完成后端契约预留

## 7. 评审输出格式

1. 结论：`通过` / `有条件通过` / `不通过`
2. 阻断项：逐条附证据
3. 非阻断风险：影响与建议
4. 验证记录：命令与结果摘要
5. 建议动作：最多 3 条

## 8. 一句话要求

请以当前代码与测试结果为准裁决，不使用历史阶段结论代替本轮证据。
