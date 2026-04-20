# novel-fusion-autopilot 接口草案

## 1. 目标

本草案定义 `alpha-autopilot` 小说章节推荐原型迁移到 `novel-fusion-autopilot` 时的接口边界、数据契约和模块职责，用于后续工程接入与评审对齐。

核心原则：

- 保留可解释特征矩阵
- 保留状态推演中枢
- 保留训练日志与版本快照
- 不强制依赖静态数据库
- 允许与 `novel-fusion-autopilot` 的生成、检索、审稿模块并行工作

## 2. 总体接口分层

### 2.1 状态层
负责接收小说上下文，构建结构化故事状态。

### 2.2 推演层
根据状态和特征矩阵生成候选章节策略。

### 2.3 评分层
对候选方案进行量化打分与排序。

### 2.4 反馈层
接收实际写作结果、人工修正或读者反馈，更新权重。

### 2.5 版本层
管理矩阵快照、训练记录、样本版本。

## 3. 数据契约

### 3.1 StoryState

```python
@dataclass
class StoryState:
    chapter_index: int
    stage: str
    mainline_progress: float
    sideplot_progress: float
    conflict_intensity: float
    emotional_temperature: float
    pacing_speed: float
    foreshadowing_load: float
    payoff_pressure: float
    characters: Dict[str, CharacterState]
    tags: List[str]
```

#### 含义
- `chapter_index`：当前章节序号
- `stage`：叙事阶段，例如 `opening` / `middle` / `mid_late` / `late`
- `mainline_progress`：主线推进程度
- `sideplot_progress`：支线推进程度
- `conflict_intensity`：冲突强度
- `emotional_temperature`：情绪温度
- `pacing_speed`：推进速度
- `foreshadowing_load`：伏笔负载
- `payoff_pressure`：回收压力
- `characters`：角色状态映射
- `tags`：题材、风格、平台标签

### 3.2 CharacterState

```python
@dataclass
class CharacterState:
    name: str
    presence: float
    consistency_risk: float
    relationship_tension: float
    arc_progress: float
```

#### 含义
- `presence`：角色存在感
- `consistency_risk`：人设偏移风险
- `relationship_tension`：关系张力
- `arc_progress`：角色弧光推进进度

### 3.3 NarrativeCandidate

```python
@dataclass(frozen=True)
class NarrativeCandidate:
    action: str
    delta: Dict[str, float]
    explanation: str
```

#### 含义
- `action`：推荐动作名
- `delta`：该动作对状态变量的增量影响
- `explanation`：推荐理由

### 3.4 RecommendationResult

```python
@dataclass
class RecommendationResult:
    candidate: NarrativeCandidate
    score: float
    details: Dict[str, float]
```

#### 含义
- `candidate`：候选方案
- `score`：综合得分
- `details`：特征分布明细

## 4. 核心接口草案

### 4.1 状态构建接口

```python
class StoryStateBuilder:
    def build(self, payload: dict) -> StoryState:
        ...
```

#### 输入
- 章节文本摘要
- 角色状态
- 前文上下文
- 标签信息

#### 输出
- 结构化 `StoryState`

### 4.2 特征评分接口

```python
class FeatureMatrixService:
    def score(self, state: StoryState, features: dict) -> float:
        ...

    def update_from_feedback(self, features: dict, target: float, prediction: float) -> None:
        ...
```

#### 作用
- 为候选方案打分
- 根据反馈更新权重

### 4.3 候选推演接口

```python
class ChapterPlannerService:
    def recommend(self, state: StoryState) -> list[RecommendationResult]:
        ...
```

#### 作用
- 生成候选推进策略
- 排序输出 Top-K 方案

### 4.4 训练接口

```python
class TrainingService:
    def fit(self, samples: Iterable[TrainingSample]) -> FeatureMatrix:
        ...
```

#### 作用
- 从拆解样本训练初版矩阵
- 形成可追踪版本

### 4.5 版本管理接口

```python
class VersionService:
    def create_version(self, weights: dict, bias: float, sample_count: int, notes: str = "") -> MatrixSnapshot:
        ...
```

#### 作用
- 保存快照
- 便于回滚与审查

### 4.6 反馈接口

```python
class FeedbackService:
    def record(self, stage: str, action: str, predicted: float, target: float, feedback: float) -> None:
        ...
```

#### 作用
- 记录训练或推荐后的效果
- 作为下一轮更新依据

## 5. 与 novel-fusion-autopilot 的对接方式

### 5.1 输入对接
`novel-fusion-autopilot` 负责提供：

- 章节摘要
- 人物设定
- 世界观上下文
- 风格标签
- 平台约束
- 历史章节摘要

然后由 `StoryStateBuilder` 转为 `StoryState`。

### 5.2 输出对接
推荐模块输出：

- 推荐动作名
- 推荐评分
- 结构化解释
- 状态变化增量

`novel-fusion-autopilot` 再把这些结果映射到：

- 章节规划
- 大纲生成
- 片段生成
- 编辑审稿

### 5.3 反馈对接
`novel-fusion-autopilot` 可回传：

- 人工采纳情况
- 文本质量评分
- 章节连贯性评分
- 读者反馈信号

用于更新特征矩阵。

## 6. 迁移边界

### 保留
- 特征矩阵思想
- 状态推演思想
- 训练日志
- 版本快照
- 反馈闭环

### 重新实现
- 真实 API 网关
- 数据校验层
- 异步任务调度
- 持久化存储接口
- UI 与交互层

### 不建议直接迁移
- 任何和象棋领域强耦合的命名
- 只适用于棋盘的搜索逻辑
- 与小说无关的评估维度

## 7. 工程建议

- 先用当前原型作为 `novel-fusion-autopilot` 的参考子模块
- 接口先统一，内部实现后续替换
- 所有状态与评分结构均保留版本号
- 先跑通“输入 -> 推演 -> 推荐 -> 反馈 -> 更新”最小闭环

## 8. 结论

该接口草案的目标是让小说章节推荐系统先以独立原型存在，再逐步接入 `novel-fusion-autopilot` 的正式工程链路，避免一开始就过度耦合。
