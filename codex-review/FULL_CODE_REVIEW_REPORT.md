# alpha-autopilot 全量 Code Review（Codex）

评审时间：2026-04-24  
评审对象：`D:\workspace\alpha-autopilot`  
评审方法：代码静态审读 + 关键路径复现实验 + 全量测试/构建校验 + Claude 历史评审逐条核验

## 总体结论

结论：**不建议当前状态直接合入主线**。  
理由：存在 `P1` 级问题 3 项，均可复现，会导致接口稳定性或交付口径偏差。

## 关键发现（按严重级别）

### P1-1 可选质量工件损坏会直接打崩 workbench contexts 接口

- 位置：
  - `backend/app/services/narrative_v2/imported_contexts.py:64`
  - `backend/app/services/narrative_v2/imported_contexts.py:79`
  - `backend/app/services/narrative_v2/imported_contexts.py:123-129`
- 问题：
  - `json.loads(...)` 对 `v3_records/*.json*` 无异常兜底。
  - 任何一行坏 JSON 都会抛 `JSONDecodeError`，导致 `list_contexts()` 失败。
- 复现证据：
  - 见 `REVIEW_EVIDENCE.md`，已复现输出 `JSONDecodeError`。
- 风险：
  - `v3` 质量增强本应是可选增强层，当前变成 fail-closed。
- 建议修复：
  - 在 `_load_quality_records_from_json/_jsonl` 层做逐文件/逐行容错，坏记录跳过并记录告警。

### P1-2 v2 workbench service 使用共享默认实例，存在隐藏的全局状态耦合

- 位置：
  - `backend/app/services/narrative_v2/workbench_service.py:14`
  - `backend/app/api/routes/workbench_v2.py:8`
- 问题：
  - `history_service: HistoryService = HistoryService()` 使用类定义期实例，所有 `NarrativeV2WorkbenchService()` 共享同一对象。
  - 路由层又持有模块级 `service` 单例，进一步固化共享状态。
- 复现证据：
  - 见 `REVIEW_EVIDENCE.md`，`id(s1.history_service) == id(s2.history_service)` 输出 `True`。
- 风险：
  - 共享连接/状态让并发与生命周期边界不清晰，后续排错成本高。
- 建议修复：
  - 改为 `field(default_factory=HistoryService)`。
  - 路由层改请求级构建 service（与 training/feedback/history 路由一致）。

### P1-3 README 启动入口与主后端不一致，易导致“跑错系统”的评审误判

- 位置：
  - `README.md:44`
  - `backend_app.py`（仅 demo 路由）
  - `backend/app/main.py:17-23`（主路由聚合）
- 问题：
  - README 指导 `uvicorn backend_app:app --reload`。
  - 该入口不包含 `/api/history`、`/api/v2/workbench/contexts` 等主链路接口。
- 复现证据：
  - 见 `REVIEW_EVIDENCE.md`：`backend_app` 对上述路径均为 `False`，`backend.app.main` 为 `True`。
- 风险：
  - 评审、联调、回归会在错误入口上进行，形成“假失败”或“假通过”。
- 建议修复：
  - README 主入口改为 `uvicorn backend.app.main:app --reload`。
  - 明确 `backend_app.py` 仅 demo，用途与主 API 严格区分。

### P2-1 历史时间线基于截断样本聚合，语义容易被误读为全量演化

- 位置：
  - `backend/app/services/narrative/history_service.py:24`
  - `backend/app/services/narrative/history_service.py:30-106`
- 问题：
  - 先 `training_logs = training_logs[-limit:]`，再做 `versionTimeline`/`stageTimeline` 聚合。
- 风险：
  - UI/评审若按“全量时间线”理解，会得出偏差结论。
- 建议修复：
  - 聚合使用全量过滤结果，日志列表再单独按 `limit` 截断；或在响应中显式标注“windowed timeline”。

### P2-2 evaluation ledger 读取对坏行无容错，后续审计链路存在脆弱点

- 位置：
  - `alpha_autopilot_v2/validation/ledger.py:32-33`
- 问题：
  - `json.loads(line)` 无异常处理，单行坏数据导致整次读取失败。
- 复现证据：
  - 见 `REVIEW_EVIDENCE.md`，已复现 `JSONDecodeError`。
- 建议修复：
  - 坏行跳过 + 计数告警 + 保留可读部分。

### P3-1 文档与契约治理仍有残缺点

- 位置：
  - `README.md`（database-free 描述与当前 SQLite 事实不一致）
  - `docs/API.md`（缺失）
  - `backend/app/api/routes/history.py`（无 `response_model`）
- 风险：
  - 长期会造成“代码真相”和“文档口径”持续漂移。
- 建议修复：
  - 补齐 API 文档，历史路由补响应模型，更新 README 的真实架构描述。

## 测试与构建状态（本轮）

- `pytest tests -q`：`33 passed`
- `python scripts/run_layered_tests.py core quality api import frontend`：各层全部通过
- `ui-react npm test`：`5 files / 10 tests passed`
- `ui-react npm run build`：通过
- `ruff check`：存在 4 个 `F401`（未使用导入），非阻断但建议清理

## 是否可继续推进新功能

建议：**先修复 P1，再推进新需求**。  
在 P1 关闭前，不建议将当前版本作为“主线稳定候选”。

