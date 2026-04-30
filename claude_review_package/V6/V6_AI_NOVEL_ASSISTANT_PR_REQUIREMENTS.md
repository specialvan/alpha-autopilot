# alpha-autopilot V6/V7 对标 AI-Novel-Writing-Assistant 开发 PR 需求文档

## 1. 文档定位

- 日期：2026-04-28
- 对标项目：`ExplosiveCoderflome/AI-Novel-Writing-Assistant`
- 对标地址：https://github.com/ExplosiveCoderflome/AI-Novel-Writing-Assistant
- 对标主题：AI 导演式长篇小说生产系统、Creative Hub、整本生产主链、写法引擎、RAG/知识库、任务恢复与桌面化
- 本项目承接阶段：alpha-autopilot V1 至 V6
- 输出目的：深度梳理该项目对 alpha-autopilot 的启发，并形成可拆分开发 PR 需求文档

本文不是复制对方项目的功能清单，而是把其产品判断和系统能力翻译为 alpha-autopilot 当前阶段可执行的研发需求。

alpha-autopilot 当前已经具备：

- V1/V2：章节推荐、Workbench、基础稳定链路；
- V3：读者留存目标函数与生成控制层；
- V4：人物关系、性格、外部压力驱动剧情；
- V5：留存欲望向量、六步情节骨架、情绪滑块、角色功能位、关系图、宏观结构、Prompt 压缩；
- V6：正在引入动态故事世界推演、多路径模拟、事件注入、角色访谈与群体记忆。

AI-Novel-Writing-Assistant 对 alpha-autopilot 最大的启发是：

> 仅有“更聪明的推荐/推演”还不够，长篇小说系统还必须具备“从一句灵感到整本完结”的生产主链、任务编排、资产沉淀、状态恢复、写法资产和新手低认知入口。

因此，本需求文档建议在 V6 动态推演之外，新增一组面向“整本生产系统化”的 PR：PR-AA-16 至 PR-AA-25。

## 2. AI-Novel-Writing-Assistant 核心能力梳理

### 2.1 产品定位：AI 导演式长篇小说生产系统

该项目不是传统“输入 prompt，生成一段正文”的聊天壳，而是定位为：

- 从一句灵感出发；
- 自动构建书级 framing、世界观、角色、主线和卷级规划；
- 管理知识、设定、拆书资产与写法资产；
- 编排章节写作、审阅、修复、状态同步；
- 支持整本批量推进和任务恢复；
- 目标用户优先是完全不懂写作的新手。

对 alpha-autopilot 的启发：

- 当前 alpha-autopilot 更强在“推荐/评分/推演/解释”，但仍偏模块化能力；
- 需要把这些能力收束成一条默认生产主链；
- 系统目标应从“给作者更好的建议”升级为“带作者持续推进整本小说”。

### 2.2 自动导演开书

AI-Novel-Writing-Assistant 支持从一句模糊灵感进入自动导演：

- 生成多套整本方向；
- 生成标题组；
- 支持按重要阶段审核、自动推进到可开写、继续自动执行前 10 章；
- 支持检查点恢复、现有项目接管、页内继续推进、换模型重试；
- 角色阶段有质量门禁，不把坏角色阵容直接落库。

对 alpha-autopilot 的启发：

- alpha-autopilot 已有 StoryState、MacroStoryStructure、V6 NarrativeSeed，但缺少“一句灵感 -> 可开写项目”的导演入口；
- 可以把 V6 的种子抽取与多路径推演向前扩展为“开书导演”；
- 需要引入方向候选、标题候选、书级承诺、前 10 章承诺和审核节点。

### 2.3 Creative Hub 与 Agent Runtime

该项目将对话、追问、规划、工具调用、执行状态和回合总结收束到 Creative Hub，并具备：

- Planner；
- Tool Registry；
- Runtime；
- 审批节点；
- 状态卡片；
- 中断恢复链路。

对 alpha-autopilot 的启发：

- alpha-autopilot Workbench 当前更像“能力展示与推荐操作台”；
- 需要升级为“创作中枢”，承载规划、推演、任务执行、审批和恢复；
- V6 多路径推演、角色访谈、事件注入等能力需要一个统一 Runtime，而不是多个独立按钮。

### 2.4 整本生产主链

AI-Novel-Writing-Assistant 明确收束了整本生产流程：

1. 书级 framing；
2. 故事宏观规划/约束引擎；
3. 动态角色系统；
4. 卷战略；
5. 卷骨架；
6. 卷内节奏板；
7. 当前卷章节列表；
8. 章节细化 bundle；
9. 章节执行/runtime；
10. state sync；
11. narrative audit/replan。

对 alpha-autopilot 的启发：

- alpha-autopilot 目前已有局部能力，但缺少类似“唯一默认主链”的产品约束；
- V6 的动态推演应嵌入整本生产链，而不是独立的模拟工具；
- 章节推荐、路径推演、角色关系、伏笔回收、审计和重规划需要统一状态流。

### 2.5 写法引擎

该项目将写法从 prompt 文本升级为长期资产：

- 可从文本提取写法特征；
- 保存原文样本；
- 特征池可编辑、启用、停用、组合；
- 写法规则可重编译；
- 写法资产可绑定到整本书；
- 参与生成、检测和修正链路；
- 有反 AI 规则。

对 alpha-autopilot 的启发：

- 当前 alpha-autopilot 的 PromptCompressor 和风格约束偏运行时上下文处理；
- 需要引入长期 StyleAsset/StyleDNA 管理；
- 写法不应只是“提示词附加段”，而应成为可版本化、可测试、可绑定、可审计的生成控制资产。

### 2.6 世界观、角色、拆书、知识库联动

该项目将世界观、角色、拆书和知识库串为长期记忆系统：

- 世界观支持创建、分层、快照、深化问答、一致性检查和小说绑定；
- 角色系统从静态角色卡升级为动态角色资产；
- 拆书结果可发布到知识库，再回灌到规划和正文生成；
- 知识库支持文档管理、向量检索、关键词检索和重建任务追踪。

对 alpha-autopilot 的启发：

- V6 NarrativeSeed/RelationshipGraph/GroupMemory 是结构化世界的底座；
- 仍需要“资产生命周期管理”：创建、绑定、版本、快照、发布、回灌、回滚；
- 拆书/参考作品分析应成为提升推荐与生成质量的输入源。

### 2.7 任务中心、恢复与可解释状态

AI-Novel-Writing-Assistant 强调长任务可恢复：

- 自动导演任务可服务重启恢复；
- 章节执行可补跑最早未完成章节；
- 等待审批后继续不会误跳；
- 任务中心展示排队、运行、失败状态；
- 状态字段包括 displayStatus、blockingReason、resumeAction、lastHealthyStage 等方向。

对 alpha-autopilot 的启发：

- V6 多路径推演、事件注入、批量章节执行、知识库重建都可能是长任务；
- 需要 TaskRuntime/Checkpoint/Resume 机制；
- 用户必须知道“为什么停、怎么继续、上一个健康阶段在哪里”。

### 2.8 模型路由与本地/桌面分发

该项目支持：

- 多模型供应商；
- 不同任务配置不同模型；
- SQLite 默认运行；
- Qdrant/RAG 可选；
- Electron 桌面版作为非开发用户入口。

对 alpha-autopilot 的启发：

- alpha-autopilot 需要从“研发验证系统”走向“可被普通作者使用”；
- 不应要求用户理解所有服务依赖；
- 模型路由应按任务类型拆开：规划、推演、写作、审阅、修复、访谈、抽取。

## 3. 对 alpha-autopilot 的差距判断

| 能力域 | AI-Novel-Writing-Assistant | alpha-autopilot 当前状态 | 差距判断 |
| --- | --- | --- | --- |
| 开书入口 | 一句灵感自动导演 | 有 StoryState/V6 seed，但无完整导演入口 | 需补 P0 |
| 整本主链 | 明确从 framing 到 audit/replan | 阶段能力强，但主链分散 | 需补 P0 |
| Agent Runtime | Planner/Tool/Runtime/审批/恢复 | Workbench + API，Runtime 概念弱 | 需补 P0/P1 |
| 写法引擎 | 长期 StyleAsset，可提取/绑定/检测/修复 | Prompt 压缩与局部风格约束 | 需补 P1 |
| 知识库/RAG | 文档管理、向量/关键词、重建任务 | Story Bible/关系图/记忆，RAG 弱 | 需补 P1/P2 |
| 任务恢复 | 检查点、恢复、任务中心 | 单次 API/脚本为主 | 需补 P0 |
| 新手入口 | 低认知 AI 主驾 | 更偏专家/评审/工程验证 | 需补 P1 |
| 桌面化 | Electron 分发路径 | 未规划 | P2 可选 |

## 4. 新增 PR 总览

建议新增 PR-AA-16 至 PR-AA-25，作为 V6 后半段或 V7 需求池。若 V6 当前主线仍聚焦 MiroFish 动态推演，则 PR-AA-16 至 PR-AA-20 应优先作为“V6.5 整本生产主链补强”，PR-AA-21 至 PR-AA-25 可进入 V7。

| 编号 | 功能名称 | 优先级 | 核心目标 | 主要启发来源 |
| --- | --- | --- | --- | --- |
| PR-AA-16 | AI 自动导演开书入口 | P0 | 从一句灵感生成可开写项目与方向候选 | 自动导演开书 |
| PR-AA-17 | NovelProductionOrchestrator 整本生产编排器 | P0 | 将规划、推演、章节执行、审计、重规划收成默认主链 | 整本生产主链 |
| PR-AA-18 | TaskRuntime 检查点与恢复系统 | P0 | 为长任务提供 checkpoint、resume、failure explanation | 任务中心/恢复 |
| PR-AA-19 | Workbench Creative Hub 升级 | P1 | 将 Workbench 升级为规划、工具、审批、状态中枢 | Creative Hub |
| PR-AA-20 | 章节执行包与审阅修复闭环 | P1 | 将推演 winner 转为章节任务单，并接入审阅/修复 | 章节执行/质量修复 |
| PR-AA-21 | StyleAsset 写法引擎 | P1 | 写法特征提取、绑定、检测、修复和反 AI 规则 | 写法引擎 |
| PR-AA-22 | 参考作品拆书与知识回灌 | P1 | 拆书结果进入知识库/Story Bible/写法资产 | 拆书分析/知识库 |
| PR-AA-23 | Unified Asset Lifecycle 资产版本与快照 | P1 | 世界观、角色、关系、写法、伏笔资产统一版本/绑定/回滚 | 世界观/角色/知识库 |
| PR-AA-24 | ModelRouteRegistry 阶段级模型路由 | P2 | 按任务配置不同模型与 fallback | 模型路由 |
| PR-AA-25 | Desktop/Local-first 作者分发模式 | P2 | 面向非开发用户的本地运行/桌面打包路径 | Windows 桌面版 |

## 5. PR 详细需求

### 5.1 PR-AA-16：AI 自动导演开书入口

#### 背景

alpha-autopilot 目前对“已有故事状态”的推荐和推演能力更强，但对“从零开书”的新手路径不足。AI-Novel-Writing-Assistant 的自动导演证明：长篇系统的第一关键点是降低开书认知负担，让用户从一句灵感进入可写项目。

#### 输入

- 一句灵感或题材方向；
- 可选目标读者感受；
- 可选题材/类型；
- 可选主角偏好；
- 可选篇幅目标；
- 可选自动推进模式：`review_each_stage` / `auto_to_ready` / `auto_to_front10`。

#### 输出

`DirectorOpeningPlan` 至少包含：

- `candidate_directions[]`：2 至 3 套整本方向；
- `title_candidates[]`：每套方向的标题组；
- `book_framing`：题材、卖点、核心承诺、读者情绪目标；
- `main_conflict`：长期对立与推进方式；
- `first_30_chapter_promises`：前 30 章承诺；
- `initial_character_roster`：初始角色阵容；
- `world_seed`：世界观种子；
- `review_points[]`：需要作者确认的节点；
- `next_action`。

#### 功能要求

1. 新增自动导演开书 API；
2. 支持多方向候选，而不是只生成一个方案；
3. 候选方向可进入 PR-AA-09 NarrativeSeed 管道；
4. 角色阵容必须接入 PR-AA-10 参数化与质量门禁；
5. 支持作者选择、局部重做、标题组重做；
6. 不覆盖手动创建入口；
7. 所有自动生成内容默认 pending review。

#### 验收标准

- 输入一句灵感可返回至少 2 套方向；
- 每套方向包含标题、卖点、主线冲突和前 30 章承诺；
- 作者可选择其中一套进入 StoryState 初始化；
- 低质量角色名或功能位角色进入 review，而非直接落库；
- deterministic mock 下测试稳定。

#### 建议文件

- `backend/app/services/narrative_v7/director_opening.py`
- `backend/app/services/narrative_v7/schemas.py`
- `backend/app/api/routes/narrative_v7.py`
- `tests/test_director_opening.py`

### 5.2 PR-AA-17：NovelProductionOrchestrator 整本生产编排器

#### 背景

alpha-autopilot 各阶段能力已经较强，但缺少唯一默认主链。PR-AA-17 负责建立整本生产编排器，把开书、宏观规划、角色、卷、章节、推演、审阅、修复、状态同步和重规划收束为一个可追踪流程。

#### 默认主链

1. `book_framing`；
2. `story_macro`；
3. `character_preparation`；
4. `volume_strategy`；
5. `volume_skeleton`；
6. `beat_sheet`；
7. `chapter_plan`；
8. `simulation_recommendation`；
9. `chapter_task_sheet`；
10. `chapter_execution`；
11. `review`；
12. `repair`；
13. `state_sync`；
14. `audit`；
15. `replan`。

#### 功能要求

1. 新增 orchestrator service；
2. 支持从手动项目、自动导演项目、已有项目接管进入同一主链；
3. 将 V6 多路径推演作为 `simulation_recommendation` 阶段；
4. 每个阶段输出标准 `StageResult`；
5. 支持阶段跳过、重试、回退和人工确认；
6. 与 PR-AA-18 TaskRuntime 集成；
7. 不破坏现有 V2/V4/V6 API。

#### 验收标准

- 可从已有 StoryState 启动 orchestrator；
- 至少跑通 `chapter_plan -> simulation_recommendation -> chapter_task_sheet`；
- 每阶段有状态、输入、输出、错误和 next_action；
- 失败阶段可重试；
- 手动入口和自动导演入口进入同一阶段模型。

#### 建议文件

- `backend/app/services/narrative_v7/orchestrator.py`
- `backend/app/services/narrative_v7/stage_contracts.py`
- `tests/test_novel_production_orchestrator.py`

### 5.3 PR-AA-18：TaskRuntime 检查点与恢复系统

#### 背景

长篇生产任务不是单次 API 调用。自动导演、拆书、知识库重建、多路径推演、批量章节执行都可能中断。AI-Novel-Writing-Assistant 的任务恢复机制对 alpha-autopilot 是 P0 启发。

#### 数据模型

`NarrativeTaskRuntime` 至少包含：

- `task_id`；
- `task_type`；
- `status`：queued/running/waiting_review/failed/completed/cancelled；
- `current_stage`；
- `last_healthy_stage`；
- `checkpoint_payload`；
- `display_status`；
- `blocking_reason`；
- `resume_action`；
- `retry_count`；
- `created_at` / `updated_at`；
- `failure_logs[]`。

#### 功能要求

1. 提供任务创建、更新、查询、恢复 API；
2. 支持 checkpoint 写入；
3. 支持服务重启后恢复；
4. 支持 waiting_review 状态；
5. 支持跳过非阻断章节或路径，但必须记录审计；
6. 任务中心可消费 display_status/blocking_reason/resume_action。

#### 验收标准

- 模拟任务在 stage 2 中断后可从 checkpoint 继续；
- 失败任务能返回明确 blocking_reason；
- waiting_review 任务不会被误标为 failed；
- 查询接口返回 last_healthy_stage；
- deterministic 测试覆盖 queued/running/failed/resume。

#### 建议文件

- `backend/app/services/narrative_v7/task_runtime.py`
- `backend/app/services/narrative_v7/task_store.py`
- `tests/test_task_runtime_resume.py`

### 5.4 PR-AA-19：Workbench Creative Hub 升级

#### 背景

现有 Workbench 是 alpha-autopilot 的核心操作界面，但它更像“预览/推荐/上下文面板”。AI-Novel-Writing-Assistant 的 Creative Hub 提醒我们：创作中枢应统一承载对话、规划、工具调用、任务状态、审批和回合总结。

#### 功能要求

1. 在 V2 Workbench 中新增 Creative Hub 面板；
2. 统一展示当前项目阶段、下一步建议、运行中任务、等待审批项；
3. 支持用户用自然语言提出目标，由 planner 映射到工具调用；
4. 工具调用范围先限制为安全操作：种子抽取、角色参数化、多路径推演、章节任务单生成；
5. 每次回合生成 `TurnSummary`；
6. 与 TaskRuntime 展示对齐。

#### 输出模型

`CreativeHubTurn` 至少包含：

- `user_intent`；
- `planned_actions[]`；
- `tool_calls[]`；
- `approval_required`；
- `state_cards[]`；
- `turn_summary`；
- `next_action`。

#### 验收标准

- Workbench 可展示运行中任务与等待审批项；
- 用户请求“帮我推演下一章”可映射到 PR-AA-11；
- 工具调用前可要求确认；
- turn_summary 可保存；
- 不允许 Creative Hub 绕开后端 schema 直接改状态。

#### 建议文件

- `backend/app/services/narrative_v7/creative_hub.py`
- `ui-react/src/features/v2Workbench/components/CreativeHubPanel.tsx`
- `tests/test_creative_hub_planner.py`

### 5.5 PR-AA-20：章节执行包与审阅修复闭环

#### 背景

V6 多路径推演输出 winner 后，还需要转化为“可写章节任务”。AI-Novel-Writing-Assistant 的章节执行区、质量修复区启发 alpha-autopilot：推荐结果必须进入执行、审阅、修复和状态同步闭环。

#### 输入

- PR-AA-11 winner path；
- 六步情节骨架；
- 角色参数；
- 关系变化；
- 留存评分解释；
- 当前章节目标。

#### 输出

`ChapterExecutionPackage` 至少包含：

- `chapter_goal`；
- `must_include`；
- `must_avoid`；
- `character_obligations`；
- `relationship_obligations`；
- `payoff_obligations`；
- `ending_hook_requirement`；
- `risk_flags`；
- `review_checklist`；
- `repair_strategy`：默认 `patch_first`。

#### 功能要求

1. 将推演 winner 转为章节任务单；
2. 支持审阅 checklist；
3. 支持修复建议；
4. 默认局部修复优先，整章重写需明确触发；
5. 输出状态变更候选，交由 StateCommit 机制确认；
6. 与 V3 留存目标保持一致。

#### 验收标准

- winner path 可生成合法 ChapterExecutionPackage；
- package 包含必写、禁写、角色义务、关系义务、结尾钩子；
- review 可发现至少一类风险；
- repair_strategy 默认 patch_first；
- 不直接修改正式正文或 Story Bible。

#### 建议文件

- `backend/app/services/narrative_v7/chapter_execution_package.py`
- `backend/app/services/narrative_v7/chapter_review.py`
- `tests/test_chapter_execution_package.py`

### 5.6 PR-AA-21：StyleAsset 写法引擎

#### 背景

AI-Novel-Writing-Assistant 的写法引擎说明：写法必须沉淀为长期资产，而不是临时 prompt。alpha-autopilot 需要建立 StyleAsset，使风格、句式、叙事密度、反 AI 规则可以被提取、绑定、测试和修复。

#### 数据模型

`StyleAsset` 至少包含：

- `style_id`；
- `name`；
- `source_samples[]`；
- `feature_pool[]`；
- `enabled_features[]`；
- `anti_ai_rules[]`；
- `compile_prompt_fragment`；
- `version`；
- `binding_scope`：book/volume/chapter；
- `evaluation_metrics`。

#### 功能要求

1. 从参考文本提取写法特征；
2. 保存原文样本；
3. 支持启用/停用/组合特征；
4. 支持绑定到项目、卷或章节；
5. 生成时注入编译后的写法片段；
6. 审阅时检测风格偏移；
7. 修复时可输出局部改写建议；
8. 支持反 AI 规则，例如减少模板腔、解释腔、总结腔。

#### 验收标准

- 给定样本文本可提取至少 3 个写法特征；
- StyleAsset 可绑定到 StoryState 或章节任务；
- compile_prompt_fragment 可生成；
- 审阅可识别至少一类风格偏移；
- 不依赖真实 LLM 的 mock extractor 测试可通过。

#### 建议文件

- `backend/app/services/narrative_v7/style_asset.py`
- `backend/app/services/narrative_v7/style_review.py`
- `tests/test_style_asset_engine.py`

### 5.7 PR-AA-22：参考作品拆书与知识回灌

#### 背景

参考作品拆书可以为新书提供题材模式、节奏模式、写法特征和结构经验。AI-Novel-Writing-Assistant 已将拆书与知识库/写法资产联动。alpha-autopilot 应把 reverse outline 能力纳入主链。

#### 输入

- 参考作品文本；
- 拆书范围：full_document/first_n_segments/segment_range；
- 目标：结构、角色、节奏、写法、爽点、伏笔；
- 是否发布到知识库或写法资产。

#### 输出

`BookAnalysisResult` 至少包含：

- `coverage`；
- `segment_notes[]`；
- `structure_patterns[]`；
- `pacing_patterns[]`；
- `character_patterns[]`；
- `hook_patterns[]`；
- `style_feature_candidates[]`；
- `knowledge_items[]`；
- `publish_warnings[]`。

#### 功能要求

1. 支持前 N 片段试跑；
2. 支持暂停、恢复、扩范围；
3. 所有局部结果必须带 coverage；
4. 可发布到知识库；
5. 可生成 StyleAsset 候选；
6. 不允许局部拆书结果静默冒充整书结论。

#### 验收标准

- first_n_segments 模式输出 coverage；
- 暂停后可从已完成 segment 恢复；
- 发布到知识库时保留来源和范围；
- 可生成至少 1 个 style_feature_candidate；
- coverage warning 可被前端展示。

#### 建议文件

- `backend/app/services/narrative_v7/book_analysis.py`
- `backend/app/services/narrative_v7/knowledge_ingestion.py`
- `tests/test_book_analysis_coverage.py`

### 5.8 PR-AA-23：Unified Asset Lifecycle 资产版本与快照

#### 背景

alpha-autopilot 已有 StoryState、RelationshipGraph、GroupMemory、StyleAsset 等多个资产形态。随着 V6/V7 增强，如果没有统一资产生命周期，系统会出现“多个模块眼里不是同一本书”的问题。

#### 资产范围

- BookFraming；
- NarrativeSeed；
- CharacterProfile；
- RelationshipGraph；
- GroupMemory；
- StyleAsset；
- PayoffLedger；
- ChapterExecutionPackage；
- SimulationResult。

#### 功能要求

1. 每类资产支持版本号；
2. 支持 snapshot；
3. 支持 binding scope；
4. 支持 pending review 与 confirmed 两类状态；
5. 支持 rollback；
6. 支持 asset diff；
7. 支持来源追踪：AI generated/user edited/imported/simulation derived。

#### 验收标准

- 任一资产更新前可创建 snapshot；
- pending review 资产不会默认污染正式状态；
- rollback 后读取到旧版本；
- diff 可显示字段级变化；
- SimulationResult 写入正式资产必须经过确认。

#### 建议文件

- `backend/app/services/narrative_v7/asset_lifecycle.py`
- `backend/app/services/narrative_v7/asset_diff.py`
- `tests/test_asset_lifecycle.py`

### 5.9 PR-AA-24：ModelRouteRegistry 阶段级模型路由

#### 背景

不同任务需要不同模型：抽取、规划、推演、正文、审阅、修复、访谈、压缩、嵌入。AI-Novel-Writing-Assistant 已支持模型路由。alpha-autopilot 应建立统一模型路由注册表，避免所有能力硬吃同一模型。

#### 路由维度

- `seed_extraction`；
- `director_opening`；
- `character_parameterization`；
- `parallel_simulation`；
- `chapter_planning`；
- `chapter_writing`；
- `chapter_review`；
- `chapter_repair`；
- `character_interview`；
- `prompt_compression`；
- `book_analysis`。

#### 功能要求

1. 支持每类任务配置 provider/model；
2. 支持 fallback；
3. 支持连通性测试；
4. 支持成本/延迟日志；
5. 默认可使用当前配置，不强制用户设置全部路由；
6. 不在测试中调用真实模型。

#### 验收标准

- 未配置路由时走默认模型；
- 配置 route 后对应任务使用指定模型；
- 主模型失败可 fallback；
- 日志记录 requested/effective model；
- 路由配置不泄露 API Key。

#### 建议文件

- `backend/app/services/narrative_v7/model_routes.py`
- `backend/app/core/config.py`
- `tests/test_model_route_registry.py`

### 5.10 PR-AA-25：Desktop/Local-first 作者分发模式

#### 背景

AI-Novel-Writing-Assistant 已将 Electron 桌面版作为非开发用户入口。alpha-autopilot 当前更偏开发者/评审者环境。若未来面向普通作者，需要 local-first 或桌面化路径。

#### 一期范围

1. 不重写核心业务；
2. 保留 Web/源码运行；
3. 增加 local-first 配置说明或最小桌面壳方案；
4. 默认 SQLite/本地文件；
5. RAG/Qdrant 不作为首发硬依赖；
6. 首启向导只暴露模型配置和默认资源补齐。

#### 验收标准

- 非开发用户可按文档启动 local-first 模式；
- 首启可完成模型配置；
- 默认资源可自动补齐；
- 不要求用户配置 Qdrant；
- 不破坏当前后端和前端开发路径。

#### 建议文件

- `docs/local-first-author-mode.md`
- `scripts/run_local_author_mode.py`
- 后续如进入桌面化，再新增 `desktop/`。

## 6. 与现有 V6 MiroFish 推演需求的关系

V6 MiroFish 文档强调的是“动态故事世界推演”：

- PR-AA-09：种子抽取；
- PR-AA-10：角色参数化；
- PR-AA-11：多路径推演；
- PR-AA-12：冲突探针；
- PR-AA-13：事件注入；
- PR-AA-14：角色访谈；
- PR-AA-15：群体记忆。

本文件新增 PR-AA-16 至 PR-AA-25 强调的是“整本生产系统化”：

- 开书入口；
- 整本编排；
- 任务恢复；
- Creative Hub；
- 章节执行；
- 写法资产；
- 拆书知识回灌；
- 资产生命周期；
- 模型路由；
- 作者分发。

两者不是替代关系，而是上下游关系：

```text
PR-AA-16 自动导演开书
  -> PR-AA-09 NarrativeSeed
  -> PR-AA-10 角色参数化
  -> PR-AA-11 多路径推演
  -> PR-AA-20 章节执行包
  -> PR-AA-17 Orchestrator
  -> PR-AA-18 TaskRuntime
  -> PR-AA-23 资产生命周期
```

换句话说：

- MiroFish 启发 alpha-autopilot 获得“动态推演能力”；
- AI-Novel-Writing-Assistant 启发 alpha-autopilot 把“动态推演能力”放进整本生产链。

## 7. 推荐实施顺序

### 7.1 第一批：P0 主链补齐

1. PR-AA-18 TaskRuntime 检查点与恢复系统；
2. PR-AA-17 NovelProductionOrchestrator；
3. PR-AA-16 AI 自动导演开书入口；
4. PR-AA-20 章节执行包与审阅修复闭环。

理由：

- 没有 TaskRuntime，长链路不可恢复；
- 没有 Orchestrator，各能力继续分散；
- 没有自动导演，新手入口不足；
- 没有章节执行包，推演 winner 无法落到正文生产。

### 7.2 第二批：P1 资产与中枢深化

5. PR-AA-19 Workbench Creative Hub；
6. PR-AA-21 StyleAsset 写法引擎；
7. PR-AA-23 Unified Asset Lifecycle；
8. PR-AA-22 参考作品拆书与知识回灌。

理由：

- Creative Hub 提升可用性；
- StyleAsset 提升文风稳定；
- Asset Lifecycle 防止多模块状态分叉；
- BookAnalysis 提供参考作品知识输入。

### 7.3 第三批：P2 产品化增强

9. PR-AA-24 ModelRouteRegistry；
10. PR-AA-25 Desktop/Local-first 作者分发模式。

理由：

- 模型路由降低成本并提升稳定性；
- local-first/desktop 是产品化入口，不应抢在主链稳定前。

## 8. API 与模块建议

建议新增 `backend/app/services/narrative_v7/`，作为“整本生产主链与 AI 导演系统”命名空间。V6 继续保留动态推演模块，V7 负责把这些能力编排成完整产品链路。

建议结构：

- `schemas.py`
- `director_opening.py`
- `orchestrator.py`
- `stage_contracts.py`
- `task_runtime.py`
- `creative_hub.py`
- `chapter_execution_package.py`
- `style_asset.py`
- `book_analysis.py`
- `knowledge_ingestion.py`
- `asset_lifecycle.py`
- `model_routes.py`

建议 API：

| Method | Path | 用途 | PR |
| --- | --- | --- | --- |
| POST | `/api/narrative/v7/director/opening` | 一句灵感自动开书 | PR-AA-16 |
| POST | `/api/narrative/v7/orchestrator/start` | 启动整本生产主链 | PR-AA-17 |
| POST | `/api/narrative/v7/orchestrator/{id}/continue` | 继续主链 | PR-AA-17/18 |
| GET | `/api/narrative/v7/tasks/{id}` | 查询任务状态 | PR-AA-18 |
| POST | `/api/narrative/v7/tasks/{id}/resume` | 恢复任务 | PR-AA-18 |
| POST | `/api/narrative/v7/creative-hub/turn` | Creative Hub 回合 | PR-AA-19 |
| POST | `/api/narrative/v7/chapter/package` | 生成章节执行包 | PR-AA-20 |
| POST | `/api/narrative/v7/styles/extract` | 提取写法资产 | PR-AA-21 |
| POST | `/api/narrative/v7/book-analysis/start` | 启动拆书任务 | PR-AA-22 |
| POST | `/api/narrative/v7/assets/{id}/snapshot` | 创建资产快照 | PR-AA-23 |
| GET | `/api/narrative/v7/model-routes` | 查询模型路由 | PR-AA-24 |

## 9. 测试与验收策略

### 9.1 P0 必测

- `tests/test_director_opening.py`
- `tests/test_novel_production_orchestrator.py`
- `tests/test_task_runtime_resume.py`
- `tests/test_chapter_execution_package.py`

### 9.2 P1/P2 必测

- `tests/test_creative_hub_planner.py`
- `tests/test_style_asset_engine.py`
- `tests/test_book_analysis_coverage.py`
- `tests/test_asset_lifecycle.py`
- `tests/test_model_route_registry.py`

### 9.3 回归要求

新增 PR-AA-16 至 PR-AA-25 不得破坏：

- V2 preview/workbench 流程；
- V3 retention scoring；
- V4 relationship/character/pressure bridge；
- V5 PR-AA-01 至 PR-AA-08；
- V6 PR-AA-09 至 PR-AA-15。

### 9.4 端到端验收口径

最小 V7 P0 成功标准：

> 用户输入一句灵感，系统生成 2 至 3 套开书方向；用户选定一套后，系统生成 NarrativeSeed 和角色参数，启动多路径推演，选出 winner，生成章节执行包，并以 TaskRuntime 记录整个过程的阶段状态、检查点和下一步建议。

完整 V7 成功标准：

> 用户可以在 Creative Hub 中从开书、规划、推演、章节执行、审阅、修复、状态同步到重规划持续推进，并能使用写法资产、拆书知识、资产快照和模型路由降低长篇创作风险。

## 10. 风险与边界

### 10.1 不要盲目复制对方全栈产品形态

AI-Novel-Writing-Assistant 是 TypeScript/Express/Prisma/LangGraph/React/桌面化路线。alpha-autopilot 当前是 Python/FastAPI 风格后端加 React 前端，不应为了对标而迁移技术栈。

应吸收的是：

- 产品链路；
- 状态治理；
- 长任务恢复；
- 资产化思想；
- 新手低认知入口。

不应直接复制的是：

- 具体目录；
- Prisma 数据模型；
- Electron 工程；
- AGPL 代码实现。

### 10.2 自动导演不能变成不可控黑盒

自动导演必须保留审核节点、候选解释、局部重做和人工确认。不能把“自动推进”理解为“全部自动落库”。

### 10.3 写法引擎不能污染内容安全边界

StyleAsset 只能表达风格与表达策略，不能引入受版权限制的原文复刻。参考文本应保留来源、权限和样本范围。

### 10.4 拆书结果必须带 coverage

局部拆书不能冒充整书规律。所有拆书结论进入知识库、写法资产或生成链路时必须携带 coverage。

### 10.5 桌面化不应抢占主链开发资源

PR-AA-25 应在 P0 主链稳定后推进。否则容易把工程重点从“小说生产成功率”转移到“分发壳层”。

## 11. 一句话总结

AI-Novel-Writing-Assistant 对 alpha-autopilot 的最大启发是：动态推演只是能力核心，真正让作者持续完成长篇小说的是“AI 导演 + 整本生产主链 + 任务恢复 + 写法资产 + 知识回灌 + 低认知入口”。因此 alpha-autopilot 在 V6 的多路径推演之后，应继续用 PR-AA-16 至 PR-AA-25 把这些能力收束成一个可持续推进整本小说的 AI 导演系统。
