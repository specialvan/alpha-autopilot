# V6 实施任务板（单任务推进制）

## 1. 执行规则

1. 同一时间只允许一个 `ACTIVE` 任务。
2. 当前任务未达到 `ACCEPTED`，不得推进下一个任务。
3. 每个任务必须绑定固定验收命令与报告输出位置。
4. 每次验收后必须更新任务状态、风险和下一任务候选。

## 2. 当前周期

- active_task_id: `T17`
- active_task_name: `V6.1 graph memory audit trend alerts`
- cycle_status: `ACCEPTED`
- acceptance_command: `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q`
- acceptance_report_root: `artifacts/v6_cycles/t17/`
- next_task_candidate: `V6.1 graph memory audit UI/workbench surface`

## 3. 任务池（串行）

| Task ID | 对应 PR | 任务名称 | 验收命令 | 状态 |
| --- | --- | --- | --- | --- |
| `T01` | PR-AA-09 | 小说种子信息结构化提取器 | `pytest tests/test_narrative_seed_extractor.py -q` | `ACCEPTED (2026-04-28)` |
| `T02` | PR-AA-10 | 文本驱动自动人设参数化 | `pytest tests/test_character_parameterizer.py -q` | `ACCEPTED (2026-04-28)` |
| `T03` | PR-AA-11 | 多路径情节并行推演 | `pytest tests/test_parallel_plot_simulation.py -q` | `ACCEPTED (2026-04-28)` |
| `T04` | PR-AA-12 | 涌现式冲突探针 | `pytest tests/test_emergent_conflict_probe.py -q` | `ACCEPTED (2026-04-28)` |
| `T05` | PR-AA-13 | 上帝视角事件注入与重算 | `pytest tests/test_event_injection_checkpoint.py -q` | `ACCEPTED (2026-04-28)` |
| `T06` | PR-AA-14 | 角色访谈接口 | `pytest tests/test_character_interview.py -q` | `ACCEPTED (2026-04-28)` |
| `T07` | PR-AA-15 | 群体/派系记忆层 | `pytest tests/test_group_memory_layer.py -q` | `ACCEPTED (2026-04-28)` |
| `T08` | V6 Gate | 全链路验收与外部评审准备 | `python scripts/run_layered_tests.py v6 api v4 frontend` | `ACCEPTED (2026-04-28)` |
| `T09` | V6.1 | simulation 持久化回放加固 | `pytest tests/test_v6_state_store.py tests/test_narrative_v6_api.py -q` | `ACCEPTED (2026-04-28)` |
| `T10` | V6.1 | 观测门禁 + 轮转归档回放 | `pytest tests/test_v6_state_store.py tests/test_narrative_v6_observability.py tests/test_narrative_v6_api.py -q` | `ACCEPTED (2026-04-28)` |
| `T11` | V6.1 | GraphRAG 检索接入与主链路注入 | `pytest tests/test_graph_rag_retrieval.py tests/test_parallel_plot_simulation.py tests/test_character_interview.py tests/test_narrative_v6_api.py -q` | `ACCEPTED (2026-04-28)` |
| `T12` | V6.1 | cross-session graph memory stitching | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-04-28)` |
| `T13` | V6.1 | stitching policy hardening（TTL/window/weight） | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-04-28)` |
| `T14` | V6.1 | semantic-drift guard + memory compaction | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-05-01)` |
| `T15` | V6.1 | graph memory audit snapshots | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-05-01)` |
| `T16` | V6.1 | graph memory audit snapshot persistence | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-05-01)` |
| `T17` | V6.1 | graph memory audit trend alerts | `pytest tests/test_v6_graph_memory_store.py tests/test_graph_rag_retrieval.py tests/test_narrative_v6_api.py tests/test_run_v6_acceptance_review.py tests/test_run_layered_tests.py -q` | `ACCEPTED (2026-05-01)` |

## 4. 全局门禁（每个任务都要过）

- 不破坏 `v1/v2` 默认行为
- 不绕过 `V3` 留存排序
- deterministic/mock 路径可用
- 失败路径不拖垮主流程
- 回滚路径存在且可执行

## 5. 任务切换标准

- `PASS`: 验收命令返回 0
- `ACCEPTED`: `PASS` 且任务证据已回写文档
- `BLOCKED`: 有阻断项（schema 冲突、回滚缺失、测试失败）

## 6. 状态回写目标

每轮任务完成后至少回写：

- `PROJECT_STATUS.md`
- `claude_review_package/V6/V6_DEVELOPMENT_ACCEPTANCE_CHECKLIST.md`
- 当前任务对应的验收报告路径
