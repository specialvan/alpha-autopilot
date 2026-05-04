# V8.1 工程化收紧总稿

> 依据文档：
> - `claude_review_package/v8/V8_CLAUDE_REVIEW_SUMMARY.md`
> - `claude_review_package/v8/V8_CLAUDE_REVIEW_EVIDENCE.md`
> - `claude_review_package/v8/V8_CODEX_REVIEW_TOTAL.md`
>
> 目标不是继续扩写“坏女人设定”，而是把已经固定的证据链压成可实现、可验证、可约束、可回退的 v8.1 工程闭环。

## v8.1 修订总览

v8.1 不推翻 v8 的主方向，也不重做概念层。它做的事情只有一件：把已经被 Claude 固定下来的结构，从“字段堆叠”收紧成“受约束的控制回路”。

v8.1 的工程闭环必须明确固定为：

`人格底盘 -> 合法性外壳 -> 心理缺口 -> 原语选择 -> 场景适配 -> 失手恢复 -> 升级触发 -> 状态迁移`

因此这轮修订的核心不是多加字段，而是做 5 个收口：

1. 让稳定核心对象继续保留，但把内部语义层拆干净。
2. 让所有选刀限制前置成 schema / compatibility / validation，而不是塞进 controller。
3. 让状态账本从 flat delta log 升级成分层快照与分层 shift。
4. 让 packet 变成可消费控制包，而不是结果摘要。
5. 让 flavor 有唯一来源和唯一出口，避免退化成文案糖衣。

## 保留项

v8.1 继续保留以下稳定核心，不推翻主结构：

1. 顶层实体继续保留：
   - `KnifePrimitive`
   - `VillainProfile`
   - `TargetProfile`
   - `SceneContext`
   - `LedgerSnapshot`
   - `StateLedgerShift`
   - `VillainFeedbackPacket`
   - `BuildVillainFeedbackInput / Output`

2. 反派稳定核心字段继续保留：
   - `core_wound`
   - `core_belief`
   - `psychology_literacy`
   - `preferred_knives`
   - `secondary_knives`
   - `forbidden_moves`
   - `public_mask`
   - `private_drive`
   - `time_horizon`
   - `blind_spot`
   - `escalation_rule`
   - `shame_relation`
   - `witness_need`
   - `flavor_profile`

3. 目标稳定核心字段继续保留：
   - `core_need`
   - `core_fear`
   - `weak_points`
   - `defense_style`
   - `resistance_style`
   - `witness_sensitivity`
   - `identity_anchor`

4. 场景稳定核心字段继续保留：
   - `arena`
   - `stake`
   - `visibility`
   - `relationship_distance`
   - `time_pressure`
   - `current_phase`
   - `existing_state`

5. 输出包稳定消费面继续保留：
   - `decision`
   - `explanation`
   - `state_shift`
   - `future_hooks`
   - `risk_if_exposed`
   - `flavor_render`

保留原则是：顶层对象不重命名，不把 v8.1 搞成新体系；只把原来过软的边界拆成显式子结构和显式验证关卡。

## 需要拆分或新增的结构

### 1. 状态账本

`StateLedger` 不能再被理解成单一 delta 表，必须拆成四层：

1. `relationship state`
   - `trust`
   - `debt`
   - `dependency`
   - `leverage`

2. `narrative state`
   - `suspicion`
   - `reputation`
   - `witness_alignment`
   - `explanation_control`

3. `psychological echo state`
   - `shame_load`
   - `wound_activation`
   - `protector_trigger`
   - `identity_destabilization`

4. `hook state`
   - `planted_hooks`
   - `armed_payoffs`
   - `recovered_hooks`

收口要求：

1. `LedgerSnapshot` 只表示当前分层局势。
2. `StateLedgerShift` 只表示本次动作的分层偏移。
3. `hook` 层只处理延迟回报和回收，不允许和 `relationship` 混写。
4. ledger 记录的是结构状态，不是事件流水。

### 2. 刀法约束

`preferredKnives / secondaryKnives / forbiddenMoves` 继续保留，但不再独立承担约束职责。

必须新增显式约束层：

1. `KnifeConstraintSet`
   - `scene_restrictions`
   - `target_restrictions`
   - `observer_requirements`
   - `anti_conditions`
   - `backfire_conditions`
   - `ineffective_conditions`
   - `flavor_conflicts`

2. `KnifeCompatibilityEdge`
   - `left`
   - `right`
   - `relation`
   - `reason`

收口要求：

1. profile 数组负责“偏好与禁手”。
2. constraint set 负责“何时不能用、何时会反噬、何时根本无效”。
3. compatibility graph 负责“刀和刀能不能串、为什么不能串”。
4. controller 不再推断这些规则。

### 3. 场景模型

`SceneContext` 不能只靠 `audience` 或 `observers` 作为简单数组。

必须保留并强化：

1. `SceneObserver.role`
   - `witness`
   - `judge`
   - `transmitter`
   - `buffer`
   - `recovery_node`

2. `SceneObserver.alignment`
   - `villain`
   - `target`
   - `mixed`
   - `volatile`
   - `unknown`

3. `PowerEdge`
   - `source`
   - `target`
   - `relation`
   - `asymmetry`

收口要求：

1. selector 不能只看 `visibility`。
2. observer topology 必须影响公开型刀法的可用性与分数。
3. power topology 必须影响服从/资源/体面类动作的合法窗口。

### 4. 输出包

`VillainFeedbackPacket` 必须显式拆成五层主结构加一个 flavor 出口：

1. `decision layer`
   - 选了什么
   - 没选什么
   - 为什么没选
   - fallback 是什么

2. `explanation layer`
   - 对外动作
   - 内在驱动
   - 目标误读
   - 为什么是现在
   - 为什么是这把刀
   - 为什么这个反派会这么用

3. `transition layer`
   - 本次是继续隐藏、进入修复、触发升级，还是进入坍塌

4. `state shift layer`
   - 本次行为如何改写四层账本

5. `hook layer`
   - 本次埋了什么未来钩子
   - 风险暴露后会怎么反咬

6. `flavor layer`
   - 只描述本次渲染，不反过来定义角色本体

### 5. 失手 / 修复 / 升级 / 状态迁移

这一块是我上一轮没有压到底的地方。Claude 固定的是完整链条，不只是 packet 更结构化而已，所以 v8.1 还必须把下面这些从“叙述存在”升级成“结构存在”：

1. `current_control_state`
   - 当前处于 `harmless / suspicious / distrusted / repair_attempt / partially_restored / upgraded / more_hidden / stronger / hardened / collapsed` 的哪一档

2. `failure_mode`
   - `shell_exposed`
   - `pace_lost`
   - `position_locked`
   - `narrative_lost`

3. `recovery_mode`
   - `re_feel_vulnerability`
   - `lower_intensity`
   - `retreat_to_safer_role`
   - `change_scene`
   - `re_establish_decorum`
   - `re_establish_narrative_control`

4. `upgrade_trigger`
   - `primitive_stalled`
   - `shell_seen_through`
   - `higher_order_path_found`

5. `upgrade_path`
   - `more_hidden`
   - `more_sparse`
   - `more_systemic`
   - `more_enduring`
   - `more_complex`
   - `outsourced_interpretation`

6. `transition layer`
   - 必须明确写出 `prior_state -> next_state`
   - 不能只在 explanation 里暗示

收口要求：

1. `fallback` 不等于自动 `collapsed`。
2. `recovery_mode` 和 `upgrade_trigger` 不能都靠 controller 临时拼出来。
3. `upgrade_path` 不能脱离 `upgrade_trigger` 单独漂浮。
4. `collapsed` 不能同时伪装成“已经恢复中”。

### 6. 风味字段

风味必须收口成四个层位，不能散在 profile、scene、explanation、packet 多处抢定义权：

1. `stable preference`
   - 只放在 `FlavorAxisProfile`
   - 这是长期稳定偏好

2. `temporary shell`
   - 由 `public_mask` 和场景共同生成
   - 是本场对外壳，不是永久人格

3. `scene render`
   - 由 `delivery_surface / pressure_channel / witness_posture / cost_profile / hook_style` 组成
   - 是这次动作在当前场景下的渲染结果

4. `output flavor`
   - 只存在于 `FlavorRender`
   - 必须作用到 `external_move / risk_if_exposed / future_hooks / state_shift`

## 必须前置的约束与验证

controller 之前，必须先把下面 7 类东西做实，且能单独测试：

1. `schema validation`
   - profile 约束
   - packet 形状约束
   - fallback 形状约束
   - public scene observer 约束
   - flavor 结构面约束

2. `knife compatibility validation`
   - incompatible edge 必须真实生效
   - conditional edge 必须有理由
   - incompatible knife 不能混进 selected pool

3. `scene compatibility validation`
   - observer requirement 缺失时必须硬拒绝
   - scene restriction 不满足时必须硬拒绝
   - power topology 不满足时必须阻断相关动作

4. `state boundary validation`
   - relationship / narrative / psychological / hook 四层不能串写
   - hook recovery 不能覆盖其他层
   - 单场高幅度 delta 数量要受限

5. `transition policy validation`
   - `prior_state` 必须可追溯
   - `next_state` 不能靠 explanation 文案猜
   - `upgrade_path` 不能无 trigger
   - `collapse` 不能伪装成 `recovery`

6. `differential validation`
   - same knife / different villain
   - same villain / different scene
   - observer topology changes public-pressure fit
   - flavor difference changes structure, not only wording

7. `fallback validation`
   - no-fit 时必须进入 `fallback`
   - `fallback` 不得伪装成选中了某把刀
   - `selected_signals` 必须为空

### 必须先做的 helper

先做 helper，再做 controller。最先落地的 helper 应该是：

1. `build_candidate_knife_ids`
   - 固化候选池来源

2. `evaluate_knife_rejection`
   - 固化 scene / target / observer / anti-condition / backfire / flavor conflict 的拒绝逻辑

3. `evaluate_compatibility_conflict`
   - 固化双刀兼容性判定

4. `select_knives`
   - 只负责硬过滤后打分、选主刀/副刀、生成 rejected reasons、生成 fallback

5. `render_flavor`
   - 只负责稳定偏好到本次 render 的投影

6. `build_state_shift`
   - 把 flavor focus 和 hooks 投到分层状态变化

7. `apply_state_shift`
   - 只负责四层账本边界内的安全应用

8. `derive_transition_outcome`
   - 只负责 `failure / recovery / upgrade / collapse` 状态机
   - 不允许 controller 内联分支

9. `build_risk_if_exposed / build_hook_seed / build_external_move_envelope`
   - 只做 packet 子层拼装

如果某条业务规则只能在 controller 里写出来，说明 helper 设计还没收紧到位。

## 实施顺序修订

v8.1 的实施顺序必须改成下面这条链，不允许再从 schema 直接跳 controller：

1. `schema definition`
   - 先固定 stable entities 和 nested sub-structures。

2. `constraint and compatibility rules`
   - 先定义刀法约束词表、兼容图、拒绝原因类型。

3. `validation layer`
   - 先把 schema / scene / knife / state boundary / fallback 的验证门建起来。

4. `knife library`
   - 再填默认 10 把刀和默认 compatibility graph。

5. `selection helpers`
   - 再做 hard-filter-first 的 selector。

6. `flavor rendering`
   - 再做稳定偏好到场景 render 的映射。

7. `layered ledger application`
   - 再做 state shift 生成、transition 派生和 snapshot 应用。

8. `controller orchestration`
   - 最后只拼输入、调 helper、组 packet、产出 next snapshot。

一句话原则：controller 只编排，不发现规则，不解释边界，不发明 fallback。

## 测试顺序修订

测试顺序必须同步改成下面这条链：

1. `schema tests`
   - 先证实对象边界和 packet 形状是硬的。

2. `compatibility tests`
   - 再证实刀法兼容、scene restriction、observer requirement、anti-condition 都是真正硬门。

3. `state transition tests`
   - 再证实分层 ledger 不串写、hook 不越界、delta 有边界，而且 transition state machine 不漂。

4. `differential tests`
   - 再证实 same knife / different villain 和 same villain / different scene 真的分化。

5. `fallback tests`
   - 再证实 no-fit 场景输出结构诚实。

6. `controller integration tests`
   - 最后才测 orchestration，确认 controller 没有偷塞业务规则。

验收顺序也要按这个逻辑看，而不是只跑 happy path。

## 仍然保留的风险

即使 v8.1 按上面收紧，仍然保留以下风险：

1. 所有角色仍然可能塌成同一个 smart-bad voice。
   - 原因不是 schema 不够多，而是差异测试集还不够宽。

2. flavor 仍然可能退化成纯文案。
   - 如果 `FlavorRender` 不能持续改写 packet 结构面，最后还是会只剩措辞差别。

3. ledger 仍然可能退化成 flat event log。
   - 一旦后续功能把跨层副作用塞回 controller，四层账本会重新塌平。

4. scene 仍然可能过粗导致 selector 失真。
   - 特别是 observer role 和 power topology 如果只填样例、不形成稳定词表，结果会开始漂。

5. recovery / upgrade / collapse 边界仍然可能太软。
   - 这轮我已经把字段 owner、transition owner、helper owner 补出来了，但阈值、触发器和切换策略还需要后续更系统的回归集压实。

6. 证据已经足够，但“证据到规则”的映射仍有枚举漂移风险。
   - 后续新增 villain family、scene family、knife primitive 时，必须继续通过 compatibility 和 differential tests 扩容，不能只加字段。

## 一句话结论

v8.1 的正确收口，不是“多写点反派设定”，而是把整套系统稳定成：

`人格底盘 -> 合法性外壳 -> 心理缺口 -> 原语选择 -> 场景适配 -> 失手恢复 -> 升级触发 -> 状态迁移`

这条链上的每一段，都有自己的 schema、helper、validation、fallback 和测试关卡。
