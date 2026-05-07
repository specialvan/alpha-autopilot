# alpha-autopilot 接口文档

更新时间：2026-05-08

## 目的

本目录不是“大而全”的模块百科，而是给 DeepWiki、后续维护者、前后端协作者使用的契约锚点。文档优先固定以下四类内容，再解释实现细节：

1. 关键接口清单：入口、出入口、异步回调、Webhook、内部 RPC/HTTP、定时任务入口。
2. 数据契约：请求/响应字段、枚举值、状态流转、必填项、默认值。
3. 关键流程：从触发到完成的完整链路，标出成功/失败分支。
4. 依赖说明：数据库、文件存储、队列、第三方服务、配置项。

## 阅读顺序

1. [CONVENTIONS.md](./CONVENTIONS.md)
2. [02-core-data-contracts.md](./02-core-data-contracts.md)
3. [10-http-api-contract.md](./10-http-api-contract.md)
4. [20-workbench-and-recommendation-flows.md](./20-workbench-and-recommendation-flows.md)
5. [50-external-dependencies-and-config.md](./50-external-dependencies-and-config.md)

## 当前范围

当前这一版先覆盖主链契约：

- Baseline 推荐、训练、反馈、历史导出
- V2 Workbench 上下文与推荐预览
- V4 预览、可观测性、告警路由
- V6 Simulation、GraphRAG、事件注入
- V7 决策预览、benchmark、治理主链
- V8 内部控制态与 Workbench 嵌入预览

## 治理边界

- `alpha_autopilot/` 与 `alpha_autopilot_v2/` 属于 Baseline 主链，文档需要稳定收口。
- `alpha_autopilot_v3/` 及以后是 Increment/实验增强层，文档应强调“如何被主链调用”，不要先按算法细节平铺。
- `backend/app/main.py` 是当前主服务入口；`backend_app.py` 仅保留为 demo-only 入口，不能与主入口混写。

## 当前已确认的系统边界

- 入站协议以 HTTP API 为主，统一由 FastAPI 暴露。
- 当前未发现入站 Webhook。
- 当前未发现消息队列或 broker 依赖。
- 当前未发现仓库内建 scheduler/cron worker。
- 当前真实外部 HTTP 调用只有两类：
  - `backend/app/services/narrative_v2/online_report_contexts.py` 拉取 PlotPilot 在线报告。
  - `backend/app/services/narrative_v4/alert_channel.py` 发送 V4 critical alert 出站 Webhook。

## 后续建议补充

以下文档建议在本目录继续新增：

- `30-alerts-events-and-postmortem-objects.md`
- `40-state-machines-and-task-lifecycles.md`
- `60-tests-and-contract-verification.md`

## 当前待确认

- `demo.py` 仍引用 `TrainingExample`，当前仓库内未找到该类型定义，疑似过期脚本。
- V7 长链路 `auto-remediate` 家族接口数量极多；本目录当前只固定主治理链，长尾接口建议单独分册。
