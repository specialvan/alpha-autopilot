# Alpha-Autopilot 生产控制系统 Wiki
 
> **版本**: v8.2 (codex/v8.2-control-surface-handoff)
> **仓库**: specialvan/alpha-autopilot
> **依赖**: Python >= 3.10 | FastAPI | Pydantic | Uvicorn
 
---
 
## 目录
 
1. [架构总览](#1-架构总览)
2. [目录结构与概念映射](#2-目录结构与概念映射)
3. [入口文件](#3-入口文件)
4. [核心模块 (Core)](#4-核心模块-core)
5. [规划器 (Planner)](#5-规划器-planner)
6. [控制器 (Controller)](#6-控制器-controller)
7. [代理层 (Agents / Services)](#7-代理层-agents--services)
8. [配置系统 (Configs)](#8-配置系统-configs)
9. [任务调度完整链路](#9-任务调度完整链路)
10. [策略选择机制](#10-策略选择机制)
11. [执行反馈链路](#11-执行反馈链路)
12. [故障恢复逻辑](#12-故障恢复逻辑)
13. [启动参数与运行方式](#13-启动参数与运行方式)
14. [配置文件示例](#14-配置文件示例)
15. [文件分类清单](#15-文件分类清单)
16. [模块依赖关系图](#16-模块依赖关系图)
17. [V7 决策规则参考](#17-v7-决策规则参考)
18. [V8 反派控制面参考](#18-v8-反派控制面参考)
19. [alpha-SRE 集成](#19-alpha-sre-集成)
 
---
 
## 1. 架构总览
 
Alpha-Autopilot 是一个**小说叙事推荐的生产自动驾驶系统**，核心功能是根据当前故事状态（StoryState）自动推荐最优叙事策略，并通过训练反馈持续优化决策权重矩阵。
 
### 三层治理结构
 
```
┌──────────────────────────────────────────────────────────────┐
│  Layer 3: Advanced Control (V7 NQM + V8 Villain Surface)     │
│  ├─ DecisionFeedbackController  (NQM 决策路由)               │
│  ├─ NQMSampler                  (29 维叙事质量采样)           │
│  ├─ OpeningGate / DeadlockRouter / AntiPatternRegistry       │
│  └─ V8 KnifeSelection + Ledger  (反派控制面)                 │
├──────────────────────────────────────────────────────────────┤
│  Layer 2: Incremental Engines (V3-V6)                        │
│  ├─ V3 Projection Bridge        (留存目标函数桥接)            │
│  ├─ V4 Bridge + Memory + Observability                       │
│  └─ V6 Parallel Simulation + GraphRAG                        │
├──────────────────────────────────────────────────────────────┤
│  Layer 1: Baseline (V1/V2)                                   │
│  ├─ ChapterPlanner              (章节推荐规划)               │
│  ├─ FeatureMatrix               (特征权重矩阵)               │
│  ├─ Trainer                     (训练反馈循环)               │
│  └─ HistoryRepository           (持久化存储)                 │
└──────────────────────────────────────────────────────────────┘
```
 
### 数据流概览
 
```
StoryState (输入)
    │
    ├──► ChapterPlanner.recommend()      ← Layer 1: 11 候选策略评分排序
    │       │
    │       └──► FeatureMatrix.score()   ← 上下文权重 (genre/tone/stage)
    │
    ├──► NQMSampler.sample()             ← Layer 3: 29 维指标采样
    │       │
    │       └──► DecisionFeedbackController.decide()
    │               │
    │               ├──► OpeningGate.run()         ← 开篇门禁
    │               ├──► DeadlockRouter.check()    ← 死锁路由
    │               ├──► AntiPatternRegistry.evaluate() ← 反模式检测
    │               └──► ThresholdBandEngine.classify_zone() ← 阈值带分类
    │
    ├──► V6 ParallelPlotSimulationService.run()  ← 多策略并行模拟
    │       │
    │       └──► GraphRAGRetriever.retrieve()     ← 图谱知识检索
    │
    └──► V8 build_villain_feedback()             ← 反派控制面
            │
            ├──► select_knives()                  ← 策略刀选择
            ├──► render_flavor()                  ← 风味渲染
            ├──► build_state_shift() / apply_state_shift() ← 状态变更
            └──► derive_transition_outcome()      ← 状态转移
```
 
---
 
## 2. 目录结构与概念映射
 
用户提出的 `core/`, `planner/`, `controller/`, `agents/`, `configs/` 在实际仓库中对应如下：
 
| 概念目录 | 实际路径 | 说明 |
|----------|----------|------|
| **core/** | `alpha_autopilot/` | 核心领域模型和引擎 |
| **planner/** | `alpha_autopilot/planner.py` | 章节规划器 |
| | `backend/app/services/narrative_v7/decision_controller.py` | V7 决策控制器 |
| | `backend/app/services/narrative_v6/parallel_simulation.py` | V6 并行模拟 |
| **controller/** | `backend/app/services/narrative_v7/` | NQM 决策反馈控制 |
| | `backend/app/services/narrative_v8/controller.py` | V8 反派控制面 |
| **agents/** | `backend/app/services/narrative/` | V1 服务层 |
| | `backend/app/services/narrative_v2/` | V2 服务层 |
| | `backend/app/services/narrative_v4/` | V4 桥接+可观测 |
| | `backend/app/services/narrative_v6/` | V6 并行模拟+GraphRAG |
| | `backend/app/services/narrative_v7/` | V7 NQM 控制器 |
| | `backend/app/services/narrative_v8/` | V8 反派控制面 |
| **configs/** | `backend/app/core/config.py` | pydantic_settings 配置中心 |
| | `backend/app/services/narrative_v7/decision_rules.default.json` | V7 决策规则 |
| | `.env` (可选) | 环境变量覆盖 |
 
### 实际目录结构
 
```
alpha-autopilot/
├── alpha_autopilot/              # [core] 核心领域引擎
│   ├── __init__.py               # 公共接口导出
│   ├── feature_matrix.py         # 特征权重矩阵 + 上下文权重
│   ├── planner.py                # ChapterPlanner 章节规划
│   ├── narrative.py              # 领域模型 (StoryState, etc.)
│   ├── trainer.py                # 训练反馈循环
│   ├── metrics.py                # 推荐价值指标
│   ├── recommend.py              # recommend_chapter() 入口函数
│   ├── repositories.py           # 持久化仓储 (File/DB/Fallback)
│   ├── storage.py                # ArtifactStore 文件管理
│   ├── training_log.py           # 训练日志
│   └── versioning.py             # MatrixSnapshot 版本管理
│
├── backend/
│   └── app/
│       ├── main.py               # [入口] FastAPI 应用工厂
│       ├── core/
│       │   └── config.py         # [configs] 60+ 配置参数
│       ├── api/routes/            # API 路由层
│       │   ├── dashboard.py
│       │   ├── recommendation.py
│       │   ├── recommendation_v2.py
│       │   ├── training.py
│       │   ├── feedback.py
│       │   ├── history.py
│       │   ├── narrative_v4.py
│       │   ├── narrative_v6.py
│       │   └── narrative_v7.py
│       └── services/             # [agents] 服务实现层
│           ├── narrative/          # V1 服务
│           ├── narrative_v2/       # V2 服务
│           ├── narrative_v4/       # V4 桥接+可观测
│           ├── narrative_v6/       # V6 并行模拟
│           ├── narrative_v7/       # V7 NQM 控制器
│           ├── narrative_v8/       # V8 反派控制面
│           └── observability_envelope.py
│
├── backend_app.py                # [入口] 独立 FastAPI 应用
├── recommend.py                  # [入口] 离线推荐脚本
├── train.py                      # [入口] 离线训练脚本
├── demo.py                       # [实验] 早期演示脚本
│
├── scripts/
│   ├── run_v4_production_cycle.py # 生产周期门禁脚本
│   └── run_layered_tests.py       # 分层测试运行器
│
├── pyproject.toml                # 项目依赖定义
└── samples.json                  # 训练样本数据
```
 
---
 
## 3. 入口文件
 
### 3.1 `backend/app/main.py` — FastAPI 应用工厂 (主入口)
 
**角色**: 生产环境主入口，创建并配置 FastAPI 应用实例。
 
```python
# backend/app/main.py
def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(dashboard_router)
    app.include_router(recommendation_router)
    app.include_router(recommendation_v2_router)
    app.include_router(workbench_v2_router)
    app.include_router(training_router)
    app.include_router(feedback_router)
    app.include_router(history_router)
    app.include_router(narrative_v4_router)
    app.include_router(narrative_v6_router)
    app.include_router(narrative_v7_router)
    return app
 
app = create_app()
```
 
**启动方式**:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
 
### 3.2 `backend_app.py` — 独立 FastAPI 应用
 
**角色**: 独立部署版入口，不依赖 backend/ 包结构。内嵌 `/api/dashboard`、`/api/recommendation/preview`、`/api/v2/recommendation/preview` 端点。
 
**启动方式**:
```bash
uvicorn backend_app:app --host 0.0.0.0 --port 8000
```
 
### 3.3 `recommend.py` — 离线推荐脚本
 
**角色**: 命令行调用核心推荐引擎，输出 JSON 结果。
 
```bash
python recommend.py
# 输出: {"state": {...}, "recommendations": [...]}
```
 
### 3.4 `train.py` — 离线训练脚本
 
**角色**: 从 `samples.json` 加载训练数据，执行模型训练，生成版本快照。
 
```bash
python train.py
# 输出: trained_weights, bias, history_len, summary, version
```
 
### 3.5 `scripts/run_v4_production_cycle.py` — 生产周期门禁
 
**角色**: 运行 V4 生产周期验收任务（T01-T04），生成验收报告。
 
```bash
python scripts/run_v4_production_cycle.py T01 --repo-root /path/to/repo
# 任务: T01(Baseline Gate), T02(Dual-Path Gate), T03(Runtime Metrics Gate), T04(Remote Alert Gate)
# 输出: artifacts/production_cycles/<task>/v4-<task>-<timestamp>.md
```
 
---
 
## 4. 核心模块 (Core)
 
核心模块位于 `alpha_autopilot/` 包下，通过 `__init__.py` 统一导出公共接口。
 
### 4.1 `narrative.py` — 领域模型
 
定义系统中所有核心数据结构。
 
| 数据类 | 字段 | 说明 |
|--------|------|------|
| `StoryState` | chapter_index, stage, mainline_progress, sideplot_progress, conflict_intensity, emotional_temperature, pacing_speed, foreshadowing_load, payoff_pressure, characters, tags | 当前故事状态快照 |
| `CharacterState` | name, presence, consistency_risk, relationship_tension, arc_progress | 角色状态 |
| `NarrativeCandidate` | action, delta, explanation | 叙事候选策略 |
| `RecommendationResult` | candidate, score, details | 推荐结果（含评分） |
 
**stage 取值**: `opening` → `middle` → `mid_late` → `late`
 
### 4.2 `feature_matrix.py` — 特征权重矩阵
 
评分引擎，根据上下文动态调整 7 维特征权重。
 
**7 维特征**:
 
| 特征名 | 说明 |
|--------|------|
| `conflict_push` | 冲突推进力 |
| `emotion_payoff` | 情感回报 |
| `hook_strength` | 钩子强度 |
| `continuity_safety` | 连续性安全 |
| `character_focus` | 角色聚焦 |
| `foreshadowing_value` | 伏笔价值 |
| `tempo_fit` | 节奏匹配 |
 
**上下文权重系统**:
 
```python
# 类型权重 (genre)
GENRE_WEIGHTS = {
    "suspense":  {"conflict_push": 1.3, "hook_strength": 1.4, ...},
    "romance":   {"emotion_payoff": 1.5, "character_focus": 1.3, ...},
    "power":     {"conflict_push": 1.4, "tempo_fit": 1.2, ...},
    "daily":     {"continuity_safety": 1.3, ...},
    "xianxia":   {"conflict_push": 1.3, "foreshadowing_value": 1.2, ...},
}
 
# 节奏权重 (tone)
TONE_WEIGHTS = {
    "fast":     {"tempo_fit": 1.3, "conflict_push": 1.2, ...},
    "balanced": {"continuity_safety": 1.1, ...},
    "slow":     {"emotion_payoff": 1.3, "character_focus": 1.2, ...},
}
 
# 阶段权重 (stage)
STAGE_WEIGHTS = {
    "opening":  {"hook_strength": 1.4, "conflict_push": 1.2, ...},
    "middle":   {"foreshadowing_value": 1.3, ...},
    "mid_late": {"tempo_fit": 1.3, "conflict_push": 1.2, ...},
    "late":     {"emotion_payoff": 1.4, "continuity_safety": 1.3, ...},
}
```
 
**评分公式**:
```python
def score(self, state: StoryState, features: Dict[str, float]) -> float:
    total = self.bias
    combined = self._contextual_weights(state)  # genre * tone * stage
    for name, value in features.items():
        total += combined.get(name, 0.0) * value
    total += 0.15 * state.conflict_intensity
    total += 0.10 * state.emotional_temperature
    total += 0.10 * state.mainline_progress
    total += self._tag_bonus(state)             # 标签奖励
    return total
```
 
### 4.3 `repositories.py` — 数据持久化
 
三种仓储实现 + 工厂函数：
 
```
HistoryRepository (抽象基类)
    ├── FileHistoryRepository    → JSON 文件存储
    ├── DbHistoryRepository      → SQLite 数据库存储
    └── FallbackHistoryRepository → DB 优先，文件兜底
```
 
**工厂函数**: `create_history_repository(store)` 自动创建 `FallbackHistoryRepository`
 
### 4.4 `versioning.py` — 版本管理
 
```python
@dataclass
class MatrixSnapshot:
    version: str          # e.g. "v003"
    created_at: str       # ISO 时间戳
    weights: Dict[str, float]
    bias: float
    sample_count: int
    notes: str
 
class VersionManager:
    def create_version(weights, bias, sample_count, notes) -> MatrixSnapshot
    def latest() -> MatrixSnapshot | None
```
 
### 4.5 `trainer.py` — 训练器
 
```python
class Trainer:
    matrix: FeatureMatrix
    history: List[Dict[str, float]]
    value_metrics: RecommendationValueMetrics
 
    def fit(samples: Iterable[TrainingSample]) -> FeatureMatrix
    # 遍历样本，对每个样本：
    #   1. ChapterPlanner.recommend(state) 获取候选
    #   2. 匹配 target_action 找到 chosen
    #   3. matrix.update_from_feedback(features, target_score, predicted_score, lr=0.08)
```
 
### 4.6 公共接口导出 (`__init__.py`)
 
```python
# alpha_autopilot/__init__.py 导出清单：
FeatureMatrix, ChapterPlanner, StoryState, NarrativeCandidate, RecommendationResult,
Trainer, TrainingSample, VersionManager, MatrixSnapshot, HistoryRepository,
FileHistoryRepository, DbHistoryRepository, FallbackHistoryRepository,
create_history_repository, ArtifactStore, TrainingLogger,
RecommendationMetricRecord, RecommendationValueMetrics,
recommend_chapter, preview_recommendations
```
 
---
 
## 5. 规划器 (Planner)
 
### 5.1 ChapterPlanner — 章节规划器
 
**文件**: `alpha_autopilot/planner.py`
 
ChapterPlanner 是 Layer 1 的核心调度器，负责从 11 个预定义候选策略中评分排序。
 
**11 个默认候选策略**:
 
| # | action | 说明 | 关键 delta |
|---|--------|------|-----------|
| 1 | `push_conflict` | 推进主线冲突 | conflict+0.18, mainline+0.10 |
| 2 | `escalate_pressure` | 升级压力 | conflict+0.22, emotion+0.14 |
| 3 | `focus_character` | 聚焦角色 | character_focus+0.20 |
| 4 | `deepen_relationship` | 深化关系 | emotion+0.16, character+0.12 |
| 5 | `plant_foreshadow` | 埋设伏笔 | foreshadowing+0.20, hook+0.08 |
| 6 | `open_new_branch` | 开新支线 | sideplot+0.15, hook+0.12 |
| 7 | `deliver_payoff` | 兑现回报 | payoff-0.18, emotion+0.20 |
| 8 | `reverse_twist` | 反转 | conflict+0.15, hook+0.18 |
| 9 | `adjust_pacing` | 调节节奏 | pacing+0.12 |
| 10 | `stabilize_continuity` | 稳定连续性 | continuity+0.18 |
| 11 | `close_branch` | 关闭支线 | sideplot-0.12, payoff-0.08 |
 
**推荐流程**:
```python
def recommend(self, state: StoryState) -> List[RecommendationResult]:
    results = []
    for candidate in DEFAULT_CANDIDATES:
        features = self.extract_features(state, candidate)   # 提取 7 维特征
        score = self.matrix.score(state, features)            # 上下文加权评分
        results.append(RecommendationResult(candidate, score, features))
    return sorted(results, key=lambda x: x.score, reverse=True)
```
 
**特征提取** (`extract_features`):
```python
def extract_features(self, state, candidate) -> Dict[str, float]:
    return {
        "conflict_push":       delta["conflict_intensity"] + 0.1 * state.conflict_intensity,
        "emotion_payoff":      delta["emotional_temperature"] + 0.08 * state.emotional_temperature,
        "hook_strength":       delta.get("hook_strength", 0) + 0.12 * (1 - state.payoff_pressure),
        "continuity_safety":   1.0 - abs(delta.get("continuity_risk", 0)) * 0.5,
        "character_focus":     delta.get("character_focus", 0) + 0.1,
        "foreshadowing_value": delta.get("foreshadowing_load", 0) + 0.08 * state.foreshadowing_load,
        "tempo_fit":           1.0 - abs(delta.get("pacing_speed", 0) - state.pacing_speed) * 0.6,
    }
```
 
### 5.2 V7 DecisionFeedbackController — NQM 决策控制器
 
**文件**: `backend/app/services/narrative_v7/decision_controller.py`
 
V7 的核心控制器，基于 NQM (Narrative Quality Metric) 向量做出干预决策。
 
**决策路由表**:
 
| 路由 | 条件 | 决策类型 | 风险等级 | 动作 |
|------|------|----------|----------|------|
| R-OVERRIDE | author 主动确认 | OBSERVE | P2 | 继续生成 |
| R-04 | 前 N 章 T8 < opening_gate | STOP_LOSS | P0 | 暂停+开篇诊断 |
| R-08 | antipattern_critical=true | STOP_LOSS | P0 | 强制干预+回滚 |
| R-05 | deadlock_triggered=true | RETRACE_REPAIR | P1 | 并行路径注入 |
| R-06 | T4 ≤ tail_hook_zero | ADD | P1 | 注入钩子 |
| R-07 | t9_delta_5chapters < threshold | RETRACE_REPAIR | P1 | 恢复反派压力 |
| R-09 | a6_sigma_delta < -2.0 | REDUCE | P1 | 重校 IP 风味 |
| R-10 | death_chapter && W6 < 0.4 | RETRACE_REPAIR | P1 | 情感回报修复 |
| R-01 | composite < L threshold | STOP_LOSS | P0 | 锚定事实+强制修复 |
| R-02 | L < composite < H | RETRACE_REPAIR | P2 | 弹性注入 |
| R-02B | composite 接近 H | BREAKOUT_FOLLOW | P2 | 突破确认 |
| R-03 | composite > H | OBSERVE | P2 | 继续生成 |
 
**决策类型枚举**:
- `STOP_LOSS`: 止损（P0 级别，立即停止生成）
- `RETRACE_REPAIR`: 回溯修复
- `ADD`: 添加元素
- `REDUCE`: 削减元素
- `BREAKOUT_FOLLOW`: 突破跟随
- `OBSERVE`: 观察（不干预）
 
---
 
## 6. 控制器 (Controller)
 
### 6.1 NQM 采样器 — `NQMSampler`
 
**文件**: `backend/app/services/narrative_v7/nqm_sampler.py`
 
从章节文本中提取 **29 维** NQM 指标。
 
**指标层次**:
 
| 层 | 指标 | 权重 | 说明 |
|----|------|------|------|
| **P 层 (7)** | P1-P7 | 0.20 | 基础质量（节奏均衡、对话比例、冲突密度、角色数量、倒计时信号、对话身份、POV 一致性） |
| **T 层 (10)** | T1-T10 | 0.30 | 张力指标（结构信号、冲突密度、奖励密度、钩子密度、兴奋值、随机奖励、社交密度、开篇钩子、反派压力、感官密度） |
| **W 层 (6)** | W1-W6 | 0.15 | 合规/安全指标（规则违反、信息速率、钩子密度、冲突密度、冲突层次、死亡回报） |
| **A 层 (6)** | A1-A6 | 0.35 | 对齐指标（质量代理、角色覆盖、因果信号、留存对齐、反转信号、IP 风味走廊） |
 
**综合评分**:
```python
composite = P_avg * 0.20 + T_avg * 0.30 + W_avg * 0.15 + A_avg * 0.35
```
 
### 6.2 阈值带引擎 — `ThresholdBandEngine`
 
**文件**: `backend/app/services/narrative_v7/threshold_band.py`
 
将 NQM composite 映射到三个操作区间：
 
```
composite
    │
    ▼
[0.0 ─── stop_loss ─── L(0.52) ─── support ─── H(0.78) ─── resistance ─── breakout ─── 1.0]
         │                │                        │                          │
   hard_intervention  elastic_injection      free_generation          breakout_confirm
```
 
- **hard_intervention** (composite < L=0.52): 强制干预
- **elastic_injection** (L ≤ composite ≤ H=0.78): 弹性注入
- **free_generation** (composite > H=0.78): 自由生成
 
**K 线模式识别**:
```python
def detect_pattern(ohlcv_open, ohlcv_close, ohlcv_volume, band) -> str:
    # volume_breakdown | support_breakdown | confirmed_breakout |
    # thin_breakout | resistance_test | support_retest | range_trading
```
 
### 6.3 开篇门禁 — `OpeningGate`
 
**文件**: `backend/app/services/narrative_v7/opening_gate.py`
 
对开篇文本进行 T8 评分门禁检查。
 
**T8 评分公式**:
```python
T8 = 0.28 * conflict_signal + 0.24 * protagonist_focus
   + 0.24 * target_clarity   + 0.24 * info_gap
```
 
**毒点检测** (10 种反模式):
- 背景大科普、碎念独白、无意义日常、逻辑自相矛盾、圣母过载
- 人物过载、梦境回忆开场、系统刷屏、文笔堆砌、目标缺失
 
**门禁规则**: T8 < 0.60 → 阻断（除非 `allow_override=true`）
 
### 6.4 死锁路由器 — `DeadlockRouter`
 
**文件**: `backend/app/services/narrative_v7/deadlock_router.py`
 
检测连续 3 章的叙事死锁状态。
 
**触发条件**: 最近 3 章均满足 `t2_slope < 0.05 AND t4 < 0.2 AND p3 < 0.4`
 
**路由策略选择**:
```python
if avg_p3 < 0.25:  → "parallel_world_variable_injection"  # 平行世界变量注入
if avg_t4 < 0.10:  → "foreshadow_recycle"                  # 伏笔回收
else:              → "goal_backtrace"                       # 目标回溯
```
 
### 6.5 反模式注册表 — `AntiPatternRegistry`
 
**文件**: `backend/app/services/narrative_v7/antipattern_registry.py`
 
检测 7 种叙事反模式：
 
| 反模式 | 触发指标 | 说明 |
|--------|----------|------|
| POV_POLLUTION | P7 < 0.45 | POV 一致性下降 |
| DIALOGUE_AWKWARD | P6 < 0.50 | 对话身份系数过低 |
| LOGIC_BREAK | W1 < 0.45 | 世界规则一致性下降 |
| PUPPET_PROTAGONIST | P3 < 0.35 | 主角被动（傀儡化） |
| VILLAIN_NERF | T9 < 0.50 | 反派压力下降（弱化） |
| PACING_DRAG | T2 < 0.35 | 张力梯度过弱 |
| SELF_INDULGENCE_TOPIC | A6 < 0.45 | IP 风味走廊偏移 |
 
**严重度升级**: WARNING (连续 1 次) → ERROR (连续 2 次) → CRITICAL (连续 ≥ 3 次)
 
### 6.6 V8 反派控制面
 
**文件**: `backend/app/services/narrative_v8/controller.py`
 
V8 控制面是一个完整的反派行为决策系统。
 
**核心流程** (`build_villain_feedback`):
```
VillainProfile + TargetProfile + SceneContext
    │
    ├── select_knives()          → 策略刀选择 (scored_fit | fallback)
    ├── render_flavor()          → 风味渲染
    ├── build_future_hooks()     → 未来钩子生成
    ├── build_state_shift()      → 状态账本变更
    ├── build_explanation()      → 决策解释
    ├── derive_transition()      → 状态转移
    └── build_risk_if_exposed()  → 暴露风险评估
    │
    ▼
VillainFeedbackPacket + LedgerSnapshot + next_control_state
```
 
---
 
## 7. 代理层 (Agents / Services)
 
### 7.1 V1 叙事服务 (`backend/app/services/narrative/`)
 
| 文件 | 类/函数 | 职责 |
|------|---------|------|
| `dashboard_service.py` | `build_dashboard()` | 构建仪表盘数据 |
| `preview_service.py` | `build_preview()` | 推荐预览 |
| `training_service.py` | `NarrativeTrainingService` | 训练服务（含 V3 Projection 桥接） |
| `feedback_service.py` | `NarrativeFeedbackService` | 反馈记录服务 |
| `history_service.py` | - | 历史查询服务 |
| `history_export_service.py` | - | 历史导出服务 |
| `state_builder.py` | `base_state()` | 默认状态构造 |
| `write_service.py` | `NarrativeWriteService` | 统一写入服务 |
| `v3_projection_bridge.py` | 桥接函数 | V3 留存投射数据转换 |
| `schemas.py` | 数据结构 | 请求/响应模型 |
 
### 7.2 V4 桥接+可观测 (`backend/app/services/narrative_v4/`)
 
| 文件 | 职责 |
|------|------|
| `bridge.py` | V4 桥接负载构建 (含记忆) |
| `memory_store.py` | V4 记忆存储 |
| `emotion_slider.py` | 情感滑块映射 |
| `observability.py` | V4 可观测快照 |
| `alert_channel.py` | 告警路由 (本地+远端) |
| `relationship_graph.py` | 关系图谱导出 |
| `character_validation.py` | 角色验证 |
| `prompt_compressor.py` | Prompt 压缩 |
 
### 7.3 V6 并行模拟 (`backend/app/services/narrative_v6/`)
 
| 文件 | 类 | 职责 |
|------|-----|------|
| `parallel_simulation.py` | `ParallelPlotSimulationService` | 多策略并行模拟 |
| `graph_rag.py` | `GraphRAGRetriever` | 图谱知识检索 |
| `graph_memory_store.py` | - | 图谱记忆存储 |
| `group_memory.py` | - | 群体记忆管理 |
| `character_interview.py` | - | 角色访谈 |
| `character_parameterizer.py` | - | 角色参数化 |
| `conflict_probe.py` | - | 冲突探测 |
| `event_injection.py` | - | 事件注入 |
| `scoring.py` | - | 模拟路径评分 |
| `seed_extractor.py` | - | 叙事种子提取 |
| `state_store.py` | - | 状态存储 |
| `observability.py` | - | V6 可观测 |
 
**并行模拟默认策略**:
- `retention_first`: 留存优先（开场直接给爽点）
- `suspense_first`: 悬念优先（线索半曝光+误导）
- `relationship_burst`: 关系爆发（关系位移+立场冲突）
 
### 7.4 V7 NQM 控制 (`backend/app/services/narrative_v7/`)
 
| 文件 | 类 | 职责 |
|------|-----|------|
| `decision_controller.py` | `DecisionFeedbackController` | 核心决策路由 |
| `nqm_sampler.py` | `NQMSampler` | 29 维 NQM 采样 |
| `market_state_adapter.py` | `StoryStateMarketAdapter` | 故事状态→市场状态适配 |
| `threshold_band.py` | `ThresholdBandEngine` | 阈值带分类 |
| `opening_gate.py` | `OpeningGate` | 开篇门禁 |
| `deadlock_router.py` | `DeadlockRouter` | 死锁路由 |
| `antipattern_registry.py` | `AntiPatternRegistry` | 反模式检测 |
| `decision_rules.py` | `DecisionRuleSet` | 决策规则加载（支持热重载） |
| `ohlcv.py` | - | K 线数据结构 |
| `pacing_controller.py` | - | 节奏控制 |
| `emotion_satisfaction.py` | - | 情感满足度 |
| `expectation_debt.py` | - | 期望债务 |
| `loop_structure.py` | - | 循环结构 |
| `contract_guard.py` | - | 合约守卫 |
| `benchmark_library.py` | - | 基准库 |
| `benchmark_store.py` | - | 基准存储 |
| `benchmark_refit.py` | - | 基准重拟合 |
| `observability.py` | - | V7 可观测 |
 
### 7.5 V8 反派控制面 (`backend/app/services/narrative_v8/`)
 
| 文件 | 职责 |
|------|------|
| `controller.py` | `build_villain_feedback()` 主控函数 |
| `knife_library.py` | 10 把策略刀定义 + 兼容性图 |
| `selection.py` | 策略刀选择 + 评分 |
| `constraints.py` | 硬约束过滤 |
| `fallbacks.py` | 降级策略 (无可用刀时) |
| `transitions.py` | 状态转移推导 |
| `transition_policy.py` | 转移策略 |
| `ledger.py` | 状态账本 (关系/叙事/心理/钩子) |
| `flavor.py` | 风味渲染 + 解释生成 |
| `schemas.py` | V8 数据模型 |
| `workbench_bridge.py` | Workbench 预览桥接 |
 
---
 
## 8. 配置系统 (Configs)
 
### 8.1 主配置 — `backend/app/core/config.py`
 
基于 `pydantic_settings.BaseSettings`，支持环境变量覆盖。
 
```python
class Settings(BaseSettings):
    # === 应用基础 ===
    app_name: str = "alpha-autopilot api"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
 
    # === V4 特性开关 ===
    v4_enabled: bool = True
    v4_memory_enabled: bool = True
 
    # === V6 特性开关 ===
    v6_simulation_enabled: bool = True
    v6_graph_rag_enabled: bool = True
    v6_graph_rag_top_k: int = 5
    v6_group_memory_enabled: bool = True
 
    # === V7 特性开关 ===
    v7_enabled: bool = True
    v7_opening_gate_enabled: bool = True
    v7_antipattern_guard_enabled: bool = True
    v7_deadlock_router_enabled: bool = True
 
    # === V8 特性开关 ===
    v8_workbench_enabled: bool = True
 
    # === 可观测性阈值 ===
    v4_observability_enabled: bool = True
    v4_observability_window_limit: int = 200
    v4_runtime_latency_p95_threshold_ms: float = 250.0
    v4_runtime_error_rate_threshold: float = 0.05
    v4_runtime_fallback_rate_threshold: float = 0.20
 
    # === 告警与远端路由 ===
    v4_remote_alert_enabled: bool = False
    v4_remote_alert_endpoint: str = ""
    v4_alert_cooldown_seconds: int = 300
 
    # === 压缩与验证 ===
    v4_compress_prompt: bool = True
    v4_compress_max_tokens: int = 2048
    v4_character_validation_enabled: bool = True
```
 
### 8.2 V7 决策规则 — `decision_rules.default.json`
 
**文件**: `backend/app/services/narrative_v7/decision_rules.default.json`
 
可热重载的 JSON 配置，支持通过环境变量 `AA_V7_DECISION_RULES_JSON` 指定自定义路径。
 
```json
{
    "early_chapter_limit": 3,
    "opening_t8_gate": 0.60,
    "tail_hook_zero_threshold": 0.01,
    "antagonist_drop_threshold": -0.20,
    "a6_sigma_lower": -2.0,
    "w6_floor": 0.40,
    "elastic_breakout_margin": 0.02
}
```
 
**热重载机制**: `DecisionRuleSet` 在每次 `current()` 调用时检查文件 mtime_ns，变化时自动重新加载并合并默认值。
 
---
 
## 9. 任务调度完整链路
 
### 9.1 Layer 1: 基础推荐链路
 
```
用户请求 (POST /api/recommendation/preview)
    │
    ▼
preview_service.build_preview()
    │
    ├── state_builder.base_state()           → 构造 StoryState
    │
    ├── recommend_chapter(state, matrix)      → 调用核心推荐
    │       │
    │       └── ChapterPlanner.recommend(state)
    │               │
    │               ├── for candidate in DEFAULT_CANDIDATES (11个):
    │               │       features = extract_features(state, candidate)
    │               │       score = matrix.score(state, features)
    │               │
    │               └── sorted(results, key=score, reverse=True)
    │
    └── 返回 List[RecommendationResult]
```
 
### 9.2 Layer 2: 训练反馈链路
 
```
POST /api/training
    │
    ▼
NarrativeTrainingService.train()
    │
    ├── _default_samples()                    → 4 个内置样本
    │
    ├── _projection_samples()                 → V3 Projection 桥接样本
    │       │
    │       └── load_matrix_projection()      → 从 artifacts/v3/ 加载
    │           build_training_samples_from_projection() → 转换为 TrainingSample
    │
    ├── Trainer().fit(all_samples)
    │       │
    │       ├── for sample in samples:
    │       │       candidates = planner.recommend(sample.state)
    │       │       chosen = match(target_action) or candidates[0]
    │       │       matrix.update_from_feedback(features, target, predicted, lr=0.08)
    │       │
    │       └── 返回更新后的 FeatureMatrix
    │
    ├── versioner.create_version()            → 创建 MatrixSnapshot
    │
    ├── writer.persist_training()             → 持久化训练日志
    │
    └── writer.persist_value_metric()         → 持久化价值指标
```
 
### 9.3 Layer 3: V7 NQM 决策链路
 
```
POST /api/v7/narrative/decision
    │
    ▼
StoryStateMarketAdapter.adapt(payload)
    │
    ├── _normalize_story_state()              → 规范化故事状态
    ├── _resolve_project_state()              → 解析项目状态
    ├── _resolve_benchmark_state()            → 解析基准参数
    ├── _resolve_metric_state()               → 解析指标状态 (含 override)
    └── _resolve_decision_state()             → 计算 composite
    │
    ▼
NQMSampler.sample(text, ...)
    │
    ├── _keyword_density() × 5 类关键词      → 冲突/钩子/奖励/社交/感官
    ├── 计算 P1-P7                            → 基础质量层
    ├── 计算 T1-T10                           → 张力层
    ├── 计算 W1-W6                            → 合规层
    ├── 计算 A1-A6                            → 对齐层
    └── _composite()                          → 加权合成
    │
    ▼
DecisionFeedbackController.decide(NQMVector, MarketState)
    │
    ├── 优先级 1: author override             → R-OVERRIDE (OBSERVE)
    ├── 优先级 2: opening gate (T8)           → R-04 (STOP_LOSS)
    ├── 优先级 3: antipattern critical        → R-08 (STOP_LOSS)
    ├── 优先级 4: deadlock                    → R-05 (RETRACE_REPAIR)
    ├── 优先级 5: tail hook zero              → R-06 (ADD)
    ├── 优先级 6: antagonist drop             → R-07 (RETRACE_REPAIR)
    ├── 优先级 7: IP flavor loss              → R-09 (REDUCE)
    ├── 优先级 8: death payoff                → R-10 (RETRACE_REPAIR)
    ├── 优先级 9: threshold zone
    │       ├── hard_intervention             → R-01 (STOP_LOSS)
    │       ├── elastic + near breakout       → R-02B (BREAKOUT_FOLLOW)
    │       ├── elastic                       → R-02 (RETRACE_REPAIR)
    │       └── free                          → R-03 (OBSERVE)
    │
    └── 返回 DecisionResponse(NarrativeDecision)
```
 
### 9.4 Layer 3: V8 反派控制链路
 
```
POST /api/v2/workbench/contexts (with v8_enabled=true)
    │
    ▼
workbench_bridge.build_v8_workbench_preview(context)
    │
    ├── _build_v8_preview_input(context)      → 构造 V8 输入
    │       ├── 推导 visibility (public/private)
    │       ├── 推导 arena, stake, control_preference
    │       └── 构造 VillainProfile + TargetProfile + SceneContext
    │
    ▼
controller.build_villain_feedback(payload)
    │
    ├── select_knives(villain, target, scene)
    │       │
    │       ├── build_candidate_knife_ids()   → 候选刀清单
    │       ├── evaluate_knife_rejection()    → 硬约束过滤
    │       ├── _score_candidate()            → 适配度评分
    │       │       ├── preferred_palette      +0.30
    │       │       ├── arena_fit              +0.12
    │       │       ├── pressure_type_fit      +0.10
    │       │       ├── vulnerability_match    +0.08~0.12
    │       │       ├── flavor_profile_fit     +0.14
    │       │       └── observer_support       +0.00~0.14
    │       │
    │       ├── PRIMARY_SELECTION_THRESHOLD    = 0.55
    │       ├── SECONDARY_SELECTION_THRESHOLD  = 0.68
    │       └── evaluate_compatibility_conflict() → 兼容性检查
    │
    ├── render_flavor()                       → 风味渲染
    ├── build_future_hooks()                  → 未来钩子
    ├── build_state_shift()                   → 状态账本变更
    │       ├── relationship: debt_delta, dependency_delta, trust_delta
    │       ├── narrative: explanation_control_delta, witness_alignment_delta
    │       ├── psychological: identity_destabilization_delta, shame_load_delta
    │       └── hook: planted_hooks
    │
    ├── apply_state_shift()                   → 应用变更到快照
    │       └── MAX_HIGH_MAGNITUDE_DELTAS = 2 (每场景最多 2 个高幅度变更)
    │
    ├── build_explanation()                   → 决策解释
    ├── derive_transition_outcome()           → 状态转移
    └── build_risk_if_exposed()               → 暴露风险
```
 
---
 
## 10. 策略选择机制
 
### 10.1 Layer 1: 11 候选策略的特征矩阵评分
 
评分 = `bias + sum(contextual_weight[i] * feature[i]) + state_bonus + tag_bonus`
 
上下文权重 = `base_weight * genre_weight * tone_weight * stage_weight`
 
### 10.2 V6: 多策略并行模拟
 
```python
class ParallelPlotSimulationService:
    def run(request):
        # 1. 解析策略列表 (默认 3 种)
        strategies = resolve_strategies(request)
 
        # 2. 对每种策略并行模拟
        for strategy in strategies:
            path = simulate_path(strategy, request)
            # 生成: plot_outline, six_step_mapping, character_reactions
            #        relationship_deltas, memory_deltas, retention_score
 
        # 3. 排名并选择胜者
        winner = rank_paths(paths)  # 按 retention_score 排序
        # 如果顶级路径有 critical-consistency 风险，选下一个安全候选
 
        # 4. 构建决策摘要
        return ParallelPlotSimulationResult(paths, winner, decision_summary)
```
 
### 10.3 V7: NQM 区间决策
 
```
NQM Composite Score
    │
    ├── < 0.52 (L) ──────► hard_intervention
    │                        → STOP_LOSS / 强制修复
    │
    ├── 0.52 ~ 0.78 ─────► elastic_injection
    │       │
    │       ├── 接近 H ──► BREAKOUT_FOLLOW
    │       └── 其他 ────► RETRACE_REPAIR (弹性注入)
    │
    └── > 0.78 (H) ──────► free_generation
                             → OBSERVE (继续生成)
```
 
### 10.4 V8: 策略刀选择
 
**10 把策略刀**:
 
| ID | 名称 | 核心机制 | 最佳场景 |
|----|------|----------|----------|
| `self_image_feeding` | 自我形象喂养 | 定义体面 → 维护表演 | 朝堂/世家 |
| `high_ground_pity` | 高位怜悯 | 宽容姿态 → 低位叙事 | 朝堂/门派 |
| `fake_vulnerability` | 伪造脆弱 | 可控脆弱 → 保护欲 | 情寨/师徒 |
| `delayed_asking` | 延迟索取 | 安全感 → 延迟回收 | 师徒/资源 |
| `relationship_withdrawal` | 关系抽离 | 撤回供给 → 失衡追索 | 情寨/师徒 |
| `old_wound_trigger` | 旧伤触发 | 旧伤回路 → 误判重演 | 师徒/世家 |
| `memory_reframing` | 记忆改写 | 重释过去 → 改写判断 | 师徒/门派 |
| `courteous_humiliation` | 礼貌羞辱 | 规训外壳 → 公开降位 | 朝堂/门派 |
| `gentle_absorption` | 温柔收编 | 接纳保护 → 依赖轨道 | 情寨/师徒 |
| `baited_concession` | 诱饵让步 | 有限退让 → 更深承诺 | 朝堂/资源 |
 
**分类**:
- 公共压力刀: `self_image_feeding`, `courteous_humiliation`, `high_ground_pity`
- 私密压力刀: `fake_vulnerability`, `gentle_absorption`, `relationship_withdrawal`
- 资源压力刀: `baited_concession`, `delayed_asking`
- 记忆压力刀: `old_wound_trigger`, `memory_reframing`
 
---
 
## 11. 执行反馈链路
 
### 11.1 反馈记录
 
```
POST /api/feedback
    │
    ├── action, target, predicted, feedback, notes
    │
    ▼
NarrativeFeedbackService.record_feedback()
    │
    ├── 判断是否需要版本修正:
    │       abs(target - predicted) > 0.12 OR feedback < 0.8
    │       → 创建新 MatrixSnapshot (feedback correction)
    │
    ├── TrainingLogger.record()                → 记录训练日志
    ├── writer.persist_training()              → 持久化训练数据
    ├── writer.persist_value_metric()          → 持久化价值指标
    │       ├── accepted = feedback >= 0.8
    │       ├── chapter_quality = feedback
    │       ├── followup_writeability = feedback * 0.9 + 0.05
    │       └── continuity_delta = target - predicted
    │
    └── 返回 FeedbackResult(value_summary, top_actions)
```
 
### 11.2 训练反馈循环
 
```
Trainer.fit(samples)
    │
    for sample in samples:
    │   candidates = planner.recommend(sample.state)
    │   chosen = match(sample.target_action)
    │   error = sample.target_score - chosen.score
    │   │
    │   └── matrix.update_from_feedback(
    │           features=chosen.details,
    │           target=sample.target_score,
    │           predicted=chosen.score,
    │           lr=0.08
    │       )
    │       │
    │       └── for name, value in features.items():
    │               weights[name] += lr * error * value
    │           bias += lr * error
    │
    └── 返回更新后的 FeatureMatrix
```
 
---
 
## 12. 故障恢复逻辑
 
### 12.1 FallbackHistoryRepository — 数据持久化降级
 
```python
class FallbackHistoryRepository(HistoryRepository):
    """DB 优先，File 兜底"""
 
    def read_training_logs(self):
        combined = []
        if self.db_repo is not None:
            try:
                combined.extend(self.db_repo.read_training_logs())
            except Exception:
                pass  # DB 失败静默降级
        combined.extend(self.file_repo.read_training_logs())  # File 始终兜底
        return combined
```
 
**降级模式**:
- 正常: SQLite DB 读写
- DB 异常: 静默降级到 JSON 文件读写
- 两者合并: 读取时合并 DB + File 数据
 
### 12.2 V4 告警路由降级
 
```
route_v4_observability_alerts(snapshot)
    │
    ├── 远端路由 (v4_remote_alert_enabled=true)
    │       ├── 发送到 v4_remote_alert_endpoint
    │       ├── 冷却期: v4_alert_cooldown_seconds (默认 300s)
    │       └── 远端失败 → 降级到本地 sink
    │
    └── 本地 sink (默认)
            └── 写入本地日志
```
 
### 12.3 V6 并行模拟降级
 
```python
# 单条路径失败不影响其他路径
for strategy in strategies:
    try:
        path = simulate_path(strategy, request)
        paths.append(path)
    except Exception as exc:
        paths.append(SimulationPath(
            status="failed",
            error_message=str(exc),
            risk_flags=["path_generation_failed"]
        ))
 
# 全部路径失败时
if winner_path_id is None:
    decision_summary = "Fallback to baseline recommendation is required."
 
# 顶级路径有严重一致性风险时
for path in ranked:
    if "critical-consistency" in path.risk_flags:
        continue  # 跳过，选下一个安全候选
    return path.path_id
```
 
### 12.4 V7 决策规则热重载降级
 
```python
class DecisionRuleSet:
    def _load_if_needed(self, *, force: bool):
        if not self._config_path.exists():
            self._cached_rules = dict(_DEFAULT_RULES)  # 文件不存在 → 用默认值
            return
 
        loaded = self._safe_load_rules(self._config_path)
        merged = dict(_DEFAULT_RULES)
        merged.update(loaded)  # 合并：缺失字段自动填充默认值
        self._cached_rules = merged
 
    def _safe_load_rules(self, path):
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}  # JSON 解析失败 → 返回空，使用默认值
```
 
### 12.5 V8 策略刀降级
 
```python
# 无可用策略刀时的降级
if not viable_candidates:
    return KnifeSelectionResult(
        decision=build_fallback_decision(
            scene=scene,
            rejected_knives=rejections,
            fallback_reason="no knife survived hard filters"
        )
    )
 
# 降级动作选择
def choose_fallback_action(scene):
    if scene.visibility == "public":
        if scene.current_control_state == "distrusted":
            return "reduce_exposure"
        return "defer_to_public_mask"
    if scene.current_control_state in REPAIR_OR_RECOVERY_STATES:
        return "hold_position"
    return "gather_information"
 
# 降级恢复模式
recovery_modes = {
    "reduce_exposure":       "lower_intensity",
    "defer_to_public_mask":  "retreat_to_safer_role",
    "hold_position":         "re_establish_decorum",
    "gather_information":    "change_scene",
}
```
 
### 12.6 V8 状态账本安全约束
 
```python
LEDGER_LOW = -3        # 状态值下限
LEDGER_HIGH = 3        # 状态值上限
MAX_HIGH_MAGNITUDE_DELTAS = 2  # 每场景最多 2 个高幅度变更
 
def apply_state_shift(snapshot, shift):
    if count_high_magnitude_deltas(shift) > MAX_HIGH_MAGNITUDE_DELTAS:
        raise ValueError("at most two high-magnitude deltas are allowed per scene")
    # 所有状态值 clamp 到 [-3, 3] 范围
```
 
### 12.7 GraphRAG 检索降级
 
```python
class GraphRAGRetriever:
    def retrieve(self, request):
        hits = [...]  # 词法匹配
        if not hits:
            fallback_used = True
            fallback_reason = "no-lexical-hit"
            hits = self._fallback_hits(candidates, top_k, ...)
            # 按 confidence + node_type_boost 排序
```
 
---
 
## 13. 启动参数与运行方式
 
### 13.1 FastAPI 后端启动
 
```bash
# 开发模式
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
 
# 生产模式
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
 
# 独立入口
uvicorn backend_app:app --host 0.0.0.0 --port 8000
```
 
### 13.2 离线脚本
 
```bash
# 离线推荐
python recommend.py
 
# 离线训练
python train.py
 
# V4 生产周期门禁
python scripts/run_v4_production_cycle.py T01  # Baseline Gate
python scripts/run_v4_production_cycle.py T02  # Dual-Path Gate
python scripts/run_v4_production_cycle.py T03  # Runtime Metrics Gate
python scripts/run_v4_production_cycle.py T04  # Remote Alert Gate
python scripts/run_v4_production_cycle.py T01 --output /custom/path/report.md
```
 
### 13.3 环境变量
 
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AA_V7_DECISION_RULES_JSON` | V7 决策规则 JSON 路径 | `decision_rules.default.json` |
| 所有 `Settings` 字段 | 可通过环境变量覆盖 (大写+下划线) | 见 config.py |
 
### 13.4 依赖安装
 
```bash
pip install -e .
# 或
pip install fastapi pydantic pydantic-settings uvicorn
```
 
---
 
## 14. 配置文件示例
 
### 14.1 环境变量配置 (.env)
 
```env
# === 应用基础 ===
APP_NAME=alpha-autopilot api
APP_VERSION=0.1.0
API_PREFIX=/api
 
# === 特性开关 ===
V4_ENABLED=true
V4_MEMORY_ENABLED=true
V6_SIMULATION_ENABLED=true
V6_GRAPH_RAG_ENABLED=true
V6_GRAPH_RAG_TOP_K=5
V7_ENABLED=true
V7_OPENING_GATE_ENABLED=true
V7_ANTIPATTERN_GUARD_ENABLED=true
V7_DEADLOCK_ROUTER_ENABLED=true
V8_WORKBENCH_ENABLED=true
 
# === 可观测性 ===
V4_OBSERVABILITY_ENABLED=true
V4_OBSERVABILITY_WINDOW_LIMIT=200
V4_RUNTIME_LATENCY_P95_THRESHOLD_MS=250.0
V4_RUNTIME_ERROR_RATE_THRESHOLD=0.05
V4_RUNTIME_FALLBACK_RATE_THRESHOLD=0.20
 
# === 远端告警 ===
V4_REMOTE_ALERT_ENABLED=false
V4_REMOTE_ALERT_ENDPOINT=https://hooks.example.com/alert
V4_ALERT_COOLDOWN_SECONDS=300
 
# === V7 决策规则 ===
AA_V7_DECISION_RULES_JSON=/path/to/custom_rules.json
```
 
### 14.2 V7 决策规则 (decision_rules.json)
 
```json
{
    "early_chapter_limit": 3,
    "opening_t8_gate": 0.60,
    "tail_hook_zero_threshold": 0.01,
    "antagonist_drop_threshold": -0.20,
    "a6_sigma_lower": -2.0,
    "w6_floor": 0.40,
    "elastic_breakout_margin": 0.02
}
```
 
### 14.3 训练样本 (samples.json)
 
```json
[
    {
        "chapter_index": 1,
        "stage": "opening",
        "mainline_progress": 0.12,
        "sideplot_progress": 0.02,
        "conflict_intensity": 0.58,
        "emotional_temperature": 0.42,
        "pacing_speed": 0.63,
        "foreshadowing_load": 0.18,
        "payoff_pressure": 0.14,
        "target_action": "push_conflict",
        "target_score": 0.92,
        "feedback": 0.88,
        "tags": ["opening", "fast_pace", "conflict"]
    }
]
```
 
---
 
## 15. 文件分类清单
 
### 入口文件 (Entry Points)
 
| 文件 | 类型 | 说明 |
|------|------|------|
| `backend/app/main.py` | **生产入口** | FastAPI 应用工厂 |
| `backend_app.py` | **独立入口** | 独立 FastAPI 应用 |
| `recommend.py` | **CLI 入口** | 离线推荐脚本 |
| `train.py` | **CLI 入口** | 离线训练脚本 |
| `scripts/run_v4_production_cycle.py` | **门禁入口** | V4 生产周期验收 |
| `scripts/run_layered_tests.py` | **测试入口** | 分层测试运行器 |
 
### 公共接口 (Public API)
 
| 文件 | 导出 |
|------|------|
| `alpha_autopilot/__init__.py` | 核心引擎全部公共接口 |
| `backend/app/api/routes/*.py` | REST API 端点 |
| `backend/app/services/narrative_v4/__init__.py` | V4 桥接公共接口 |
| `backend/app/core/config.py` | 配置 Settings 单例 |
 
### 核心模块 (Core Modules)
 
| 文件 | 关键类/函数 |
|------|-------------|
| `alpha_autopilot/planner.py` | `ChapterPlanner` |
| `alpha_autopilot/feature_matrix.py` | `FeatureMatrix` |
| `alpha_autopilot/narrative.py` | `StoryState`, `NarrativeCandidate`, `RecommendationResult` |
| `alpha_autopilot/trainer.py` | `Trainer` |
| `alpha_autopilot/repositories.py` | `HistoryRepository`, `FallbackHistoryRepository` |
| `alpha_autopilot/versioning.py` | `VersionManager`, `MatrixSnapshot` |
| `alpha_autopilot/recommend.py` | `recommend_chapter()`, `preview_recommendations()` |
 
### 控制器 (Controllers)
 
| 文件 | 关键类 |
|------|--------|
| `backend/app/services/narrative_v7/decision_controller.py` | `DecisionFeedbackController` |
| `backend/app/services/narrative_v7/nqm_sampler.py` | `NQMSampler` |
| `backend/app/services/narrative_v7/threshold_band.py` | `ThresholdBandEngine` |
| `backend/app/services/narrative_v7/opening_gate.py` | `OpeningGate` |
| `backend/app/services/narrative_v7/deadlock_router.py` | `DeadlockRouter` |
| `backend/app/services/narrative_v7/antipattern_registry.py` | `AntiPatternRegistry` |
| `backend/app/services/narrative_v8/controller.py` | `build_villain_feedback()` |
| `backend/app/services/narrative_v8/selection.py` | `select_knives()` |
 
### 实验性代码 (Experimental)
 
| 文件/目录 | 说明 |
|-----------|------|
| `demo.py` | 早期演示脚本（使用已废弃的 `TrainingExample` 接口） |
| `claude-review/` | Claude Review 实验代码 |
| `codex-review/` | Codex Review 实验代码 |
| `test-cases/` | 测试用例草稿 |
| `claude_review_package/` | Claude 代码审查包 |
 
---
 
## 16. 模块依赖关系图
 
```
                    ┌─────────────────┐
                    │  backend/app/   │
                    │    main.py      │
                    └────────┬────────┘
                             │ include_router
                    ┌────────┴────────┐
                    │  api/routes/*   │
                    └────────┬────────┘
                             │ 调用
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼───────┐ ┌─────▼──────┐  ┌──────▼──────┐
    │ services/     │ │ services/  │  │ services/   │
    │ narrative/    │ │ narrative_ │  │ narrative_  │
    │ (V1 服务)     │ │ v4~v6/    │  │ v7~v8/      │
    └───────┬───────┘ └─────┬──────┘  └──────┬──────┘
            │               │                │
            └───────────────┼────────────────┘
                            │ 依赖
                    ┌───────▼───────┐
                    │ alpha_autopilot│
                    │   (核心引擎)   │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
     ┌────────▼──┐  ┌──────▼────┐  ┌─────▼──────┐
     │ planner   │  │ feature_  │  │ narrative  │
     │           │  │ matrix    │  │ (models)   │
     └────────┬──┘  └──────┬────┘  └────────────┘
              │            │
              └──────┬─────┘
                     │ 依赖
            ┌────────▼────────┐
            │   trainer       │
            └────────┬────────┘
                     │ 使用
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼─────┐  ┌──────▼─────┐  ┌─────▼──────┐
│repositories│ │ versioning │  │ storage    │
│(File/DB/  │  │(Snapshot/  │  │(Artifact   │
│ Fallback) │  │ Manager)   │  │ Store)     │
└───────────┘  └────────────┘  └────────────┘
```
 
### V7 内部依赖
 
```
DecisionFeedbackController
    ├── DecisionRuleSet          (规则加载)
    └── ThresholdBandEngine      (阈值分类)
 
NQMSampler
    └── BenchmarkParameterSet    (基准参数)
 
StoryStateMarketAdapter
    ├── NarrativeMarketState     (市场状态)
    └── BenchmarkParameterSet    (基准参数)
```
 
### V8 内部依赖
 
```
build_villain_feedback()
    ├── select_knives()
    │       ├── build_candidate_knife_ids()     (constraints.py)
    │       ├── evaluate_knife_rejection()      (constraints.py)
    │       ├── evaluate_compatibility_conflict() (constraints.py)
    │       ├── build_default_knife_library()   (knife_library.py)
    │       └── build_fallback_decision()       (fallbacks.py)
    │
    ├── render_flavor()                          (flavor.py)
    ├── build_future_hooks()                     (flavor.py)
    ├── build_explanation()                       (flavor.py)
    ├── build_risk_if_exposed()                  (flavor.py)
    │
    ├── build_state_shift()                      (ledger.py)
    ├── apply_state_shift()                      (ledger.py)
    │
    └── derive_transition_outcome()              (transitions.py)
```
 
---
 
## 17. V7 决策规则参考
 
### 决策优先级
 
1. **R-OVERRIDE**: 作者主动确认 → OBSERVE
2. **R-04**: 开篇门禁 (T8 < gate) → STOP_LOSS (P0)
3. **R-08**: 反模式临界 → STOP_LOSS (P0)
4. **R-05**: 死锁检测 → RETRACE_REPAIR (P1)
5. **R-06**: 尾钩缺失 (T4 ≤ 0.01) → ADD (P1)
6. **R-07**: 反派压力塌陷 (t9_delta < -0.2) → RETRACE_REPAIR (P1)
7. **R-09**: IP 风味走廊偏移 (a6_sigma < -2.0) → REDUCE (P1)
8. **R-10**: 死亡章回报不足 (W6 < 0.4) → RETRACE_REPAIR (P1)
9. **R-01**: NQM 硬干预 (composite < L) → STOP_LOSS (P0)
10. **R-02/R-02B**: NQM 弹性区 → RETRACE_REPAIR/BREAKOUT_FOLLOW (P2)
11. **R-03**: NQM 自由区 (composite > H) → OBSERVE (P2)
 
### NQM 关键阈值
 
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `early_chapter_limit` | 3 | 开篇门禁生效章数 |
| `opening_t8_gate` | 0.60 | T8 开篇钩子门禁 |
| `tail_hook_zero_threshold` | 0.01 | 尾钩密度下限 |
| `antagonist_drop_threshold` | -0.20 | 反派压力跌幅阈值 |
| `a6_sigma_lower` | -2.0 | IP 风味走廊下限 |
| `w6_floor` | 0.40 | 死亡回报下限 |
| `elastic_breakout_margin` | 0.02 | 弹性→突破边距 |
| L (low_threshold) | 0.52 | 硬干预阈值 |
| H (high_threshold) | 0.78 | 自由生成阈值 |
 
---
 
## 18. V8 反派控制面参考
 
### 策略刀兼容性矩阵
 
```
                  self_image  high_ground  fake_vuln  delayed  rel_withdraw  old_wound  memory_ref  courteous  gentle  baited
self_image         -           compat       -          -        INCOMPAT      -           -          compat      -       compat
high_ground        compat      -            -          -        -             -           -          -           -       -
fake_vuln          -           -            -          compat   -             -           -          INCOMPAT    compat  -
delayed_asking     -           -            compat     -        -             -           -          -           compat  compat
rel_withdraw       INCOMPAT    -            -          -        -             compat      -          -           INCOMPAT -
old_wound          -           -            -          -        compat        -           compat     -           -       -
memory_ref         -           -            -          -        -             compat      -          -           -       compat
courteous          compat      -            INCOMPAT   -        -             -           -          -           -       -
gentle             -           -            compat     compat   INCOMPAT      -           -          -           -       -
baited             compat      -            -          compat   -             -           compat     -           -       -
```
 
### 状态账本维度
 
| 领域 | 状态字段 | 范围 |
|------|----------|------|
| **relationship** | trust, debt, dependency, leverage | [-3, 3] |
| **narrative** | suspicion, reputation, witness_alignment, explanation_control | [-3, 3] |
| **psychological** | shame_load, wound_activation, protector_trigger, identity_destabilization | [-3, 3] |
| **hook** | planted_hooks, armed_payoffs, recovered_hooks | list |
 
### 控制状态转移图
 
```
harmless → suspicious → distrusted → collapsed
    │           │              │
    └── repair_attempt ────────┘
            │
    partially_restored
```
 
---
 
## 19. alpha-SRE 集成
 
Alpha-SRE (`/home/ubuntu/repos/alpha-SRE`) 是配套的 SRE 工具集，提供：
 
- **快照与回放**: 叙事状态快照管理和回放能力
- **门禁系统**: 生产发布门禁规则
- **事故导出**: 叙事事故后验模板
- **一致性验证**: 叙事指标目录和因果验证规范
- **治理文档**: 执行治理、架构演进策略、需求准入流程
 
### SRE 关键文件
 
| 文件 | 职责 |
|------|------|
| `integration_plan_alpha_autopilot.md` | 与 alpha-autopilot 的集成方案 |
| `narrative_state_schema.md` | 叙事状态 Schema 规范 |
| `consistency_metric_catalog.md` | 一致性指标目录 |
| `causal_validation_spec.md` | 因果验证规范 |
| `replay_spec.md` | 回放规范 |
| `incident_postmortem_template.md` | 事故复盘模板 |
| `execution_governance.md` | 执行治理规范 |
| `schema_evolution_policy.md` | Schema 演进策略 |
 
---
 
## 附录: API 端点速查
 
| 方法 | 路径 | 服务 | 说明 |
|------|------|------|------|
| GET | `/api/dashboard` | `build_dashboard()` | 仪表盘 |
| POST | `/api/recommendation/preview` | `build_preview()` | V1 推荐预览 |
| POST | `/api/v2/recommendation/preview` | V2 预览 | V2 推荐预览 |
| GET | `/api/v2/workbench/contexts` | workbench | Workbench 上下文 |
| POST | `/api/v2/workbench/contexts/refresh` | workbench | Workbench 刷新 |
| POST | `/api/training` | `NarrativeTrainingService` | 训练 |
| POST | `/api/feedback` | `NarrativeFeedbackService` | 反馈记录 |
| GET | `/api/history` | history_service | 历史查询 |
| POST | `/api/history/export` | history_export | 历史导出 |
| * | `/api/v4/*` | narrative_v4 | V4 桥接+可观测 |
| * | `/api/v6/*` | narrative_v6 | V6 并行模拟 |
| * | `/api/v7/*` | narrative_v7 | V7 NQM 决策 |