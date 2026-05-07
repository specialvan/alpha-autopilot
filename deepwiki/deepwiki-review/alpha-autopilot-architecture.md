# alpha-autopilot 架构与数据流分析

## 1. 项目总定位

`alpha-autopilot` 是一个面向**小说章节推荐与写作辅助**的研究型系统。核心目标是将"模型黑箱前的提示词工程"与"特征矩阵推荐"结合，形成可解释、可迭代、可验证、可进化的章节规划系统。

配套项目 `alpha-SRE` 是独立的 **SRE 可靠性控制面**，负责叙事状态一致性校验、事件回放、门禁拦截和事故管理。

---

## 2. 三层治理结构（版本分层）

```
┌─────────────────────────────────────────────────────────┐
│  Experimental / Advanced (V7 / V8)                      │
│  量化决策引擎 · 反派心理推演                               │
├─────────────────────────────────────────────────────────┤
│  Increment (V3 → V6)                                    │
│  留存目标函数 · 情节推荐增强 · 并行模拟 · 图谱记忆          │
├─────────────────────────────────────────────────────────┤
│  Baseline (V1 / V2)                                     │
│  特征矩阵推荐 · 工作台 · Dashboard                        │
└─────────────────────────────────────────────────────────┘
```

| 层级 | 版本 | 定位 | 状态 |
|------|------|------|------|
| Baseline | V1 | 初始特征矩阵推荐 | 稳定收口 |
| Baseline | V2 | 独立推荐工作台、上下文管理 | 稳定收口 |
| Increment | V3 | 读者留存目标函数、生成控制层 | 已完成 |
| Increment | V4 | 生产级工程化（可回滚、可观测、可验收） | 已完成 |
| Increment | V6 | 种子提取、角色参数化、并行模拟、图谱 RAG | 已完成 |
| Advanced | V7 | 叙事质量量化（NQM）、市场状态映射、决策路由 | 活跃 |
| Advanced | V8 | 反派控制面建模、刀法选择、状态账本 | 活跃 |

> **注意**：V5 在项目中被跳过，V3 与 V4 紧密耦合（V4 桥接 V3 的留存指标）。

---

## 3. 整体架构图

```
                          ┌──────────────┐
                          │   React UI   │
                          │  (Dashboard  │
                          │  + Workbench)│
                          └──────┬───────┘
                                 │ HTTP / REST
                                 ▼
                    ┌────────────────────────┐
                    │      FastAPI App       │
                    │  (backend/app/main.py) │
                    └────────────┬───────────┘
                                 │
          ┌──────────┬───────────┼───────────┬──────────┐
          ▼          ▼           ▼           ▼          ▼
     ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
     │ V2 API  ││ V4 API  ││ V6 API  ││ V7 API  ││ V8 API  │
     │Workbench││Narrative ││Narrative││Narrative ││(via V2  │
     │         ││         ││         ││         ││Workbench│
     └────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼
     ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
     │Service  ││Service  ││Service  ││Service  ││Service  │
     │Layer V2 ││Layer V4 ││Layer V6 ││Layer V7 ││Layer V8 │
     └────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
          │          │          │          │          │
          ▼          ▼          ▼          │          │
     ┌──────────────────────────────┐     │          │
     │    Core Domain Packages     │     │          │
     │  alpha_autopilot (V1)       │     │          │
     │  alpha_autopilot_v3         │     │          │
     │  alpha_autopilot_v4         │     │          │
     └──────────────────────────────┘     │          │
                                          │          │
                    ┌─────────────────────┘          │
                    ▼                                │
     ┌──────────────────────────┐                   │
     │     alpha-SRE            │                   │
     │  (Narrative State Lock   │                   │
     │   + Replay + Gate)       │◄──────────────────┘
     └──────────────────────────┘     (计划集成)
```

---

## 4. 代码组织结构

```
alpha-autopilot/
├── backend_app.py                    # 简易入口（V1 + V2 preview）
├── backend/
│   └── app/
│       ├── main.py                   # FastAPI 应用工厂 (create_app)
│       ├── core/
│       │   └── config.py             # Settings (Pydantic BaseSettings)
│       ├── api/routes/
│       │   ├── dashboard.py          # V1 Dashboard
│       │   ├── recommendation.py     # V1 推荐
│       │   ├── recommendation_v2.py  # V2 推荐预览
│       │   ├── workbench_v2.py       # V2 工作台上下文
│       │   ├── narrative_v4.py       # V4 情节预览 + 可观测性
│       │   ├── narrative_v6.py       # V6 种子提取 / 模拟 / 图谱
│       │   ├── narrative_v7.py       # V7 NQM 采样 / 决策 / 基准
│       │   ├── training.py           # 训练流程
│       │   ├── feedback.py           # 反馈收集
│       │   └── history.py            # 历史查询 / 导出
│       └── services/
│           ├── narrative/            # V1 基础服务
│           ├── narrative_v2/         # V2 工作台 + 预览
│           ├── narrative_v4/         # V4 桥接 + 记忆 + 告警
│           ├── narrative_v6/         # V6 模拟 + 图谱 + 评分
│           ├── narrative_v7/         # V7 决策控制 + 市场适配
│           └── narrative_v8/         # V8 反派控制面
├── alpha_autopilot/                  # V1 核心包
├── alpha_autopilot_v3/               # V3 留存 + 生成控制
│   ├── retention/                    # 留存目标函数 / 指标
│   ├── generation_control/           # 生成控制策略
│   └── decomposition/               # 章节分解
├── alpha_autopilot_v4/               # V4 集成桥接
│   └── integration.py               # build_v4_to_v3_bridge_result
└── ui-react/                         # React 前端
    └── src/
        ├── App.tsx                   # 主 Dashboard 页面
        ├── pages/V2WorkbenchPage.tsx # V2 工作台页面
        └── router/AppRouter.tsx      # 路由配置
```

---

## 5. 各版本详细分析

### 5.1 V1/V2 — Baseline 层

#### V1: 特征矩阵推荐
- **核心包**: `alpha_autopilot`
- **功能**: `FeatureMatrix` + `StoryState` → `recommend_chapter()`
- **数据流**: 前端请求 → 特征矩阵计算 → 推荐列表返回

#### V2: 推荐工作台
- **核心服务**: `NarrativeV2WorkbenchService`
- **功能**: 统一上下文管理，聚合多版本预览
- **上下文来源优先级**:
  1. 在线 PlotPilot 报告 API（`plotpilot_report_api_url`）
  2. 本地 PlotPilot 报告文件
  3. 导入的工作台上下文 JSON
  4. 基于 History + Dashboard 的 Live 上下文

**V2 工作台是整个系统的"聚合器"** — 它为每个上下文同时生成 V4 预览和 V8 预览：

```python
def _context_with_previews(context, *, memory_store, v8_preview_enabled):
    enriched = dict(context)
    enriched["v4_preview"] = build_v4_workbench_preview(enriched, ...)
    enriched["v8_preview"] = build_v8_workbench_preview(enriched, ...)
    return enriched
```

### 5.2 V3 — 读者留存目标函数

- **核心包**: `alpha_autopilot_v3`
- **模块**: `retention/target_function.py`, `generation_control/policy.py`

#### 留存目标函数
定义了留存驱动的优先级排序：
```
continue-reading-intent > chapter-attraction > emotional-drive
> pacing-drive > suspense-drive > conflict-drive > hook-strength
```

护栏约束：
- `preserve-structure-constraints`（结构约束）
- `preserve-style-consistency`（风格一致性）
- `preserve-fact-and-worldstate-constraints`（事实与世界观约束）
- `avoid-template-overfit`（避免模板过拟合）

#### 生成控制策略 (`GenerationControlPlan`)
根据 `chapter_attraction_score` 分档决策：

| 分数区间 | 模式 | 情感 | 节奏 | 冲突 | 钩子策略 |
|----------|------|------|------|------|----------|
| ≥0.75 | retain-and-escalate | high | brisk | aggressive | preserve-and-amplify |
| ≥0.5 | balance-and-sharpen | moderate | balanced | moderate | strengthen |
| <0.5 | repair-and-reframe | explicit | tight | raise-stakes | force-reader-pull |

同时检测反模式（template-overfit-risk, weak-reader-pull, weak-hook）。

### 5.3 V4 — 生产级工程化

- **服务层**: `backend/app/services/narrative_v4/`
- **核心**: 通过 `bridge.py` 桥接 V3 留存指标和 V4 增强

#### 关键组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Bridge | `bridge.py` | V3↔V4 数据桥接，记忆管理，genre 自动校准 |
| Memory Store | `memory_store.py` | 关系历史 / 反馈历史的持久化 |
| Alert Channel | `alert_channel.py` | 可观测性告警路由（IM / Webhook） |
| Observability | `observability.py` | 延迟 P95 / 错误率 / 回退率监控 |
| Prompt Compressor | `prompt_compressor.py` | 提示词压缩（token 预算控制） |
| Character Validation | `character_validation.py` | 角色行为验证（启发式 / LLM） |
| Relationship Graph | `relationship_graph.py` | 关系图谱过滤与导出 |
| Emotion Slider | `emotion_slider.py` | 情感滑块映射 |

#### V4 Bridge 数据流

```
context (V2 上下文)
  │
  ├─ merge relationship_history (内存存储 + 输入)
  ├─ merge feedback_history (内存存储 + 输入)
  ├─ 去噪 / 衰减 / 窗口裁剪
  ├─ genre 自动校准 (学习模式 / 护栏)
  ├─ 角色行为验证 (启发式 / 外部 LLM)
  ├─ 提示词压缩
  │
  ▼
build_v4_to_v3_bridge_result(context)  ← alpha_autopilot_v4
  │
  ├─ plot_candidates (候选情节列表)
  ├─ selected_candidate (选中候选)
  ├─ retention_sort_key (留存排序键)
  ├─ qc_summary (质量检查摘要)
  │
  ▼
V4 Payload (含 timeline, genre_calibration, memory_summary)
```

### 5.4 V6 — 动态故事世界模拟

- **服务层**: `backend/app/services/narrative_v6/`
- **API**: `/api/narrative/v6/...`

#### 关键能力

| 能力 | 描述 |
|------|------|
| 种子提取 | 从章节文本中提取叙事种子（角色、关系、事件、线程） |
| 角色参数化 | 构建角色画像（功能类型、情感滑块、置信度） |
| 并行模拟 | 对同一种子运行多策略模拟路径 |
| 图谱 RAG | 基于图谱的检索增强生成 |
| 记忆缝合 | 跨章节记忆一致性管理 |

#### 并行模拟引擎 (`ParallelPlotSimulationService`)

```
NarrativeSeed + CharacterProfiles + MacroStructure
  │
  ├─ 策略 1: retention_first    → SimulationPath 1
  ├─ 策略 2: suspense_first     → SimulationPath 2
  ├─ 策略 3: relationship_burst → SimulationPath 3
  │
  ▼ 各路径包含:
  - plot_outline (情节大纲)
  - six_step_scaffold_mapping (六步结构映射)
  - character_reactions (角色反应)
  - relationship_deltas (关系变化)
  - memory_deltas (记忆变化)
  - retention_score (留存评分)
  - consistency_issues (一致性问题)
  - causal_chain (因果链)
  │
  ▼ 排名与选择
  winner_path_id (按 retention_score 排名，跳过 critical-consistency)
```

### 5.5 V7 — 叙事质量量化引擎 (NQM)

- **服务层**: `backend/app/services/narrative_v7/`
- **API**: `/api/narrative/v7/...` (30+ 端点)

#### 核心概念：将叙事质量映射为"市场状态"

V7 借用金融市场的隐喻来量化叙事质量：

| 概念 | 叙事含义 | 金融隐喻 |
|------|----------|----------|
| NQM Vector | 叙事质量向量 (T2-T9, A4-A6, W5-W6, P3) | 多因子量化向量 |
| Composite | 综合指标 | 指数 |
| OHLCV | 开高低收量 | K 线 |
| Threshold Band | 阈值带 | 支撑/阻力位 |
| Zone | 干预区域 | 交易区间 |

#### 市场状态适配器 (`StoryStateMarketAdapter`)

```
story_state (章节状态)
  │
  ▼  _normalize_story_state()
标准化状态 (chapter_index, stage, deadlock, antipattern...)
  │
  ▼  _resolve_project_state() + _resolve_benchmark_state()
项目上下文 + 基准参数
  │
  ▼  _resolve_metric_state()
NQM 指标映射:
  T8 ← foreshadowing_load (伏笔负载)
  T4 ← payoff_pressure (兑现压力)
  T9 ← conflict_intensity (冲突强度)
  A6 ← a6_sigma_delta (IP 风味偏离)
  │
  ▼  _resolve_decision_state()
composite = avg(T8, T4, T9)
  │
  ▼
NarrativeMarketState (完整市场状态)
```

#### 决策反馈控制器 (`DecisionFeedbackController`)

优先级路由规则（按优先级排列）：

| 路由 | 条件 | 决策类型 | 风险等级 |
|------|------|----------|----------|
| R-OVERRIDE | 作者确认覆盖 | OBSERVE | P2 |
| R-04 | 开篇 T8 低于门禁 | STOP_LOSS | P0 |
| R-08 | 反模式 CRITICAL | STOP_LOSS | P0 |
| R-05 | 检测到死锁 | RETRACE_REPAIR | P1 |
| R-06 | 尾部钩子密度为零 | ADD | P1 |
| R-07 | 反派压力坍塌 | RETRACE_REPAIR | P1 |
| R-09 | IP 风味走廊偏离 | REDUCE | P1 |
| R-10 | 死亡章节情感兑现不足 | RETRACE_REPAIR | P1 |
| R-01 | NQM 综合低于 L 阈值 | STOP_LOSS | P0 |
| R-02 | NQM 在弹性注入区 | RETRACE_REPAIR | P2 |
| R-02B | 接近突破阈值 | BREAKOUT_FOLLOW | P2 |
| R-03 | NQM 高于 H 阈值 | OBSERVE | P2 |

#### V7 其他组件

| 组件 | 职责 |
|------|------|
| NQMSampler | 从文本+状态采样 NQM 向量 |
| ThresholdBandEngine | 计算支撑/阻力位、分类区域 |
| OpeningGate | 开篇门禁检查 |
| DeadlockRouter | 死锁检测与路由 |
| AntiPatternRegistry | 反模式注册与评估 |
| EmotionSatisfactionScorer | 情感满足度评分 |
| LoopStructureAnalyzer | 循环结构分析 |
| PacingInformationFlowController | 节奏信息流控制 |
| BenchmarkLibrary | 基准库管理（版本化、回滚、剪裁） |
| SellingPointContractGuard | 卖点契约守卫 |

### 5.6 V8 — 反派控制面建模

- **服务层**: `backend/app/services/narrative_v8/`
- **通过 V2 Workbench Bridge 暴露**（非独立路由）

#### 核心概念：反派心理+策略推演

V8 建模了一个完整的反派行为决策系统：

**输入三元组**：
- `VillainProfile`：反派画像（原型、核心创伤、心理素养、偏好刀法、禁忌行为等）
- `TargetProfile`：目标画像（自我形象、核心需求、弱点、防御风格等）
- `SceneContext`：场景上下文（场域、赌注、观察者、权力拓扑、控制阶段等）

#### 刀法选择流程 (`controller.py`)

```
BuildVillainFeedbackInput (villain + target + scene)
  │
  ▼  select_knives()
刀法选择（基于适配度评分、禁忌过滤、兼容性图谱）
  │  → DecisionLayer (scored_fit / fallback)
  │
  ▼  render_flavor()
风味渲染（色调、表面呈现、压力通道、证人姿态等）
  │  → FlavorRender
  │
  ▼  build_future_hooks()
未来钩子生成（基于刀法+风味+场景）
  │
  ▼  build_state_shift()
状态账本变化计算:
  │  - relationship: trust/debt/dependency/leverage
  │  - narrative: suspicion/reputation/witness_alignment/explanation_control
  │  - psychological: shame_load/wound_activation/protector_trigger/identity_destabilization
  │  - hook: planted/armed/recovered
  │
  ▼  derive_transition_outcome()
控制面状态转移 (harmless → suspicious → distrusted → ...)
  │  含失败模式 / 恢复模式 / 升级路径
  │
  ▼  apply_state_shift()
快照更新 → LedgerSnapshot (next_snapshot)
  │
  ▼
BuildVillainFeedbackOutput
  - packet (完整反派反馈包)
  - next_snapshot (下一状态快照)
  - next_control_state (下一控制面状态)
```

#### 状态账本 (Ledger) 系统

V8 使用 4 层 ±3 范围的状态账本来追踪反派-目标之间的动态：

```
LedgerSnapshot
├── RelationshipLedgerState    (trust, debt, dependency, leverage)
├── NarrativeLedgerState       (suspicion, reputation, witness_alignment, explanation_control)
├── PsychologicalLedgerState   (shame_load, wound_activation, protector_trigger, identity_destab)
└── HookLedgerState            (planted_hooks, armed_payoffs, recovered_hooks)
```

#### 控制阶段与状态机

```
控制阶段: probe → pressure_test → containment → conversion → harvest

控制面状态转移:
harmless → suspicious → distrusted → repair_attempt → partially_restored
                                                    → upgraded → more_hidden / stronger / hardened
                                                    → collapsed
```

#### V8 Workbench Bridge (`workbench_bridge.py`)

将 V2 工作台上下文自动转换为 V8 输入：
- 根据 `stage` / `tags` / `conflict_intensity` 自动推断 `visibility`
- 根据 `visibility` 自动设置 `arena`, `stake`, `control_preference`
- 根据 `control_preference` 自动选择默认刀法
- 自动构建 villain/target/scene 三元组

---

## 6. 数据流全景

### 6.1 主数据流：从请求到推荐

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户请求 (React UI)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI Routes)                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ GET /api/v2/workbench/contexts                          │   │
│  │ POST /api/narrative/v4/preview                          │   │
│  │ POST /api/narrative/v6/simulate                         │   │
│  │ POST /api/narrative/v7/decision/preview                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service Layer — 版本化服务编排                                   │
│                                                                 │
│  NarrativeV2WorkbenchService.list_contexts()                    │
│  │                                                              │
│  ├─ 1. 获取上下文来源 (Online API → Local File → Imported → Live)│
│  │                                                              │
│  ├─ 2. 对每个上下文生成 V4 预览                                  │
│  │   └─ build_v4_workbench_preview()                            │
│  │      ├─ 状态转换 _v2_state_to_v4_context()                   │
│  │      ├─ 记忆融合 (relationship + feedback history)            │
│  │      ├─ Genre 自动校准                                        │
│  │      ├─ 角色验证                                              │
│  │      ├─ 提示词压缩                                            │
│  │      └─ build_v4_to_v3_bridge_result() → 候选情节             │
│  │                                                              │
│  ├─ 3. 对每个上下文生成 V8 预览                                  │
│  │   └─ build_v8_workbench_preview()                            │
│  │      ├─ 上下文 → VillainProfile + TargetProfile + Scene       │
│  │      ├─ select_knives() → 刀法选择                           │
│  │      ├─ render_flavor() → 风味渲染                            │
│  │      ├─ build_state_shift() → 状态变化                        │
│  │      └─ derive_transition_outcome() → 状态转移               │
│  │                                                              │
│  └─ 4. 返回聚合结果                                              │
│     {contexts: [...], source_diagnostics: {...}}                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Core Domain — 核心算法执行                                      │
│                                                                 │
│  alpha_autopilot:     FeatureMatrix → recommend_chapter()       │
│  alpha_autopilot_v3:  RetentionTargetFunction →                 │
│                       GenerationControlPlan                     │
│  alpha_autopilot_v4:  build_v4_to_v3_bridge_result()           │
│  narrative_v6:        ParallelPlotSimulationService.run()       │
│  narrative_v7:        DecisionFeedbackController.decide()       │
│  narrative_v8:        build_villain_feedback()                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 V7 决策预览数据流

```
UnifiedDecisionPreviewRequest
├── text (章节文本)
├── story_state (章节状态)
├── character_states (角色状态)
├── project_state (项目上下文)
├── benchmark_state (基准参数)
├── metric_overrides (指标覆盖)
└── override_confirmed (作者覆盖)

      ▼ (1) StoryStateMarketAdapter.adapt()

NarrativeMarketState
├── project_state (项目)
├── story_state (标准化)
├── benchmark_state (基准)
├── metric_state {T2..T9, A4..A6, W5..W6, P3}
├── kline_state {open, high, low, close, volume}
├── threshold_state {}
└── decision_state {last_composite}

      ▼ (2) NQMSampler.sample()

NQMVector + NarrativeMetricOHLCV

      ▼ (3) DecisionFeedbackController.decide()

DecisionResponse
├── decision_type (OBSERVE / ADD / REDUCE / RETRACE_REPAIR / STOP_LOSS / BREAKOUT_FOLLOW)
├── risk_level (P0 / P1 / P2)
├── route_id (R-01 ~ R-10)
├── reasons [...]
├── suggested_actions [...]
└── observe_next_metrics [...]

      ▼ (4) 组装返回

UnifiedDecisionPreviewResponse
├── market_state
├── vector
├── ohlcv
├── decision
└── defaults_applied [...]
```

### 6.3 V6 并行模拟数据流

```
ParallelSimulationRequest
├── narrative_seed (叙事种子)
│   ├── characters []
│   ├── relationship_triples []
│   ├── plot_events []
│   └── open_threads []
├── character_profiles []
├── macro_story_structure
├── retention_desire_vector
├── plot_unit_scaffold (可选)
├── strategies ["retention_first", "suspense_first", ...]
└── path_count

      ▼ ParallelPlotSimulationService.run()

对每个策略:
  ▼ _simulate_path()
  ├── 构建 plot_outline (基于策略 + scaffold)
  ├── 构建 six_step_scaffold_mapping
  ├── 构建 character_reactions
  ├── 构建 relationship_deltas
  ├── 构建 memory_deltas
  ├── 检查 consistency_issues
  ├── 评估 risk_flags
  └── score_simulation_path() → retention_score

      ▼ _rank_paths()

按 retention_score 降序排名
跳过 critical-consistency 路径

      ▼

ParallelPlotSimulationResult
├── paths [SimulationPath, ...]
├── winner_path_id
├── decision_summary
└── risk_flags (聚合)
```

---

## 7. 配置与可观测性

### 7.1 配置中心 (`Settings`)

通过 `pydantic_settings.BaseSettings` 统一管理，支持 `.env` / `.env.local`：

| 配置组 | 主要参数 |
|--------|----------|
| V4 Genre 自动校准 | `v4_genre_auto_min_samples`, `v4_genre_auto_decay`, `v4_genre_auto_bias_limit` |
| V4 可观测性 | `v4_observability_latency_p95_ms_threshold` (900ms), `v4_observability_error_rate_threshold` (8%) |
| V4 告警 | `v4_alert_remote_enabled`, `v4_alert_im_webhook_url`, `v4_alert_webhook_url` |
| V4 提示词压缩 | `v4_prompt_compress_threshold_tokens` (2000), `v4_prompt_compress_target_ratio` (0.3) |
| V6 图谱记忆 | `v6_graph_memory_max_in_memory_rows` (5000), `v6_graph_memory_chapter_window` (20) |
| V6 可观测性 | `v6_observability_latency_p95_ms_threshold` (1200ms) |
| V7 特性开关 | `v7_enabled`, `v7_opening_gate_enabled`, `v7_antipattern_guard_enabled`, `v7_deadlock_router_enabled` |
| V8 | `v8_workbench_enabled` |

### 7.2 运行时度量 (V7)

V7 的每个 API 调用都通过 `_execute_with_metrics()` 包装，记录：
- `route`: API 路径
- `status`: ok / error
- `latency_ms`: 延迟
- `error_type`: 异常类型
- `http_status`: HTTP 状态码
- `route_id`: 决策路由 ID

---

## 8. alpha-SRE 集成

### 8.1 alpha-SRE 核心能力

`alpha-SRE` 是独立的叙事可靠性控制面，提供：

| 模块 | 职责 |
|------|------|
| `state.py` | 叙事快照建模（11 个状态实体 + 交叉引用验证） |
| `events.py` | 事件与命令建模 |
| `replay.py` | 事件回放引擎（因果链验证） |
| `gate.py` | 一致性门禁（阻断/放行） |
| `integration.py` | 集成桥（Read/WriteBack/IncidentExport） |
| `incident.py` | 事故报告与分类 |
| `metrics.py` | SRE 度量计算 |
| `causal_validation.py` | 因果因验证 |
| `versioning.py` | Schema 版本兼容性检查 |

### 8.2 NarrativeSnapshot（叙事快照）

```
NarrativeSnapshot
├── snapshot_id, state_identity, schema_version, policy_version, visibility_version
├── characters:        Dict[str, CharacterState]
├── relationships:     Dict[str, RelationshipState]
├── memories:          Dict[str, MemoryState]
├── constraints:       Dict[str, ConstraintState]
├── world_rules:       Dict[str, WorldRuleState]
├── chapter_intents:   Dict[str, ChapterIntentState]
├── facts:             Dict[str, FactState]
├── beliefs:           Dict[str, BeliefState]
├── plot_threads:      Dict[str, PlotThreadState]
├── capabilities:      Dict[str, CapabilityState]
└── visibility_edges:  Dict[str, VisibilityEdgeState]
```

快照的 `validate()` 方法执行完整的交叉引用检查（悬挂引用检测）。

### 8.3 IntegrationBridge（集成桥）

```
alpha-autopilot                        alpha-SRE
─────────────                          ─────────
                ReadRequest
     ──────────────────────────────►
                ReadResponse
     ◄──────────────────────────────
       (验证 state_identity, schema_version, visibility_version)

                WriteBackRequest
     ──────────────────────────────►
       (command + snapshot + events)
                                       replay()
                                       gate.evaluate()
                                       build_drift_report()
                WriteBackResult
     ◄──────────────────────────────
       (ok, replay, gate, metrics, drift_report)

                IncidentExportRequest
     ──────────────────────────────►
                IncidentExportResponse
     ◄──────────────────────────────
       (failure_classification, regression_test_reference)
```

### 8.4 回放引擎 (`ReplayEngine`)

回放流程：
1. 验证 Command + Snapshot + Events
2. 克隆 Snapshot (`snapshot.clone()`)
3. 对每个 Event 按因果序执行:
   - 可见性检查（ObservationFrame）
   - 能力检查（CapabilityState）
   - 前置条件验证
   - 状态变更应用
4. 生成 ReplayResult:
   - `state_diff`, `constraint_diff`, `visibility_diff`, `causal_chain_diff`
   - `failure_classification` (post_state_mismatch / visibility_leak / belief_conflict / ...)
   - `missing_mechanism_candidates`

### 8.5 集成规划 (`integration_plan_alpha_autopilot.md`)

状态所有权划分：
- **alpha-autopilot 拥有**: chapter generation state, feature matrix, recommendation state
- **alpha-SRE 拥有**: narrative consistency state, world rules, visibility graph
- **共享**: character state, relationship state, plot threads

集成面：
1. **Pre-generation gate**: 生成前调用 SRE 读取快照、验证一致性
2. **Post-generation write-back**: 生成后调用 SRE 写回状态变更
3. **Incident export**: 一致性失败时导出事故报告

---

## 9. 前端架构

### React Dashboard (`ui-react/`)

**路由配置**:
- `/` → Dashboard 主页面
- `/v2/workbench` → V2 工作台页面

**Dashboard 面板组成**:

| 面板 | 数据来源 |
|------|----------|
| Hero + Sidebar | overview |
| MetricsGrid | overview |
| StoryStatePanel | narrativeSignals |
| MatrixPanel | matrixWeights |
| ChapterSummaryPanel | chapterSummary |
| TuningPanel | tuningWeights (可交互调整) |
| RecommendationsPanel | recommendations |
| TrainingResultPanel | trainingResult |
| ValueTrendPanel | trainingResult vs baseline |
| VersionComparePanel | trainingResult vs baseline |
| HistoryPanel | history API |
| FeedbackPanel | feedbackNotes |
| V4ObservabilityPanel | v4Observability |
| LogsPanel | logs |

**交互流**:
1. `handleAdjust()` → 调整权重 → `handlePreview()` → `fetchRecommendationPreview()` → 刷新推荐
2. `handleTrain()` → `runTraining()` → 更新训练结果 + 历史
3. `handleFeedback()` → `submitFeedback()` → 记录反馈 + 刷新历史
4. `handleExport()` → `exportHistory()` → 导出历史 JSON

---

## 10. 关键设计模式

### 10.1 优雅降级（Graceful Degradation）
每个版本的预览都有 `try/except` 包裹，失败时返回 `enabled=False` + `fallback_reason`，不影响其他版本。

### 10.2 版本隔离（Version Isolation）
- 每个版本有独立的 API 路由前缀 (`/api/narrative/v4/`, `/v6/`, `/v7/`)
- 每个版本有独立的服务层目录
- 核心算法包也按版本隔离 (`alpha_autopilot`, `alpha_autopilot_v3`, `alpha_autopilot_v4`)

### 10.3 桥接模式（Bridge Pattern）
- V4 Bridge: V3 留存 ↔ V4 工程化
- V8 Workbench Bridge: V2 上下文 ↔ V8 反派模型
- SRE IntegrationBridge: autopilot 生成 ↔ SRE 一致性

### 10.4 特性开关（Feature Flags）
通过 `Settings` 中的布尔开关控制各版本和子功能的启停：
```python
v7_enabled, v7_opening_gate_enabled, v7_antipattern_guard_enabled,
v7_deadlock_router_enabled, v8_workbench_enabled
```

### 10.5 可观测性优先（Observability First）
V4 和 V7 都内建了可观测性层（延迟/错误率/回退率监控），V4 还支持远程告警通道。

---

## 11. 总结

`alpha-autopilot` 是一个多层演进的叙事推荐系统，从 V1 的简单特征矩阵推荐，到 V8 的反派心理推演，每一层都在前一层的基础上增加新的能力维度：

```
V1:  我该推荐什么？            (特征矩阵)
V2:  我的上下文从哪来？         (工作台聚合)
V3:  读者会不会继续看？         (留存目标函数)
V4:  生产环境能跑吗？           (可观测 + 告警 + 记忆)
V6:  有几条可能的故事线？       (并行模拟 + 图谱)
V7:  故事质量量化得分是多少？   (NQM + 市场状态 + 决策路由)
V8:  反派下一步该怎么出手？     (刀法选择 + 状态账本 + 控制面转移)
SRE: 状态一致吗？能回放吗？    (快照 + 回放 + 门禁)
```

数据流的核心驱动逻辑是：**上下文聚合 → 多版本并行预览 → 量化评分 → 决策路由 → 状态追踪**，每一层都可以独立降级，整体系统通过三层治理结构保持可演进性。
