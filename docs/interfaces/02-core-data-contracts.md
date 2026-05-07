# 核心数据契约

更新时间：2026-05-08

## 说明

本页只固定最影响 DeepWiki 理解主链关系的对象，不追求覆盖所有 schema。字段说明以当前代码为准，并尽量标出：

- `代码定义`
- `前端已消费`
- `[推断]`
- `待确认`

## 1. Baseline 与 V2 基础输入

### 1.1 `PreviewRequest`

- 文件：`backend/app/services/narrative/schemas.py`
- 用途：`POST /api/recommendation/preview` 的请求体。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `tuningWeights` | `list[TuningWeightPayload]` | 是 | 无 | 调权输入。每项含 `label/value/direction/description`。 |
| `recommendations` | `list[RecommendationPayload]` | 是 | 无 | 前端会传入推荐列表。`代码定义` 存在。 |

- 备注：
  - `[推断]` 当前 `build_preview()` 实现只消费 `tuningWeights`，没有使用 `recommendations` 字段。
  - `前端已消费`：`ui-react/src/api.ts`

### 1.2 `StoryStatePayload`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：V2 推荐预览与 Workbench context 的核心状态对象。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `chapter_index` | `int` | 是 | 无 | 章节序号。 |
| `stage` | `str` | 是 | 无 | 后端未枚举限制。前端当前只使用 `opening/middle/mid_late/late`。 |
| `mainline_progress` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `sideplot_progress` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `conflict_intensity` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `emotional_temperature` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `pacing_speed` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `foreshadowing_load` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `payoff_pressure` | `float` | 是 | 无 | `0.0 ~ 1.0`。 |
| `characters` | `dict[str, CharacterStatePayload]` | 否 | `{}` | 角色态。 |
| `tags` | `list[str]` | 否 | `[]` | 标签。 |
| `retention_desire` | `RetentionDesireVector \| None` | 否 | `None` | V2/V3 留存目标向量。 |
| `macro_structure` | `MacroStructureEnum` | 否 | `progressive` | 宏观结构枚举。 |

### 1.3 `PlotUnitScaffold`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：给 V2 preview 提供更明确的六步剧情骨架。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `encounter_event` | `str` | 是 | 无 | 遭遇事件。 |
| `desire_goal` | `str` | 是 | 无 | 欲望目标。 |
| `obstacle` | `str` | 是 | 无 | 障碍。 |
| `solution_method` | `str` | 是 | 无 | 解法。 |
| `action_climax.node` | `str` | 是 | 无 | 动作高潮节点。 |
| `action_climax.turn_type` | `TurnTypeEnum` | 是 | 无 | `obstacle_shift / goal_inversion / character_contrast`。 |
| `resolution` | `str` | 是 | 无 | 收束。 |

### 1.4 `NarrativeV2PreviewRequest`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：`POST /api/v2/recommendation/preview`
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `case_id` | `str` | 是 | 无 | 验证/账本标识。 |
| `state` | `StoryStatePayload` | 是 | 无 | 推荐输入状态。 |
| `plot_unit_scaffold` | `PlotUnitScaffold \| None` | 否 | `None` | 可选剧情脚手架。 |

### 1.5 `NarrativeV2DecisionPayload`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：V2 preview 的策略输出摘要。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `selected_action` | `str` | 否 | `""` | 选中的动作。 |
| `selected_score` | `float` | 否 | `0.0` | 动作得分。 |
| `accepted_actions` | `list[str]` | 否 | `[]` | 规则允许动作。 |
| `blocked_actions` | `list[str]` | 否 | `[]` | 规则阻断动作。 |
| `prerequisite_missing_actions` | `list[str]` | 否 | `[]` | 缺少前置条件动作。 |
| `rule_status_summary` | `RuleStatusSummaryPayload` | 否 | 见 schema | 汇总 legal/blocked/prerequisite_missing 计数。 |
| `constraint_hint` | `str` | 否 | `"clear"` | 约束提示。 |
| `quality_hint` | `str` | 否 | `"blocked"` | 结果质量提示。 |
| `candidates` | `list[NarrativeV2DecisionCandidatePayload]` | 否 | `[]` | 候选动作与分数。 |
| `retention_driver` | `NarrativeV2RetentionDriverPayload \| None` | 否 | `None` | 留存驱动解释。 |

## 2. Workbench 嵌入上下文契约

### 2.1 `NarrativeV2WorkbenchContextPayload`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：`GET/POST /api/v2/workbench/contexts*` 的单个 context 对象。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `str` | 是 | 无 | context 标识。 |
| `chapterNumber` | `int` | 是 | 无 | 章节号。 |
| `title` | `str` | 是 | 无 | 标题。 |
| `stage` | `str` | 是 | 无 | 阶段。 |
| `summary` | `str` | 是 | 无 | 章节摘要。 |
| `state` | `StoryStateContextPayload` | 是 | 无 | 上下文状态。 |
| `compare_baseline` | `NarrativeV2CompareBaselinePayload \| None` | 否 | `None` | 与 baseline 对比。 |
| `v4_preview` | `NarrativeV4WorkbenchPreviewPayload \| None` | 否 | `None` | 嵌入 V4 预览。 |
| `v8_preview` | `NarrativeV8WorkbenchPreviewPayload \| None` | 否 | `None` | 嵌入 V8 控制态预览。 |
| `quality` | `NarrativeV2ContextQualityPayload \| None` | 否 | `None` | 质量信息。 |

### 2.2 `NarrativeV2WorkbenchContextsResponsePayload`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：Workbench context 列表响应。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `contexts` | `list[NarrativeV2WorkbenchContextPayload]` | 否 | `[]` | 上下文列表。 |
| `source` | `str \| None` | 否 | `None` | 来源类型。 |
| `context_contract` | `str \| None` | 否 | `None` | 契约标识。 |
| `fallback_reason` | `str \| None` | 否 | `None` | 回退原因。 |
| `report_path` / `report_url` | `str \| None` | 否 | `None` | 本地或在线报告指针。 |
| `run_id` | `str \| None` | 否 | `None` | 报告/运行标识。 |
| `arbitration_strategy` | `str \| None` | 否 | `None` | 来源仲裁策略。 |
| `source_diagnostics` | `dict[str, Any]` | 否 | `{}` | 来源诊断。 |

## 3. V4 嵌入预览对象

### 3.1 `NarrativeV4WorkbenchPreviewPayload`

- 文件：`backend/app/services/narrative_v2/schemas.py`
- 用途：嵌入 Workbench context 的 V4 关系图/候选预览。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `enabled` | `bool` | 是 | 无 | 是否成功启用。 |
| `fallback_reason` | `str \| None` | 否 | `None` | 降级原因。 |
| `candidate_count` | `int` | 否 | `0` | 候选数。 |
| `relationship_graph` | `dict[str, Any]` | 否 | `{}` | 关系图摘要。 |
| `relationship_timeline` | `list[dict]` | 否 | `[]` | 关系时序。 |
| `candidate_timeline` | `list[dict]` | 否 | `[]` | 候选时序。 |
| `memory_summary` | `dict[str, Any]` | 否 | `{}` | V4 内存摘要。 |
| `selected_candidate` | `NarrativeV4WorkbenchCandidatePayload \| None` | 否 | `None` | 选中候选。 |
| `top_candidates` | `list[NarrativeV4WorkbenchCandidatePayload]` | 否 | `[]` | 候选列表。 |

## 4. V6 模拟与 GraphRAG

### 4.1 `NarrativeSeedExtractionRequest` / `Response`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：从章节文本提取模拟种子。
- 关键输入：
  - `chapters`：至少 1 条，`text` 必填且非空。
  - `mode`：`full / incremental / chapter_only`，默认 `full`。
  - `existing_story_bible`：可选。
  - `compression_mode`：可选。
- 关键输出：
  - `seed`
  - `relationship_graph_input`
  - `character_behavior_events`

### 4.2 `ParallelSimulationRequest`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：`POST /api/narrative/v6/simulations/parallel`
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `story_state` | `dict[str, Any]` | 否 | `{}` | 当前故事状态。 |
| `narrative_seed` | `NarrativeSeed` | 是 | 无 | 种子对象。 |
| `character_profiles` | `list[ParameterizedCharacterProfile]` | 否 | `[]` | 角色参数化画像。 |
| `relationship_graph_input` | `dict \| None` | 否 | `None` | 关系图输入。 |
| `group_memory_graph` | `GroupMemoryGraph \| None` | 否 | `None` | 群体记忆图。 |
| `plot_unit_scaffold` | `PlotUnitScaffold \| None` | 否 | `None` | 剧情脚手架。 |
| `retention_desire_vector` | `dict[str, float \| str]` | 否 | `{}` | 留存向量。 |
| `macro_story_structure` | `str` | 否 | `"progressive"` | 宏观结构。 |
| `path_count` | `int` | 否 | `3` | 仅允许 `2 ~ 3`。 |
| `simulation_id` | `str \| None` | 否 | `None` | 可传外部标识。 |
| `graph_rag_query` | `str \| None` | 否 | `None` | GraphRAG 查询。 |

### 4.3 `ParallelPlotSimulationResult`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：并行模拟结果。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `simulation_id` | `str` | 是 | 无 | 模拟 ID。 |
| `paths` | `list[SimulationPath]` | 否 | `[]` | 路径列表。 |
| `winner_path_id` | `str \| None` | 否 | `None` | 胜出路径。为空时通常表示 fallback。 |
| `decision_summary` | `str` | 是 | 无 | 决策摘要。 |
| `generated_at_utc` | `str` | 是 | 无 | UTC 时间。 |
| `risk_flags` | `list[str]` | 否 | `[]` | 风险标记。 |

### 4.4 `EventInjectionRequest` / `EventInjectionResult`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：对已有 simulation 注入事件并重排。
- 关键输入：
  - `injected_event.event_type`
  - `injected_event.description`
  - `injected_event.force_level`：默认 `0.5`
  - `author_intent`
  - `macro_story_structure`
- 关键输出：
  - `previous_winner_path_id`
  - `winner_path_id`
  - `updated_paths`
  - `ranking_changes`
  - `macro_structure_risk`
  - `destructive_confirmation_required`
  - `updated_simulation`

### 4.5 `GraphRAGRetrieveRequest` / `Response`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：检索 deterministic GraphRAG 上下文。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `query` | `str` | 是 | 无 | 最短 1 字符。 |
| `top_k` | `int` | 否 | `4` | `1 ~ 12`。 |
| `include_hidden` | `bool` | 否 | `False` | 是否检索 hidden。 |
| `chapter_index` | `int \| None` | 否 | `None` | 章节窗口。 |
| `fallback_used` | `bool` | 响应 | `False` | 是否走 fallback。 |
| `fallback_reason` | `str \| None` | 响应 | `None` | fallback 原因。 |
| `stitched_from_history_count` | `int` | 响应 | `0` | 历史记忆回填数。 |
| `history_recall_used` | `bool` | 响应 | `False` | 是否拼接历史命中。 |

### 4.6 `GraphMemoryRecord`

- 文件：`backend/app/services/narrative_v6/schemas.py`
- 用途：GraphRAG 命中历史与可复盘对象。
- 关键字段：
  - `record_id`
  - `query`
  - `source_route`
  - `chapter_index`
  - `simulation_id`
  - `node_id`
  - `node_type`
  - `summary`
  - `score`
  - `confidence`
  - `hidden`
  - `created_at_utc`

## 5. V7 决策与治理核心契约

### 5.1 `UnifiedDecisionPreviewRequest`

- 文件：`backend/app/services/narrative_v7/schemas.py`
- 用途：`POST /api/narrative/v7/decision/preview`
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `text` | `str` | 是 | 无 | 最短 1 字符。 |
| `story_state` | `dict[str, Any]` | 否 | `{}` | 原始故事态。 |
| `character_states` | `list[dict[str, Any]]` | 否 | `[]` | 角色态。 |
| `project_state` | `NovelProjectState \| None` | 否 | `None` | 项目元数据。 |
| `benchmark_state` | `BenchmarkParameterSet \| None` | 否 | `None` | benchmark 走廊。 |
| `metric_overrides` | `dict[str, float]` | 否 | `{}` | 指标覆盖。 |
| `decision_state` | `DecisionState \| None` | 否 | `None` | 决策状态。 |
| `override_confirmed` | `bool` | 否 | `False` | 是否允许覆盖型动作。 |

### 5.2 `NarrativeDecision`

- 文件：`backend/app/services/narrative_v7/schemas.py`
- 用途：V7 路由式决策结果。
- 关键字段：
  - `decision_type`：`open / add / reduce / stop_loss / take_profit / observe / reversal_confirm / breakout_follow / retrace_repair`
  - `risk_level`：`P0 / P1 / P2`
  - `route_id`
  - `reasons`
  - `suggested_actions`
  - `observe_next_metrics`

### 5.3 `BenchmarkIngestRequest` / `Response`

- 文件：`backend/app/services/narrative_v7/schemas.py`
- 用途：benchmark 样本入库。
- 关键输入：
  - `book_id`：必填且非空
  - `channel`
  - `genre_track`
  - `sample_payload`
- 关键输出：
  - `accepted`
  - `version`
  - `recalibrated`
  - `message`

### 5.4 `BenchmarkMaintenanceAlertEvent`

- 文件：`backend/app/services/narrative_v7/schemas.py`
- 用途：benchmark 维护告警事件。
- 关键字段：
  - `event_id`
  - `generated_at`
  - `level`：`ok / warn / critical`
  - `should_page`
  - `should_ticket`
  - `breaches`
  - `report_severity`

### 5.5 `BenchmarkMaintenanceAlertGovernanceRunResponse`

- 文件：`backend/app/services/narrative_v7/schemas.py`
- 用途：治理 run 主对象。
- 关键字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `run_id` | `str` | 否 | `""` | 治理 run 标识。 |
| `generated_at` | `str` | 是 | 无 | UTC 时间。 |
| `dry_run` | `bool` | 是 | 无 | 是否演练。 |
| `alert_limit` | `int` | 否 | `0` | 告警处理上限。 |
| `archive_limit` | `int` | 否 | `0` | 归档处理上限。 |
| `idempotency_key` | `str` | 否 | `""` | 幂等键。 |
| `retry_run_id` | `str` | 否 | `""` | 被重试 run。 |
| `attempt` | `int` | 否 | `1` | 重试次数。 |
| `idempotency_reused` | `bool` | 否 | `False` | 是否命中幂等复用。 |
| `performed_steps` | `list[str]` | 否 | `[]` | 已执行步骤。 |
| `auto_archive` | `BenchmarkMaintenanceAlertAutoArchiveResponse` | 是 | 无 | 自动归档结果。 |
| `archive_cleanup` | `BenchmarkMaintenanceAlertArchiveCleanupResponse` | 是 | 无 | 归档清理结果。 |
| `message` | `str` | 否 | `""` | 结果摘要。 |

- 说明：
  - V7 还有大量 `digest / escalation / remediation / auto-remediate` 衍生对象。
  - 当前建议先把 `AlertEvent -> GovernanceRunResponse -> EscalationEvent` 作为主链固定，其余接口在后续文档展开。

## 6. V8 控制态与状态机契约

### 6.1 枚举与类型别名

- 文件：`backend/app/services/narrative_v8/schemas.py`
- 当前最关键枚举：

```text
ControlPhase:
- probe
- pressure_test
- containment
- conversion
- harvest

ControlSurfaceState:
- harmless
- suspicious
- distrusted
- repair_attempt
- partially_restored
- upgraded
- more_hidden
- stronger
- hardened
- collapsed

FallbackAction:
- hold_position
- gather_information
- defer_to_public_mask
- reduce_exposure
```

### 6.2 `SceneContext`

- 文件：`backend/app/services/narrative_v8/schemas.py`
- 用途：V8 决策时的场景态输入。
- 关键字段：
  - `arena`
  - `stake`
  - `observers`
  - `power_topology`
  - `relationship_distance`
  - `visibility`
  - `time_pressure`
  - `current_phase`
  - `current_control_state`
  - `existing_state`

- 约束：
  - `代码定义`：`visibility == "public"` 时必须声明至少一个 observer。

### 6.3 `BuildVillainFeedbackOutput`

- 文件：`backend/app/services/narrative_v8/schemas.py`
- 用途：V8 控制器输出对象，当前主要通过 Workbench 嵌入。
- 关键字段：
  - `packet`
  - `next_snapshot`
  - `next_control_state`

- 约束：
  - `代码定义`：`next_control_state` 必须与 `packet.transition.next_state` 一致。

## 7. 待确认

- `StoryStatePayload.stage` 在后端是普通 `str`，当前是否允许超过前端四态之外的阶段值，需团队确认。
- `PreviewRequest.recommendations` 当前未被 baseline preview 使用，这是否是保留字段还是遗漏逻辑，需确认。
- V7 长链 `auto-remediate` 家族对象是否全部保留为长期接口，需产品/研发共同确认。
