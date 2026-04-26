# novel-fusion-autopilot 接口草案

## 1. 目标

本草案定义 `alpha-autopilot` 向 `novel-fusion-autopilot` 迁移时的接口边界、数据契约和模块职责。它不是“旁路实验说明”，而是主链路接入前的对齐文档。

统一术语如下：

- `rule layer`：规则约束、阶段门槛、质量边界。
- `search layer`：候选生成、排序、局部探索。
- `evaluation loop`：采纳、反馈、校准、再训练。
- `quality layer`：分阶段接入主链路的质量能力。

## 2. 总体分层

### 2.1 状态层

状态层接收章节上下文，构建结构化故事状态。

### 2.2 规则层

规则层把故事状态映射为可执行约束，决定哪些候选允许进入搜索。

### 2.3 搜索层

搜索层在规则约束下生成候选，并输出 Top-K 排序结果。

### 2.4 评估层

评估层记录推荐结果、实际采纳、人工反馈与版本差异，形成闭环。

### 2.5 质量层

质量层先作为旁路诊断模块存在，再逐步进入主链路。默认阶段口径如下：

- `Q1`：只诊断，不影响推荐。
- `Q2`：影响排序参考，不直接阻断输出。
- `Q3`：进入主决策链路，但支持降级回退。

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

含义：

- `stage`：`opening` / `middle` / `late` 等阶段。
- `mainline_progress`：主线推进程度。
- `sideplot_progress`：支线推进程度。
- `conflict_intensity`：冲突强度。
- `emotional_temperature`：情绪温度。
- `pacing_speed`：节奏速度。
- `foreshadowing_load`：伏笔负载。
- `payoff_pressure`：回收压力。

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

### 3.3 SearchCandidate

```python
@dataclass(frozen=True)
class SearchCandidate:
    action: str
    delta: Dict[str, float]
    explanation: str
```

### 3.4 EvaluationReport

```python
@dataclass
class EvaluationReport:
    candidate: SearchCandidate
    score: float
    details: Dict[str, float]
    accepted: bool
```

## 4. 接口草案

### 4.1 状态构建

```python
class StoryStateBuilder:
    def build(self, payload: dict) -> StoryState:
        ...
```

### 4.2 规则评估

```python
class RuleEngine:
    def validate(self, state: StoryState) -> list[str]:
        ...
```

返回值说明：

- 返回空列表表示没有硬性规则冲突。
- 返回告警列表表示候选需要降权或限制。

### 4.3 候选搜索

```python
class SearchService:
    def recommend(self, state: StoryState) -> list[SearchCandidate]:
        ...
```

### 4.4 闭环更新

```python
class EvaluationService:
    def record(
        self,
        stage: str,
        action: str,
        predicted: float,
        target: float,
        feedback: float,
    ) -> None:
        ...
```

### 4.5 质量层接入

```python
class QualityLayerService:
    def diagnose(self, state: StoryState, candidate: SearchCandidate) -> dict:
        ...
```

## 5. 与 `novel-fusion-autopilot` 的对接方式

### 5.1 输入对接

`novel-fusion-autopilot` 提供：

- 章节摘要
- 人物设定
- 世界观上下文
- 风格标签
- 平台约束
- 历史章节摘要

然后通过 `StoryStateBuilder` 转为 `StoryState`。

### 5.2 输出对接

推荐模块输出：

- 推荐动作名
- 推荐评分
- 结构化解释
- 状态变化增量

下游再把结果映射为：

- 章节规划
- 大纲生成
- 段落生成
- 编辑审稿

### 5.3 反馈对接

反馈对接包含：

- 人工采纳情况
- 文本质量评分
- 章节连贯性评分
- 读者反馈信号

这些信号进入 `evaluation loop`，再用于权重与阈值更新。

## 6. 数据库替代边界

保留的内容：

- 特征矩阵思想
- 状态推演思想
- 训练日志
- 版本快照
- 反馈闭环

重新实现的内容：

- 真正的 API 网关
- 持久化层
- 异步任务调度
- UI / workbench 集成

不建议直接迁移的内容：

- 强耦合于象棋 / 桌游领域的命名
- 只适合 demo 的搜索逻辑
- 无法解释或无法回放的临时规则

## 7. 工程建议

- 先统一术语，再替换实现。
- 先跑通 `input -> rule -> search -> evaluation -> update` 最小闭环。
- 所有状态与评分结构必须保留版本号。
- 质量层先旁路，后接主链路。
- 数据库替代先做验证口径，不先做一次性切换。

## 8. 结论

这个接口草案的核心目标是：让章节推荐系统先形成稳定的主链路，再逐步把 quality layer 和数据库替代能力纳入同一套工程约束，而不是把它们描述成独立的侧实验。
