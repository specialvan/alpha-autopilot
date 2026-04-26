# alpha-autopilot 全量代码评审报告

评审日期：2026-04-21

评审结论：不通过

结论说明：当前工程在后端启动、反馈写入、历史导出、SQLite 线程使用、SQLite 优先 + 文件回退一致性、历史看板筛选语义上存在确定性故障或高概率数据失真问题。现阶段不建议继续叠加功能，应先修复主链路可用性与数据一致性。

## Blocker 风险

1. 后端当前主入口无法启动。

文件：`alpha_autopilot/__init__.py:6-10,12-31`，`backend/app/services/narrative/training_service.py:8-17`，`backend/app/services/narrative/feedback_service.py:7`，`backend/app/services/narrative/history_service.py:5`，`backend/app/services/narrative/history_export_service.py:7`，`backend/app/services/narrative/write_service.py:6`

原因：后端服务从 `alpha_autopilot` 顶层包导入 `DbHistoryRepository`、`create_history_repository`，但 `alpha_autopilot/__init__.py` 并未导出这些符号。实测 `python -c "from backend.app.main import app"` 会直接抛 `ImportError`。

建议修复：要么在 `alpha_autopilot/__init__.py` 显式导出 `DbHistoryRepository`、`FallbackHistoryRepository`、`create_history_repository`，要么把各服务改成从 `alpha_autopilot.repositories` 直接导入，避免顶层 re-export 漏洞。

2. `/api/history/export` 在默认成功路径上会直接崩溃。

文件：`backend/app/api/routes/history.py:24`，`alpha_autopilot/repositories.py:169-219`

原因：`HistoryService.repository` 默认由 `create_history_repository()` 返回 `FallbackHistoryRepository`，该类型没有 `store` 属性，但路由在导出时直接访问 `service.repository.store.artifacts_dir`。实测 `create_history_repository()` 返回 `FallbackHistoryRepository` 且 `hasattr(repo, "store") == False`。

建议修复：不要从 repository 反查导出路径。应由 `HistoryExportService` 自己持有 `ArtifactStore`，或在路由层直接注入 `ArtifactStore`，并把导出目标统一约束到 `artifacts/exports`。

3. 反馈链路会稳定触发运行时错误，并可能造成部分写入成功的脏状态。

文件：`backend/app/services/narrative/feedback_service.py:61-72`，`alpha_autopilot/repositories.py:110-128`

原因：`persist_value_metric()` 被传入的是裸 `dict`，而仓储层按 `record.action`、`record.score` 等属性访问 `RecommendationMetricRecord`。这会在反馈写 value metrics 时直接抛异常；前面的训练日志写入可能已经发生，形成部分成功、部分失败。

建议修复：在 `feedback_service.py` 中显式构造 `RecommendationMetricRecord` 后再写入，或在 `NarrativeWriteService` 内统一做类型标准化并保证一次请求内的持久化顺序具备事务语义。

4. SQLite 连接的创建方式与当前 FastAPI 路由生命周期冲突，历史/训练/反馈接口存在跨线程直接失败的风险。

文件：`backend/app/api/routes/training.py:8`，`backend/app/api/routes/feedback.py:9`，`backend/app/api/routes/history.py:9-10`，`backend/app/services/narrative/training_service.py:47-49`，`backend/app/services/narrative/feedback_service.py:39-41`，`alpha_autopilot/repositories.py:213-217`

原因：路由模块在 import 时就实例化全局 service，并在 service 初始化时创建 `sqlite3.Connection`。当前路由是同步 `def`，FastAPI 会在线程池执行；默认 SQLite 连接线程绑定，实测跨线程访问会抛 `ProgrammingError: SQLite objects created in a thread can only be used in that same thread`。

建议修复：改成请求级连接或显式依赖注入，不要把裸 `sqlite3.Connection` 挂在模块级单例上。若必须跨线程使用，也需要重新设计连接生命周期和并发控制，而不是只加 `check_same_thread=False`。

## High 风险

1. “SQLite 优先 + 文件回退”没有真正落地，训练/反馈/写服务都直接绑定裸 DB 仓储。

文件：`backend/app/services/narrative/training_service.py:43-45,152-164`，`backend/app/services/narrative/feedback_service.py:35-37,61-72`，`backend/app/services/narrative/write_service.py:24-42`

原因：训练与反馈服务都直接 new `DbHistoryRepository`，`NarrativeWriteService` 也以 `DbHistoryRepository` 为参数类型，只要 SQLite 异常就直接失败。当前所谓 fallback 只存在于 `create_history_repository()` 的读写包装，但训练/反馈主链路并未统一接入它。

建议修复：让训练、反馈、历史、导出全部只依赖 `HistoryRepository` 接口，并通过同一工厂注入；失败策略应收敛到一个地方，不能让不同链路各写各的。

2. 文件回退路径不一致，训练日志写到了两套不同位置。

文件：`alpha_autopilot/training_log.py:22-27,34-45`，`alpha_autopilot/storage.py:16-18`，`alpha_autopilot/repositories.py:38-48`

原因：`TrainingLogger` 写入 `artifacts/training_log.json`，而 `FileHistoryRepository` 读取和回退写入的是 `artifacts/training/training_log.json`。实测两个路径不同。

建议修复：统一以 `ArtifactStore.training_log_path` 为唯一训练日志路径；`TrainingLogger`、`FileHistoryRepository`、导出服务都必须共享同一事实来源。

3. `FallbackHistoryRepository` 的读取优先级会隐藏 file fallback 数据，导致恢复后“看起来成功、实际丢数”。

文件：`alpha_autopilot/repositories.py:174-192`

原因：一旦 DB 中已经存在任意记录，`read_training_logs()` / `read_value_metrics()` 就直接返回 DB 结果，不再合并文件侧 fallback 数据。这样 SQLite 短暂故障期间写入到文件的数据，在 DB 恢复后会被静默隐藏。

建议修复：读取时至少要合并 DB 和 file 两侧数据并去重，或提供明确的补偿回灌机制。当前这种“DB 非空就完全遮蔽 file”的策略不适合作为容灾 fallback。

4. 训练与反馈的时间戳策略会让 SQLite 历史、文件日志和看板排序互相打架。

文件：`backend/app/services/narrative/training_service.py:143-160`，`backend/app/services/narrative/feedback_service.py:44-60`

原因：训练链路把 DB `timestamp` 固定写成 `snapshot.created_at`，同一轮所有训练样本共用一个时间；反馈链路甚至取上一条文件日志时间，没有历史时写空串。与此同时 `TrainingLogger.record()` 又会生成新的当前 UTC 时间写入另一套文件日志。

建议修复：在每次事件开始时只生成一次 UTC 时间戳，并把同一个值传给 DB、文件日志、导出和历史聚合；禁止空时间戳落库。

5. 历史分组逻辑过粗，会把 `notes`、`stage` 和“版本”混为一谈，直接污染 `versionTimeline` / `stageTimeline`。

文件：`backend/app/services/narrative/history_service.py:24-27,52-65,68-100`

原因：当前分组 key 是 `notes or stage or "unknown"`。训练链路把 `notes` 填成版本号还算勉强成立，但反馈链路把 `notes` 填成用户备注或默认文案，最终 `stageTimeline.versions` 会混入备注字符串，`versionTimeline` 也会把备注文本当“版本”展示。

建议修复：把 `version` 从 `notes` 中拆成独立字段，历史表显式持久化 `version_id`、`event_type`、`stage`、`event_id`；不要再用 `notes` 兼做分组主键。

6. 历史时间线是在截断后的日志集上聚合，时间线并不代表真实全量历史。

文件：`backend/app/services/narrative/history_service.py:13-18,102-117`

原因：代码先按筛选条件取 `training_logs[-limit:]`，再基于这批截断数据生成 `versionTimeline` 和 `stageTimeline`。默认 `limit=20` 时，一旦历史超过 20 条，看板时间线就是“最近 20 条的局部视图”，而不是全量版本/阶段演化。

建议修复：先对全量筛选结果做聚合，再分别对日志列表和时间线做独立分页/裁剪。否则看板会把缺失当作不存在。

7. 导出当前既会覆盖旧文件，也缺少归档/迁移必需的元数据。

文件：`backend/app/api/routes/history.py:24`，`backend/app/services/narrative/history_export_service.py:14-22`

原因：导出文件名固定为 `artifacts/exports/history-export.json`，每次都会覆盖上一次结果；导出内容只包含 `training_logs` 与 `value_metrics`，没有 schema version、版本注册表、矩阵快照、导出时间、来源路径、事件主键等元数据，不适合作为长期归档或迁移中转。

建议修复：生成唯一文件名，固定写到 `artifacts/exports` 下；同时补充 `schema_version`、`exported_at`、`registry`、`matrix_snapshots`、`source`、`event_ids` 等字段，保证可回放、可审计、可迁移。

8. 历史看板的筛选重置逻辑有误，搜索和 chips 选中过后无法真正清空过滤条件。

文件：`ui-react/src/App.tsx:174-177`，`ui-react/src/components/HistoryPanel.tsx:43-46,60-75`

原因：父层 `handleHistoryFilter()` 用 `{ ...historyFilter, ...filter }` 合并状态；子层“全部”按钮只传 `{ limit: 20 }`，输入框清空时只传 `{ action: undefined, limit: 20 }`。这不会删除旧的 `stage` / `action`，而是把旧过滤条件保留下来。

建议修复：把 filter 更新改成“替换”而不是“合并”，或显式使用 `null`/空串表示清除条件，并在 `fetchHistory()` 参数构造时正确移除。

9. `handleExport` 硬编码了 `http://127.0.0.1:8000`，与其余 API 客户端不一致。

文件：`ui-react/src/App.tsx:180-185`，`ui-react/src/api.ts:148-209`

原因：其余请求都复用 `DEFAULT_BASE_URL`，只有导出请求在 `App.tsx` 中直接写死地址。部署到非本机、反向代理、端口变化或自定义 `VITE_API_BASE_URL` 时，导出会单独失效。

建议修复：把导出接口也收敛到 `ui-react/src/api.ts`，复用同一 `DEFAULT_BASE_URL` 和统一错误处理。

## Medium 风险

1. `historyLogs` 状态目前没有真实渲染出口，训练/反馈/导出后的前端提示会被写入“死状态”。

文件：`ui-react/src/App.tsx:32,38,61,113,142,164,185`，`ui-react/src/components/HistoryPanel.tsx:20`

原因：`App.tsx` 维护了本地 `historyLogs` 状态并不断追加提示，但 `HistoryPanel` 实际读取的是 `history?.historyLogs`，没有接收这份本地状态。

建议修复：要么删除这套本地状态，统一依赖后端刷新后的 `history.historyLogs`；要么把本地日志显式传给 `HistoryPanel` 并定义合并规则。

2. `README.md` 与当前实现严重脱节，容易误导联调与验收。

文件：`README.md:7-10,25,33-39`，`backend/app/main.py:13-20`

原因：README 仍描述项目是 “database-free”，并引导使用 `uvicorn backend_app:app --reload` 启动 demo API；但真正包含历史/导出路由的入口是 `backend.app.main:app`，而且当前实现已经引入 SQLite。

建议修复：文档应改成当前真实入口，明确 SQLite、history/export 接口和 artifacts 布局；避免评审者按旧文档启动后得到错误结论。

3. `docs/API.md` 缺失，且历史路由没有 `response_model` 约束，前后端契约漂移风险偏高。

文件：`docs/API.md`，`backend/app/api/routes/history.py:13-24`

原因：`/api/history` 与 `/api/history/export` 目前只有前端类型和运行时返回值，没有正式 API 文档，也没有后端响应模型约束。

建议修复：补齐 API 文档，并给历史接口补 `response_model`；同时把导出响应类型移动到 `ui-react/src/api.ts`，避免 App 内联定义。

4. value metrics 记录缺少时间、版本和事件关联键，离线分析和迁移很难做正确关联。

文件：`alpha_autopilot/metrics.py:11-18`，`backend/app/services/narrative/history_export_service.py:16-18`

原因：`RecommendationMetricRecord` 只有 action/score/accepted/quality 等汇总字段，没有 `timestamp`、`version`、`stage`、`event_id`。导出后无法与 training log 做稳定 join，也无法重建某次训练或某轮反馈对应的指标演化。

建议修复：给 metrics 记录补充最少的审计字段，并在导出中保持一一对应关系，保证离线分析和迁移时可追溯。

## Low 风险

1. `NarrativeWriteService` 中的 `ArtifactStore` 与 `TrainingLogger` 当前未被使用，容易制造“看起来有 fallback、实际上没接通”的错觉。

文件：`backend/app/services/narrative/write_service.py:25-26`

原因：写服务实例化了本地存储对象，但真正写入只走 repository。

建议修复：删掉未使用对象，或把文件回退正式接入写服务，避免误导维护者。

2. `ArtifactStore.history_snapshots_path` 当前未被任何链路使用，历史快照概念处于悬空状态。

文件：`alpha_autopilot/storage.py:23-25`

原因：存储层定义了 `history_snapshots.json`，但没有任何写入或读取实现，导出也未包含这份数据。

建议修复：要么补齐真实用途，要么删除无效路径定义，避免让归档范围出现假象。

## 回归风险

1. 修复顶层导出和 service 初始化顺序后，会立刻暴露后续运行时问题，包括 SQLite 跨线程、fallback 读写不一致、导出路径访问错误；这些问题需要成套回归，不能只做点状修补。

2. 如果把历史分组从 `notes` 重构为独立 `version_id`，前端 `HistoryPanel`、历史接口响应、导出格式、离线分析脚本都要同步调整，属于中高回归面改动。

3. 如果统一训练日志路径并接入真正的 file fallback，需要补数据迁移逻辑，否则旧的 `artifacts/training_log.json` 会被新逻辑忽略。

4. 如果把 SQLite 连接改成请求级生命周期，还需要补并发回归，确认训练、反馈、历史查询、导出在连续请求下不会出现锁冲突、重复写入或读到半状态。

## 建议的最小修复顺序

1. 先修顶层导出缺失、service 单例持有 SQLite 连接、反馈 value metric 类型错误，确保后端能启动且核心接口不直接崩。

2. 再统一 `HistoryRepository` 注入方式、训练日志路径、fallback 读写语义，补 SQLite 失败时的端到端回退测试。

3. 然后重构历史模型，拆分 `version_id` / `notes` / `event_id` / `timestamp`，修复 `stageTimeline` 与 `versionTimeline` 聚合。

4. 最后修导出格式、README/API 文档和前端过滤/导出客户端逻辑。

## 最终是否可以继续推进

不通过

当前不建议继续推进新功能。至少需要先补齐以下验收门槛：后端入口可启动；训练、反馈、历史、导出接口可调用；SQLite 故障时文件回退可读可写；`/api/history` 与前端类型和筛选语义一致；导出文件可在 `artifacts` 下稳定生成且适合归档/迁移。
