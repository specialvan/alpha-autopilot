# Claude 评审结论核验（Codex）

核验对象：

- `claude_review_package/ULTRAREVIEW_REPORT.md`
- `claude_review_package/ULTRAREVIEW_REVIEW_SHARP.md`
- `CLAUDE_REVIEW_REPORT.md`

判定标签：

- `保留`：当前代码仍存在该问题或风险
- `部分保留`：方向成立，但描述已部分过时
- `打回`：当前代码已修复，或结论与现状不符

---

## A. `CLAUDE_REVIEW_REPORT.md`（2026-04-21）核验

| 条目 | Claude 原结论 | Codex 判定 | 证据 |
|---|---|---|---|
| B1 | 后端入口因 `alpha_autopilot/__init__.py` 未导出仓储符号而无法启动 | 打回 | `alpha_autopilot/__init__.py:6-12,18-40` 已导出；`from backend.app.main import app` 可导入 |
| B2 | `/api/history/export` 因 `repository.store` 访问崩溃 | 打回 | `backend/app/api/routes/history.py:20-22` 改为 `HistoryExportService().export_json()` |
| B3 | feedback 向 metrics 写入 dict 导致属性访问错误 | 打回 | `backend/app/services/narrative/feedback_service.py:74-84` 显式构造 `RecommendationMetricRecord` |
| B4 | training/feedback/history 路由全局 service + SQLite 跨线程风险 | 打回 | 路由改为请求级实例：`training.py:10-12`, `feedback.py:18-27`, `history.py:11-22` |
| H1 | 训练/反馈链路未接统一 `HistoryRepository` fallback | 打回 | `training_service.py:46-54`, `feedback_service.py:38-44`, `write_service.py:24-44` 均走 `HistoryRepository` |
| H2 | 训练日志路径双写不一致 | 打回 | `ArtifactStore.training_log_path` 与 `TrainingLogger.log_path` 统一为 `artifacts/training/training_log.json` |
| H3 | fallback 读取会遮蔽文件侧数据 | 打回 | `FallbackHistoryRepository.read_*` 已 merge DB+file 并去重：`repositories.py:183-242` |
| H4 | 训练/反馈时间戳在 DB 与文件链路打架 | 打回 | `training_service.py:166-187`、`feedback_service.py:47-73` 同一 payload 时间戳同时写 logger+repo |
| H5 | 历史分组把 notes/stage/version 混用污染时间线 | 打回 | `history_service.py:12-17` 用 `version` 字段构造分组 key |
| H6 | 时间线基于截断数据聚合，不代表全量历史 | 保留 | `history_service.py:24` 截断发生在聚合前 |
| H7 | 导出覆盖旧文件且缺元数据 | 部分保留 | 覆盖已修：`history_export_service.py:18-20` 唯一文件名；元数据仍简化：`22-25` |
| H8 | 历史筛选 reset 无法清空条件 | 打回 | `App.tsx:183-187` 改替换更新；`HistoryPanel.tsx:48-51` reset 显式置空 |
| H9 | 导出 URL 硬编码 `127.0.0.1:8000` | 打回 | `ui-react/src/api.ts:300,387-395` 统一 `DEFAULT_BASE_URL` |
| M1 | `historyLogs` 本地状态写入后无渲染出口 | 保留 | `App.tsx:34,47,70,122,151,173,192` 维护；`HistoryPanel` 实际读取 `history?.historyLogs` |
| M2 | README 与真实入口脱节 | 保留 | `README.md:44` 仍指向 `backend_app:app`，主后端在 `backend/app/main.py` |
| M3 | history 路由缺正式 API 文档与 response model | 保留 | `docs/API.md` 缺失；`history.py` 无 `response_model` |
| M4 | value metrics 缺时间/version/event 关联键 | 保留 | `alpha_autopilot/metrics.py:11-18` 字段仍不足 |
| L1 | write_service 未使用 ArtifactStore/TrainingLogger | 打回 | 现实现已移除无效成员，`write_service.py` 仅持 repository |
| L2 | `ArtifactStore.history_snapshots_path` 悬空未使用 | 保留 | `storage.py:23-25` 仍无读写链路使用 |

---

## B. `ULTRAREVIEW_REPORT.md` 核验

| 条目 | Claude 原结论 | Codex 判定 | 证据 |
|---|---|---|---|
| U1 | `matrix_projection` 尚未接入主训练链路 | 打回 | `training_service.py:18-22,144-157,205-206` 已接入并回传统计 |
| U2 | `reverse-outline/style DNA/checkpoint` 未接入 v2 workbench | 打回 | `imported_contexts.py:202-227` enrichment；`ContextRail.tsx:85-118` 展示 |
| U3 | 缺统一 QC 报告机制 | 打回 | `alpha_autopilot_v3/decomposition/qc.py` + build 脚本写 `qc_report.json` |
| U4 | 质量层与主链路仍双系统 | 部分保留 | 已有训练/workbench接入，但尚未覆盖完整推荐评估闭环 |
| U5 | 数据接入偏夹具化，真实章节源不足 | 部分保留 | v2 已从后端 contexts 拉取；但仍依赖 `artifacts/testing/plotpilot` |

---

## C. `ULTRAREVIEW_REVIEW_SHARP.md` 核验

| 条目 | Claude 原结论 | Codex 判定 | 证据 |
|---|---|---|---|
| S1 | v3 是旁路实验，未进入统一决策对象 | 打回 | `preview_service.py:42-58` + `decision_contract.py:9-37` 已输出标准 decision |
| S2 | `mapped_chapter` 未真正走后端上下文 | 打回 | `useV2WorkbenchController.ts:88-97` 拉后端；`contextMapping.ts:17-20` 优先后端 contexts |
| S3 | 测试分层建议（核心/质量/API/导入/前端） | 部分保留 | 已落 `scripts/run_layered_tests.py`，但仍可继续细化治理 |

---

## 需要“打回去”的不合理阻断点（可直接回退 Claude 结论）

以下结论与当前代码事实冲突，不应继续作为阻断项：

1. “`matrix_projection` 未接训练链路”
2. “v2 workbench 未接 reverse-outline/style/checkpoint”
3. “无标准 decision 对象”
4. “导出 URL 仍硬编码”
5. “历史筛选 reset 仍失效”
6. “后端主入口 import 仍崩溃”

这些项应从阻断清单中移除，避免评审噪声。

