# 外部依赖与配置项

更新时间：2026-05-08

## 说明

本页只解释“哪些接口依赖数据库、文件、第三方服务、配置项”，方便 DeepWiki 不把纯算法模块误读成独立服务。

## 1. 第三方服务依赖

### 1.1 PlotPilot 在线报告 API

- 相关文件：
  - `backend/app/services/narrative_v2/workbench_service.py`
  - `backend/app/services/narrative_v2/online_report_contexts.py`
- 用途：
  - 为 V2 Workbench 提供在线 contexts 来源。
- 调用方式：
  - `GET`
  - `Authorization: Bearer <api_key>` 可选
  - 请求 URL 会按 `preferred_model` 追加 `model` 查询参数
- 主要配置：
  - `plotpilot_report_api_url`
  - `plotpilot_report_api_key`
  - `benchmark_api_key`：作为在线报告 key 的后备来源
  - `plotpilot_report_api_timeout_seconds`
  - `plotpilot_report_api_max_attempts`
  - `plotpilot_report_api_backoff_seconds`
- 失败兜底：
  - timeout / network / 5xx / 429 可重试
  - 失败后退回本地 report、fixture 或 live fallback

### 1.2 V4 出站告警 Webhook

- 相关文件：
  - `backend/app/services/narrative_v4/alert_channel.py`
- 用途：
  - 将 critical alert 投递到 IM 或 Webhook 终点。
- 调用方式：
  - `POST`
  - `Content-Type: application/json`
- 主要配置：
  - `v4_alert_remote_enabled`
  - `v4_alert_im_webhook_url`
  - `v4_alert_webhook_url`
  - `v4_alert_webhook_timeout_seconds`
  - `v4_alert_oncall_contacts`
- 失败兜底：
  - 无远端目标：仅本地留痕
  - 缺少 oncall 联系人：阻断远端投递
  - HTTP 失败：状态降级为 `degraded-local-only`

## 2. 本地持久化依赖

### 2.1 基础 artifacts 目录

- 定义文件：`alpha_autopilot/storage.py`
- 根目录：
  - `artifacts/`

### 2.2 Baseline 训练 / 历史

| 路径 | 用途 | 相关模块 |
| --- | --- | --- |
| `artifacts/training/training_log.json` | 训练日志 | `alpha_autopilot/training_log.py` |
| `artifacts/metrics/recommendation_value_metrics.json` | 推荐价值指标 | `alpha_autopilot/trainer.py`、feedback |
| `artifacts/history/history_snapshots.json` | 历史快照 | history service |
| `artifacts/db/history.sqlite3` | SQLite 历史仓储 | `alpha_autopilot/repositories.py` |
| `artifacts/registry.json` | 版本注册表 | `alpha_autopilot/versioning.py` |
| `artifacts/matrix_v*.json` | 矩阵快照 | `alpha_autopilot/versioning.py` |

### 2.3 V2 Workbench

| 路径 | 用途 | 相关模块 |
| --- | --- | --- |
| `artifacts/testing/plotpilot/workbench_contexts.json` | 导入的 Workbench fixture | `workbench_service.py` |
| `artifacts/testing/plotpilot/raw/model_switch_tests/*` | 本地 raw reports | `imported_contexts.py` |
| `artifacts/testing/plotpilot/raw/decomposition/*` | manifest / report 仲裁输入 | `report_arbitration.py` |
| `artifacts/testing/plotpilot/v3_records/*` | quality enrichment 数据 | `imported_contexts.py` |

### 2.4 V4 关系图与告警

| 路径 | 用途 | 相关模块 |
| --- | --- | --- |
| `artifacts/history/v4_*.jsonl` | V4 memory / feedback / runtime 记录 | `memory_store.py` |
| `artifacts/history/v4_observability_alerts.jsonl` | V4 告警 sink | `alert_channel.py` |
| `artifacts/history/v4_observability_alerts.state.json` | 告警冷却状态 | `alert_channel.py` |

### 2.5 V6 Simulation / GraphRAG

| 路径 | 用途 | 相关模块 |
| --- | --- | --- |
| `artifacts/history/v6_simulation_results.jsonl` | simulation 主存储 | `state_store.py` |
| `artifacts/history/v6_simulation_archive/` | simulation 轮转归档 | `state_store.py` |
| `artifacts/history/v6_graph_memory.jsonl` | GraphRAG 命中历史 | `graph_memory_store.py` |
| `artifacts/history/v6_graph_memory_audit.jsonl` | graph memory 审计历史 | `graph_memory_store.py` |
| `artifacts/history/v6_runtime_metrics.jsonl` | V6 runtime 指标 | `observability.py` |

### 2.6 V7 benchmark 与治理

| 路径 | 用途 | 相关模块 |
| --- | --- | --- |
| `artifacts/history/v7_benchmark_store.jsonl` | benchmark 主存储 | `benchmark_store.py` |
| `artifacts/history/v7_benchmark_store_versions/` | benchmark 版本快照目录 | `benchmark_store.py` |
| `artifacts/history/v7_*.jsonl` | alert / governance / escalation / remediation 等记录 | `benchmark_store.py` |

### 说明

- `[推断]` V7 治理家族文件数量很多，但都是“事件式 JSONL 对象”而不是消息队列。

## 3. 配置项索引

### 3.1 通用应用配置

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `app_name` | `alpha-autopilot api` | 应用名 |
| `app_version` | `0.1.0` | 版本 |
| `api_prefix` | `/api` | API 前缀 |
| `benchmark_base_url` | `None` | 待确认：预留 benchmark 服务地址 |
| `benchmark_model` | `None` | Workbench 偏好模型 |
| `benchmark_api_key` | `None` | 在线报告 API key 后备来源 |

### 3.2 V2 在线报告

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `plotpilot_report_api_url` | `None` | PlotPilot 在线报告地址 |
| `plotpilot_report_api_key` | `None` | PlotPilot API key |
| `plotpilot_report_api_timeout_seconds` | `8.0` | 超时 |
| `plotpilot_report_api_max_attempts` | `3` | 最大重试次数 |
| `plotpilot_report_api_backoff_seconds` | `0.2` | 重试退避基数 |

### 3.3 V4 预览、告警、压缩

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `v4_genre_auto_min_samples` | `4` | genre auto learning 最小样本数 |
| `v4_genre_auto_decay` | `0.9` | genre auto learning 衰减 |
| `v4_genre_auto_bias_limit` | `0.12` | 偏差上限 |
| `v4_genre_auto_max_volatility` | `0.58` | 波动阈值 |
| `v4_genre_auto_max_signal_divergence` | `0.32` | 信号分歧阈值 |
| `v4_genre_guard_overrides_json` | `None` | 守卫覆盖配置 |
| `v4_observability_latency_p95_ms_threshold` | `900.0` | 观测告警阈值 |
| `v4_observability_error_rate_threshold` | `0.08` | 错误率阈值 |
| `v4_observability_fallback_rate_threshold` | `0.35` | fallback 率阈值 |
| `v4_alert_remote_enabled` | `False` | 是否允许远端告警 |
| `v4_alert_im_webhook_url` | `None` | IM webhook |
| `v4_alert_webhook_url` | `None` | 通用 webhook |
| `v4_alert_oncall_contacts` | `None` | oncall 联系人 |
| `v4_prompt_compress_enabled` | `True` | prompt 压缩开关 |
| `v4_prompt_compress_threshold_tokens` | `2000` | 压缩阈值 |
| `v4_prompt_compress_target_ratio` | `0.3` | 目标压缩比 |
| `v4_prompt_compress_default_mode` | `bullet` | 默认压缩模式 |
| `v4_character_validation_mode` | `heuristic` | 角色校验模式 |

### 3.4 V6 Simulation / GraphRAG

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `v6_enabled` | `True` | V6 全局开关 |
| `v6_simulation_store_max_rows_per_file` | `500` | simulation 文件轮转阈值 |
| `v6_simulation_store_max_bytes_per_file` | `2000000` | simulation 文件大小阈值 |
| `v6_observability_latency_p95_ms_threshold` | `1200.0` | 观测阈值 |
| `v6_observability_error_rate_threshold` | `0.1` | 错误率阈值 |
| `v6_observability_fallback_rate_threshold` | `0.4` | fallback 率阈值 |
| `v6_graph_memory_max_in_memory_rows` | `5000` | 内存缓存上限 |
| `v6_graph_memory_max_age_hours` | `168` | 历史过期小时数 |
| `v6_graph_memory_chapter_window` | `20` | chapter 检索窗口 |
| `v6_graph_memory_min_token_overlap` | `0.2` | token overlap 阈值 |
| `v6_graph_memory_compaction_max_rows` | `5000` | compaction 上限 |
| `v6_graph_memory_audit_max_rows` | `500` | audit 历史上限 |
| `v6_graph_memory_source_weights_json` | `None` | source route 权重覆盖 |

### 3.5 V7 决策与治理

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `v7_enabled` | `True` | V7 全局开关 |
| `v7_opening_gate_enabled` | `True` | opening gate 开关 |
| `v7_antipattern_guard_enabled` | `True` | 反模式守卫开关 |
| `v7_deadlock_router_enabled` | `True` | deadlock router 开关 |
| `v7_sampler_timeout_ms` | `3000` | sampler 超时 |
| `v7_llm_judge_max_tokens` | `512` | 判定器 token 限额 |

### 3.6 V8 Workbench

| 配置项 | 默认值 | 用途 |
| --- | --- | --- |
| `v8_workbench_enabled` | `True` | 是否在 Workbench 返回 V8 preview |

### 3.7 V7 环境变量家族

V7 benchmark governance 还大量依赖 `AA_V7_*` 环境变量，这些变量主要由 `benchmark_store.py` 直接读取，用于控制：

- benchmark 维护 SLA
- alert archive trigger / keep_last / ttl
- governance run prune trigger
- escalation emit cooldown
- stale threshold
- max retry attempts
- escalation failure streak

这一组建议后续单独整理成配置附录，不建议散写在 DeepWiki 模块说明里。

## 4. 当前未发现的依赖

- 未发现消息队列客户端或 broker 依赖。
- 未发现 Celery、RQ、APScheduler、cron worker 等内建调度框架。
- 未发现入站 Webhook。

## 5. 每条主链的依赖边界

| 链路 | 主要依赖 | 说明 |
| --- | --- | --- |
| Baseline preview | `FeatureMatrix`、`base_state()` | 纯本地计算，无外部 HTTP |
| Training | 默认样本、projection 文件、versioning | 离线写盘链 |
| Feedback | training log、value metrics | 本地持久化闭环 |
| V2 Workbench | PlotPilot API、本地 report、fixture、V4/V8 preview | 多级回退最复杂 |
| V4 alert routing | V4 snapshot、本地 JSONL、远端 webhook | 仅出站 HTTP |
| V6 simulation | GraphRAG、graph memory、simulation store | 以 JSONL 为主，无 MQ |
| V7 governance | benchmark store、version snapshots、alert/governance JSONL | 事件式治理对象，不是任务队列 |

## 6. 待确认

- `benchmark_base_url` 当前在配置中存在，但主链中未发现稳定使用点，需确认是否为预留字段。
- V7 `AA_V7_*` 环境变量家族数量较多，建议后续导出一份完整索引。
