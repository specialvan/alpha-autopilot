# V3 Reader Retention Interface Design

## 1. Goal

Define the code-level interfaces for the reader-retention target function and generation control layer so the implementation can proceed without ambiguity.

## 2. New modules

### 2.1 `alpha_autopilot_v3.retention`

#### `models.py`

```python
@dataclass(frozen=True)
class RetentionTargetFunction:
    name: str
    primary_objective: str
    priority_order: list[str]
    guardrails: list[str] = field(default_factory=list)
    description: str = ""

@dataclass(frozen=True)
class RetentionMetrics:
    chapter_attraction_score: float
    continue_reading_intent: float
    emotional_drive: float
    pacing_drive: float
    suspense_drive: float
    conflict_drive: float
    hook_strength: float
    template_risk: float
    evidence: dict[str, Any] = field(default_factory=dict)
```

#### `target_function.py`

- `build_retention_target_function() -> RetentionTargetFunction`

#### `metrics.py`

- `build_retention_metrics(record: ChapterDecompositionRecord) -> RetentionMetrics`

### 2.2 `alpha_autopilot_v3.generation_control`

#### `models.py`

```python
@dataclass(frozen=True)
class GenerationControlPlan:
    target_function: RetentionTargetFunction
    retention_metrics: RetentionMetrics
    focus_mode: str
    emotional_curve: str
    pacing_curve: str
    suspense_curve: str
    conflict_curve: str
    hook_strategy: str
    anti_pattern_warnings: list[str] = field(default_factory=list)
    decision_tags: dict[str, Any] = field(default_factory=dict)
    suggestions: dict[str, Any] = field(default_factory=dict)
```

#### `mapping.py`

- `build_decision_tags(record, metrics) -> dict[str, Any]`
- `build_generation_control_suggestions(record, metrics) -> dict[str, Any]`

#### `policy.py`

- `build_generation_control_plan(record) -> GenerationControlPlan`

## 3. Existing module updates

### 3.1 `alpha_autopilot_v3.decomposition.models`

Add retention-related fields to `ChapterDecompositionRecord`:

- `retention_signal`
- `attraction_score`
- `hook_strength`
- `pace_pressure`
- `emotion_curve`
- `decision_tags`
- `control_suggestions`

### 3.2 `alpha_autopilot_v3.decomposition.pipeline`

- keep existing decomposition logic
- call retention metrics builder
- call generation control builder
- enrich `workbench_context` with retention and control data

### 3.3 `alpha_autopilot_v3.__init__`

Export new retention and control symbols for easier downstream usage.

## 4. Data flow

1. Decompose chapter text
2. Build retention metrics
3. Build generation control plan
4. Write retention values into record
5. Expose final context to workbench / downstream consumers

## 5. Design rules

- Do not remove structure-first decomposition
- Do not turn metrics into a single opaque score only
- Do not let retention logic overwrite baseline admission logic
- Do not make the control layer mandatory for existing baseline consumers

## 6. Testing targets

- retention target function construction
- retention metric scoring
- generation control planning
- pipeline enrichment of chapter record
- export visibility from `alpha_autopilot_v3.__init__`

## 7. Implementation note

These interfaces are intentionally small and explicit so Codex can review them cleanly and later extend them with topic/genre-specific weighting, feedback loops, and workbench visualization.
