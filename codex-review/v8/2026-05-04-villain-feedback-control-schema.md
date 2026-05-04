# 反派反馈控制工程 Schema 草案（v8.1）

> 用途：为 `alpha-autopilot` 当前仓库提供一个可独立评审、可独立测试的“反派反馈控制核心”数据模型。
>
> 宿主校正：此前文档误把落点写成了其他线程的 `packages/core` TypeScript 模块。该假设已废弃。
>
> 当前建议落点：`backend/app/services/narrative_v8/`
>
> 范围边界：第一阶段只做独立 Python increment 控制核心，不直接接入 `writer`、UI、CLI、持久化存储或默认主链路。

## 1. 核心目标

`v8.1` 要解决的不是“再造一个会算计的坏女人模板”，而是把细腻反派争斗里的小刀子抽成可复用机制，再让这些机制在不同反派、不同场域、不同长线状态里自动变味。

第一阶段必须满足 5 个目标：

1. 同一把刀可跨角色复用，但不会把所有反派写成同一个人。
2. 反派有稳定刀谱与禁手，不是全能模板。
3. 场景里的观众、权力结构、曝光条件能改变出刀方式。
4. 每次出刀都能写入长线状态，而不是一次性动作。
5. 系统必须能结构化解释：为什么现在、为什么这把刀、为什么这个反派会这么用。

## 2. 宿主与边界

### 2.1 宿主选择

`v8.1` 建议作为当前仓库的独立 increment 模块落在：

1. `backend/app/services/narrative_v8/schemas.py`
2. `backend/app/services/narrative_v8/knife_library.py`
3. `backend/app/services/narrative_v8/constraints.py`
4. `backend/app/services/narrative_v8/selection.py`
5. `backend/app/services/narrative_v8/flavor.py`
6. `backend/app/services/narrative_v8/ledger.py`
7. `backend/app/services/narrative_v8/transitions.py`
8. `backend/app/services/narrative_v8/controller.py`

理由：

1. 这里符合当前仓库的 Python/FastAPI 服务分层。
2. 可以像 `narrative_v4/v6/v7` 一样保持增量隔离。
3. 不会把尚未稳定的控制核心过早写进 `alpha_autopilot` 基线域模型。

### 2.2 第一阶段不做什么

`v8.1` 当前不做下面这些事：

1. 不直接写正文。
2. 不直接控制 LLM prompt 产出。
3. 不加 API 路由。
4. 不加 CLI 入口。
5. 不做持久化 schema 迁移。
6. 不改现有 `narrative_v2 / v4 / v6 / v7` 默认行为。

## 3. 三层抽象模型

## 3.1 刀法原语层

这一层只定义“机制”，不定义人格口音。

建议对象：

```python
class KnifePrimitive(BaseModel):
    id: str
    name: str
    intent: str
    mechanism: str
    emotional_disguise: tuple[str, ...] = ()
    target_vulnerabilities: tuple[str, ...] = ()
    best_arenas: tuple["ArenaType", ...] = ()
    risks: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    compatible_with: tuple[str, ...] = ()
    incompatible_with: tuple[str, ...] = ()
    constraints: "KnifeConstraintSet"
```

第一版保留原先 10 个基础原语：

1. `self_image_feeding`
2. `high_ground_pity`
3. `fake_vulnerability`
4. `delayed_asking`
5. `relationship_withdrawal`
6. `old_wound_trigger`
7. `memory_reframing`
8. `courteous_humiliation`
9. `gentle_absorption`
10. `baited_concession`

### 3.1.1 显式约束模型

Claude 的关键反馈之一是：不能只靠 `preferred_knives`、`forbidden_moves` 这种字符串数组来表达约束。

因此 `KnifePrimitive` 必须带一层独立约束对象：

```python
class KnifeConstraintSet(BaseModel):
    scene_restrictions: tuple[str, ...] = ()
    target_restrictions: tuple[str, ...] = ()
    observer_requirements: tuple[str, ...] = ()
    anti_conditions: tuple[str, ...] = ()
    backfire_conditions: tuple[str, ...] = ()
    ineffective_conditions: tuple[str, ...] = ()
    flavor_conflicts: tuple[str, ...] = ()
```

这层约束的用途：

1. 显式表达“哪些场景不能用”。
2. 显式表达“哪些目标不吃这把刀”。
3. 显式表达“哪些观众结构缺失后这把刀失效”。
4. 显式表达“什么条件下会反噬”。
5. 显式表达“这把刀和哪些风味/刀法组合会打架”。

### 3.1.2 兼容图

刀法兼容性不应隐藏在 selector 的私有逻辑里。

建议单独建：

```python
class KnifeCompatibilityEdge(BaseModel):
    left: str
    right: str
    relation: Literal["compatible", "incompatible", "conditional"]
    reason: str
```

## 3.2 反派认知层

这一层决定“为什么同一把刀到了不同人手里会是不同邪道风味”。

```python
class VillainProfile(BaseModel):
    id: str
    archetype: str
    core_wound: str
    core_belief: str
    psychology_literacy: "PsychologyLiteracyLevel"
    preferred_knives: tuple[str, ...]
    secondary_knives: tuple[str, ...] = ()
    forbidden_moves: tuple[str, ...]
    public_mask: tuple[str, ...]
    private_drive: tuple[str, ...]
    time_horizon: "TimeHorizon"
    blind_spot: str
    escalation_rule: str
    shame_relation: "ShameRelation"
    witness_need: "WitnessNeed"
    flavor_profile: "FlavorAxisProfile"
```

### 3.2.1 风味必须收口

稳定风味只能收口在 `flavor_profile`，不能再像旧版那样散在多个层里互相抢定义权。

建议：

```python
class FlavorAxisProfile(BaseModel):
    temperature: Literal["cold", "soft", "hot", "faded", "sacred", "decadent"]
    rituality: Literal["low", "mid", "high"]
    sensuality: Literal["low", "mid", "high"]
    theatricality: Literal["low", "mid", "high"]
    cruelty_visibility: Literal["hidden", "mixed", "open"]
    witness_dependence: Literal["private", "mixed", "public"]
    control_preference: Literal["private_invasion", "public_rewrite", "resource_cut", "emotional_absorption"]
```

其中：

1. `flavor_profile` 是稳定偏好源。
2. `public_mask` 是她给外界看的壳。
3. `private_drive` 是她真正想要什么。
4. 运行时的 `FlavorRender` 只能是输出实例，不能反过来定义角色本体。

### 3.2.2 反派差异化硬约束

`VillainProfile` 必须满足：

1. `preferred_knives` 最少 1 个，最多 3 个。
2. `secondary_knives` 最多 2 个。
3. `forbidden_moves` 最少 1 个。
4. `preferred_knives` 与 `forbidden_moves` 不可重叠。
5. `blind_spot`、`core_wound`、`core_belief` 都不能为空。
6. `forbidden_moves` 必须在 selector 里真实生效。

心理学理解层级保留 4 级：

```python
PsychologyLiteracyLevel = Literal[
    "instinctive",
    "experiential",
    "semi_systematic",
    "systematic",
]
```

## 3.3 目标与场景映射层

### 3.3.1 TargetProfile

旧版目标建模太粗，`v8.1` 必须补到能支撑精确选刀。

```python
class TargetProfile(BaseModel):
    id: str
    self_image: str
    core_need: str
    core_fear: str
    weak_points: tuple[str, ...]
    defense_style: str
    resistance_style: str
    witness_sensitivity: Literal["low", "mid", "high"]
    identity_anchor: str
    social_priorities: tuple[str, ...] = ()
```

关键补强项：

1. `defense_style`
2. `witness_sensitivity`
3. `identity_anchor`

这样系统才能区分：某个目标是怕公开失态、怕失去身份、怕愧疚、还是怕对不起自己自认的形象。

### 3.3.2 SceneContext

旧版 `audience` 只是一个数组，不够表达“谁在看、谁有裁决权、谁会转述、谁会缓冲、谁以后能救场”。

`v8.1` 必须补出观察者拓扑和权力拓扑：

```python
class SceneObserver(BaseModel):
    id: str
    role: Literal["witness", "judge", "transmitter", "buffer", "recovery_node"]
    alignment: Literal["villain", "target", "mixed", "volatile", "unknown"]
    importance: int
    visibility_impact: int


class PowerEdge(BaseModel):
    source: str
    target: str
    relation: str
    asymmetry: int


class SceneContext(BaseModel):
    arena: "ArenaType"
    stake: "StakeType"
    observers: tuple[SceneObserver, ...]
    power_topology: tuple[PowerEdge, ...]
    relationship_distance: "RelationshipDistance"
    visibility: "SceneVisibility"
    time_pressure: "TimePressure"
    current_phase: "ControlPhase"
    current_control_state: "ControlSurfaceState"
    existing_state: "LedgerSnapshot"
```

场域仍然不是文学标签，而是权力结构标签：

```python
ArenaType = Literal[
    "shitu",
    "menpai",
    "shijia",
    "chaotang",
    "jianghu",
    "qingzhai",
    "ziyuan",
    "mingsheng",
]
```

## 4. 分层状态账本

Claude 最核心的 P0 之一就是：`StateLedger` 不能再是扁平 delta 表。

`v8.1` 必须把状态账本拆成 4 层：

1. `relationship`
2. `narrative`
3. `psychological`
4. `hook`

### 4.1 LedgerSnapshot

```python
class RelationshipLedgerState(BaseModel):
    trust: int = 0
    debt: int = 0
    dependency: int = 0
    leverage: int = 0


class NarrativeLedgerState(BaseModel):
    suspicion: int = 0
    reputation: int = 0
    witness_alignment: int = 0
    explanation_control: int = 0


class PsychologicalLedgerState(BaseModel):
    shame_load: int = 0
    wound_activation: int = 0
    protector_trigger: int = 0
    identity_destabilization: int = 0


class HookLedgerState(BaseModel):
    planted_hooks: tuple["FutureHook", ...] = ()
    armed_payoffs: tuple["FutureHook", ...] = ()
    recovered_hooks: tuple[str, ...] = ()


class LedgerSnapshot(BaseModel):
    relationship: RelationshipLedgerState
    narrative: NarrativeLedgerState
    psychological: PsychologicalLedgerState
    hook: HookLedgerState
```

### 4.2 StateLedgerShift

```python
class RelationshipLedgerShift(BaseModel):
    trust_delta: int = 0
    debt_delta: int = 0
    dependency_delta: int = 0
    leverage_delta: int = 0


class NarrativeLedgerShift(BaseModel):
    suspicion_delta: int = 0
    reputation_delta: int = 0
    witness_alignment_delta: int = 0
    explanation_control_delta: int = 0


class PsychologicalLedgerShift(BaseModel):
    shame_load_delta: int = 0
    wound_activation_delta: int = 0
    protector_trigger_delta: int = 0
    identity_destabilization_delta: int = 0


class HookLedgerShift(BaseModel):
    planted_hooks: tuple["FutureHook", ...] = ()
    armed_payoffs: tuple["FutureHook", ...] = ()
    recovered_hooks: tuple[str, ...] = ()


class StateLedgerShift(BaseModel):
    relationship: RelationshipLedgerShift
    narrative: NarrativeLedgerShift
    psychological: PsychologicalLedgerShift
    hook: HookLedgerShift
```

### 4.3 分层账本约束

1. 数值离散区间先用 `-3` 到 `+3`。
2. 单场景最多 `2` 个核心 delta 的绝对值超过 `1`。
3. 账本记录的是“局势偏移”，不是事件流水。
4. `hook` 层只能处理未来钩子、回收钩子、延迟 payoff，不和关系层混写。

### 4.4 失手 / 修复 / 升级 / 状态迁移层

Claude 固定过的证据链不只要求“有 ledger”，还要求把 `failure_mode / recovery_mode / upgrade_trigger / upgrade_path / transition_state` 明确成一等结构，而不是散在叙述里。

```python
ControlSurfaceState = Literal[
    "harmless",
    "suspicious",
    "distrusted",
    "repair_attempt",
    "partially_restored",
    "upgraded",
    "more_hidden",
    "stronger",
    "hardened",
    "collapsed",
]

FailureMode = Literal[
    "shell_exposed",
    "pace_lost",
    "position_locked",
    "narrative_lost",
]

RecoveryMode = Literal[
    "re_feel_vulnerability",
    "lower_intensity",
    "retreat_to_safer_role",
    "change_scene",
    "re_establish_decorum",
    "re_establish_narrative_control",
]

UpgradeTrigger = Literal[
    "primitive_stalled",
    "shell_seen_through",
    "higher_order_path_found",
]

UpgradePath = Literal[
    "more_hidden",
    "more_sparse",
    "more_systemic",
    "more_enduring",
    "more_complex",
    "outsourced_interpretation",
]


class TransitionLayer(BaseModel):
    prior_state: ControlSurfaceState
    next_state: ControlSurfaceState
    failure_mode: FailureMode | None = None
    recovery_mode: RecoveryMode | None = None
    upgrade_trigger: UpgradeTrigger | None = None
    upgrade_path: UpgradePath | None = None
    transition_reason: str
```

这一层的工程约束必须写死：

1. `current_control_state` 必须作为 `SceneContext` 输入的一部分，而不是让 controller 自己猜。
2. `failure_mode`、`recovery_mode`、`upgrade_trigger` 不能靠解释层文案代替。
3. `fallback` 只代表本次不稳定落刀，不等于自动进入 `collapsed`。
4. `TransitionLayer` 必须写出 `prior_state -> next_state`，不能只说“风险增大了”。
5. `upgrade_path` 不能脱离 `upgrade_trigger` 单独出现。
6. `collapsed` 状态不能同时伪装成 `recovery_mode` 已成立。

## 5. 结构化输出包

旧版 `VillainFeedbackPacket` 太叙述化。`v8.1` 必须拆成“决策层 + 解释层 + 迁移层 + 状态层 + 钩子层 + 风味层”。

```python
class SelectedKnifeSignal(BaseModel):
    knife_id: str
    fit_score: float
    reasons: tuple[str, ...]


class RejectedKnifeReason(BaseModel):
    knife_id: str
    category: Literal[
        "forbidden_move",
        "scene_restriction",
        "target_restriction",
        "observer_requirement_missing",
        "anti_condition",
        "compatibility_conflict",
        "backfire_condition",
        "ineffective_condition",
        "flavor_conflict",
        "low_fit_score",
    ]
    detail: str


class DecisionLayer(BaseModel):
    selection_mode: Literal["scored_fit", "fallback"]
    primary_knife_id: str | None = None
    secondary_knife_id: str | None = None
    fallback_action: Literal[
        "hold_position",
        "gather_information",
        "defer_to_public_mask",
        "reduce_exposure",
    ] | None = None
    fallback_reason: str | None = None
    selected_signals: tuple[SelectedKnifeSignal, ...]
    rejected_knives: tuple[RejectedKnifeReason, ...]


class ExplanationLayer(BaseModel):
    external_move: str
    inner_drive: str
    target_misread: str
    why_now: str
    why_this_choice: str
    why_this_villain_style: str


class FlavorRender(BaseModel):
    tone: str
    aesthetic: tuple[str, ...]
    social_surface: tuple[str, ...]
    private_subtext: tuple[str, ...]
    delivery_surface: Literal[
        "private_softness",
        "public_innocence",
        "ritual_distance",
        "courteous_superiority",
        "fatigued_reserve",
    ]
    pressure_channel: Literal[
        "self_image",
        "witness_pressure",
        "guilt_pull",
        "status_gap",
        "dependency_pull",
        "memory_reframe",
    ]
    witness_posture: Literal[
        "avoid_witness",
        "use_witness",
        "perform_for_judge",
        "seed_for_transmitter",
        "hide_from_recovery_node",
    ]
    cost_profile: Literal[
        "low_exposure",
        "delayed_exposure",
        "high_backfire",
        "reputation_bet",
    ]
    hook_style: Literal[
        "debt_seed",
        "shame_seed",
        "misread_seed",
        "dependency_seed",
        "public_record_seed",
    ]
    structural_targets: tuple[
        Literal["external_move", "risk_if_exposed", "future_hooks", "state_shift"],
        ...,
    ]
    state_shift_focus: Literal["relationship", "narrative", "psychological", "hook"]


class VillainFeedbackPacket(BaseModel):
    villain_id: str
    target_id: str
    scene_arena: ArenaType
    decision: DecisionLayer
    explanation: ExplanationLayer
    transition: TransitionLayer
    state_shift: StateLedgerShift
    future_hooks: tuple["FutureHook", ...]
    risk_if_exposed: tuple[str, ...]
    flavor_render: FlavorRender
```

### 5.1 Selector 不是“纯打分器”

`v8.1` 的 selector 必须是“两段式控制器”，不是“偏好排序器”。

控制顺序必须固定为：

1. 先执行硬过滤。
2. 再只对幸存候选计算 `fit_score`。

其中下面 4 类必须属于硬过滤，而不是降分项：

1. `forbidden_moves`
2. `anti_conditions`
3. `observer_requirements`
4. 不可兼容的 knife edge

因此必须满足：

1. 任一硬过滤失败的刀，不得进入 `selected_signals` 的打分池。
2. 每一把被硬过滤的刀，都必须进入 `rejected_knives`。
3. `RejectedKnifeReason.category` 必须能区分“硬过滤失败”与“只是低分淘汰”。
4. 如果没有任何刀通过硬过滤，`selection_mode` 必须进入 `fallback`，并写明 `fallback_reason`。
5. `selection_mode="fallback"` 时，`primary_knife_id`、`secondary_knife_id` 必须为 `None`，`selected_signals` 必须为空，且必须显式写出 `fallback_action` 与 `fallback_reason`。
6. `selection_mode="scored_fit"` 时，`primary_knife_id` 必须存在，`selected_signals` 不得为空，`fallback_action` 与 `fallback_reason` 应为空。

### 5.2 `FutureHook`

```python
class FutureHook(BaseModel):
    id: str
    source_knife_id: str
    description: str
    payoff_window: Literal["immediate", "near", "mid", "long"]
    recovery_condition: str
```

### 5.3 FlavorRender 不是描述标签

`FlavorRender` 不只是“这段话听起来像谁”，它必须显式声明自己改写了包的哪些结构面。

因此必须满足：

1. `structural_targets` 必须列出被 `FlavorRender` 实际改写的结构面，且至少覆盖 `external_move / risk_if_exposed / future_hooks / state_shift` 中的 2 项。
2. `state_shift_focus` 必须和最终 `state_shift` 的重心一致，不能只停留在风味描述层。
3. 如果某次 flavor 变化只改措辞、不改 `structural_targets` 覆盖到的结构字段，则视为 flavor 失败。

## 6. 运行逻辑

`v8.1` 控制回路建议按下面顺序执行：

```text
读取反派参数
-> 读取目标参数
-> 读取场景上下文
-> 读取当前 LedgerSnapshot
-> 校验 profile / scene / target / observer 约束
-> 读取刀法原语库与兼容图
-> 先执行硬过滤（forbidden / anti-condition / observer requirement / incompatibility）
-> 仅对幸存候选计算主刀 / 副刀 fit score
-> 输出 decision layer 与 rejected reasons
-> 做风味重绘
-> 生成 explanation layer
-> 结合 current_control_state、暴露风险、修复动作、升级触发信号生成 transition layer
-> 生成分层 state_shift
-> 产出 future hooks
-> 应用 shift 得到 next LedgerSnapshot
```

第一阶段建议显式输出：

```python
class BuildVillainFeedbackInput(BaseModel):
    villain: VillainProfile
    target: TargetProfile
    scene: SceneContext
    knife_library: tuple[KnifePrimitive, ...]


class BuildVillainFeedbackOutput(BaseModel):
    packet: VillainFeedbackPacket
    next_snapshot: LedgerSnapshot
```

## 7. 防塌缩规则

### 7.1 角色防塌缩

1. 反派不能“全刀精通”。
2. `forbidden_moves` 必须真实生效。
3. `psychology_literacy` 不同，解释层和选刀证据必须不同。
4. `blind_spot` 必须能制造失败风险。

### 7.2 场景防塌缩

1. 每场最多 `1 主刀 + 1 副刀`。
2. 不允许每次都用同一刀而不受场景/观众/状态影响。
3. 不允许观众拓扑变化却不影响结果。
4. 不允许没有未来钩子或没有代价。

### 7.3 文风防塌缩

1. Schema 不直接存台词模板。
2. 只存结构，不存单一人格腔调。
3. `FlavorRender` 只能做实例化渲染，不能成为稳定人格定义源。
4. `FlavorRender` 必须影响输出结构，而不只是改措辞。
5. `FlavorRender.structural_targets` 至少要显式覆盖下面 4 项中的 2 项以上：
   - `external_move` 的包装方式
   - `risk_if_exposed` 的暴露形态
   - `future_hooks` 的埋线风格
   - `state_shift` 的重点层级
6. `FlavorRender.state_shift_focus` 必须能在 `state_shift` 里看到对应的重点层变化，而不是只写在 flavor 层里。
7. 如果同一把刀在两个反派手里只是文字换皮、结构不变，则视为风味失败。

## 8. 第一阶段验证要求

`v8.1` 最低必须验证：

1. 同一把刀在两个反派手里，`decision + explanation + flavor_render` 明显不同。
2. 同一个反派在两个场景里，`observer topology` 改变会影响选刀和 `state_shift`。
3. 不符合 `anti_conditions` 的刀必须进入 `rejected_knives`。
4. 缺失 `observer_requirements` 的刀必须被硬过滤，而不是仅仅降分。
5. 任何 `forbidden_moves` 都不得进入打分候选池。
6. `StateLedgerShift` 各层边界不能串写。
7. `VillainFeedbackPacket` 不能退回到叙述性平铺结构。
8. 没有合适刀法时，系统要输出可解释 fallback，而且 fallback 不能伪装成一把主刀。
9. `selection_mode="fallback"` 时，`primary_knife_id` 与 `secondary_knife_id` 必须为空，`selected_signals` 必须为空。
10. `FlavorRender.structural_targets` 必须显式标记至少 2 个被改写的结构面。
11. `FlavorRender` 必须改变结构化输出，而不只是改变叙述语气。
12. `TransitionLayer` 必须显式写出 `prior_state`、`next_state`、`transition_reason`。
13. `upgrade_trigger` / `upgrade_path` 不能只写进评语，必须进入结构层。
14. 失败、修复、升级、坍塌的状态迁移不能继续停留在 controller 口头逻辑里。

## 9. 当前建议的最小落点

如果开始实现，第一版建议只动下面这些文件：

1. `backend/app/services/narrative_v8/schemas.py`
2. `backend/app/services/narrative_v8/knife_library.py`
3. `backend/app/services/narrative_v8/constraints.py`
4. `backend/app/services/narrative_v8/selection.py`
5. `backend/app/services/narrative_v8/flavor.py`
6. `backend/app/services/narrative_v8/ledger.py`
7. `backend/app/services/narrative_v8/transitions.py`
8. `backend/app/services/narrative_v8/controller.py`
9. `backend/app/services/narrative_v8/__init__.py`
10. `tests/test_narrative_v8_schemas.py`
11. `tests/test_narrative_v8_knife_library.py`
12. `tests/test_narrative_v8_selection.py`
13. `tests/test_narrative_v8_flavor.py`
14. `tests/test_narrative_v8_ledger.py`
15. `tests/test_narrative_v8_transitions.py`
16. `tests/test_narrative_v8_controller.py`

## 10. 一句话 handoff

> `v8.1` 不是为了复制某一个会算计的反派腔调，而是为了在当前 Python narrative 服务体系里，生成“不同反派如何基于自己的旧伤、信念、观众结构和长线状态，把同一套小刀子用出完全不同邪道风味”的独立控制面。
