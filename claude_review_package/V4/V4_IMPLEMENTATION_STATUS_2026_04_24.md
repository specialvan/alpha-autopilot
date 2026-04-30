# V4 实现推进状态（2026-04-24）

## 1. 本轮完成

- 完成 V4 需求深度评审并形成打回报告：
  - `V4_REQUIREMENT_REVIEW_REJECT_REPORT_2026_04_24.md`
- 按修订口径补齐 V4 文档中的可验收条款与桥接契约。
- 推进 V4 代码实现：
  - 关系层：修复冲突均值计算与张力评分抽象
  - 性格层：补 `analyzer` 与输入剪裁
  - 压力层：补 `pressure_index` 并导出分析接口
  - 剧情层：补候选构建、候选基数保障、留存上下文排序
  - 集成层：补 `v4_enabled` 回滚开关、QC 摘要、桥接契约字段
- 推进测试：
  - `tests/test_alpha_autopilot_v4_modules.py`
  - `backend/tests/test_narrative_v4_api.py`
  - 分层门禁脚本新增 `v4` 层
- 按 V4 PR 需求文档继续推进增量实现：
  - 关系层：补跨章节关系位移跟踪（`relationship_history` -> displacement events + graph summary）
  - 性格层：补多题材参数校准（`genre_profile` / `genre` 驱动 bias 校准）
  - 集成层：补 V3 留存反馈动态回写（`v3_feedback_history` -> retention 权重自适应）
  - 接口层：补 `/api/v4/workbench/preview`，并在 V2 workbench context 中结构化暴露
    - `relationship_graph`
    - `relationship_displacements`
    - `retention_writeback`
  - 回写输入层：live workbench context 自动从 history snapshots 提取 `v3_feedback_history`
  - 前端层：V2 Workbench Context Rail 增加 V4 结构化可视化（图谱规模、位移、反馈信号）
  - 持久化层：补跨会话 V4 记忆存储
    - `artifacts/history/v4_relationship_memory.jsonl`
    - `artifacts/history/v4_feedback_memory.jsonl`
    - `build_v4_bridge_payload_with_memory()` 自动读取/写入，形成反馈闭环与关系记忆
  - 长窗口策略：history window 从短窗口扩展到 `50`，并在 payload 中输出 `memory_summary`
  - 记忆策略层：补 V4 关系/反馈记忆的衰减与去噪策略
    - relationship: collapse + clip + decay filter
    - feedback: dedupe + clip + decay filter
    - `memory_summary` 新增策略与衰减/去噪统计
  - 时间轴层：补 V4 图谱与候选的章节级时间轴可视化
    - backend 输出 `relationship_timeline` + `candidate_timeline`
    - V2 Workbench Context Rail 增加双时间轴图表视图
  - 自动学习层：补题材校准参数自动学习首版
    - 基于反馈窗口 + 衰减聚合生成 `genre_calibration`
    - 自动回写 `genre_profile` bias，并在 `memory_summary` 暴露学习统计
    - 增加在线守护阈值与异常回退（high-volatility / divergence / reversal）
    - 增加配置化阈值入口（`settings` + `v4_genre_guard_overrides_json` 按题材分桶覆盖）
  - 可观测层：补 V4 持久化记忆看板接入
    - dashboard 输出 `v4Observability`（context/rows/signal/topGenres）
    - 前端新增 V4 Observability 面板并展示记忆与自动学习就绪度
    - 增加 trend windows 与 alerts（含 critical/warning 计数）
    - 增加本地告警通道路由（JSONL inbox + cooldown 去重）

## 2. 当前状态结论

- V4 已从“纯规划”进入“生产化工程推进”阶段（已具备首版可测能力，不再按原型口径验收）。
- 已具备跨章节关系跟踪、题材校准自动学习、留存回写、记忆可观测和 workbench 可视化能力，下一步补齐生产级门禁（SLO、远端告警、灰度与值班）。

## 3. 仍待后续扩展

- 题材自动学习守护阈值改为线上可配置（按题材分桶）
- 本地告警通道扩展到远端通知（IM/Webhook）与值班流程
- 增补 V4 生产级指标治理：P95 延迟、错误率、fallback 比例门限与告警阈值
- 增补发布治理清单：灰度条件、回退触发条件、回滚演练记录

## 4. 本轮验证证据

1. `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q`
- 结果：`26 passed`

2. `python scripts/run_layered_tests.py v4`
- 结果：通过

3. `pytest tests/test_run_layered_tests.py -q`
- 结果：`5 passed`

4. `python scripts/run_layered_tests.py quality api import`
- 结果：通过（未破坏既有 V2/V3 门禁）

5. `python scripts/run_layered_tests.py frontend import v4`
- 结果：通过

6. `npm run build` (`ui-react`)
- 结果：成功

7. `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py tests/test_narrative_v2_workbench_quality_enrichment.py tests/test_narrative_v2_workbench_context_api.py -q`
- 结果：`25 passed`

8. `python scripts/run_claude_acceptance_review.py`
- 结果：通过（产出 `artifacts/acceptance/claude-acceptance-20260426T065834Z.md`）
