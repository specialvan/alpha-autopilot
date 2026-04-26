# 项目进度表

## 当前阶段

- 项目名称：小说章节智能推荐引擎原型
- 目标目录：`D:\workspace\alpha-autopilot`
- 当前状态：`v2` 推荐工作台已独立落地，`V3` 已建立读者留存目标函数与生成控制层，`V4` 已进入可测原型开发

## 进度清单

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 叙事状态模型 | 已完成 | 已具备 `StoryState`、`CharacterState`、规则/搜索/评估基础抽象 |
| 特征矩阵原型 | 已完成 | 已具备训练、版本、日志、历史聚合基础 |
| `v2` 核心域 | 已完成 | `alpha_autopilot_v2` 已具备 rule / search / evaluation / validation |
| `v2` API | 已完成 | 已提供 `/api/v2/recommendation/preview` 与 `/api/v2/workbench/contexts` |
| `v2` 前端工作台 | 已完成 | 已从嵌入式实验面板升级为独立 `V2 Workbench` 路由 |
| PlotPilot 测试资产迁移 | 已完成 | 已迁入本地 `.env.local` 与测试样本，生成 workbench contexts |
| `V3` taxonomy / schema | 已完成 | 已冻结章节功能、style DNA、checkpoint 基础契约 |
| `V3` heuristic decomposition pipeline | 已完成 | 已支持章节拆解、evidence span、checkpoint、admission 分级 |
| `V3` PlotPilot report import | 已完成 | 已支持从 PlotPilot report 转换为 `reverse_outline_records` |
| `V3` 本地构建脚本 | 已完成 | 已支持生成 `reverse_outline_records.jsonl` 与 `matrix_projection.json` |
| `V3` 留存目标函数 | 进行中 | 正在把“留住读者”抽象成顶层目标函数 |
| `V3` 生成控制层 | 进行中 | 正在把情绪、节奏、爽点等标签转成生成决策变量 |
| `V4` 人物关系驱动剧情 | 进行中 | 已落地关系分析与张力评分原型 |
| `V4` 人物性格驱动选择 | 进行中 | 已落地性格偏好分析、压力响应原型与题材校准接口 |
| `V4` 外部压力驱动爆发 | 进行中 | 已落地压力源建模与强度指数原型 |
| `V4` API 与桥接契约 | 进行中 | 已提供 `/api/v4/plot/preview`、`/api/v4/workbench/preview` 与 `v4_enabled` 回滚开关 |
| `V4` 跨章节关系位移跟踪 | 进行中 | 已支持 `relationship_history` 驱动 displacement events 与 graph summary |
| `V4` 留存反馈动态回写 | 进行中 | 已支持 `v3_feedback_history` 驱动 retention 权重自适应 |
| `V4` live 历史反馈注入 | 进行中 | `V2` live workbench context 已自动从 history snapshots 注入反馈样本 |
| `V4` 跨会话记忆存储 | 进行中 | 已落地 `v4_relationship_memory.jsonl` / `v4_feedback_memory.jsonl` 持久化回读 |
| `mapped_chapter` 真实章节上下文 contract | 进行中 | `/api/v2/workbench/contexts` 已优先读取 PlotPilot raw `report.json`，输出 `real_chapter_context_v1` 与章节级 `compare_baseline` |
| `v2` workbench contexts API 显式契约 | 已完成 | 路由已声明 `response_model`，OpenAPI 可见 `NarrativeV2WorkbenchContextsResponsePayload` |

## 当前已知风险

- `mapped_chapter` 已从聚合式来源升级为本地 raw report 驱动 contract，但尚未接入线上真实章节服务 API
- `V3` 的留存目标函数如果实现成单一模板规则，可能重新导向八股文
- `V4` 如果直接落成固定桥段库，会失去“剧情自然长出来”的核心价值
- `matrix_projection` 已可导出，但尚未正式接入现有训练主链路
- 前端 dashboard 与 workbench 已分离，但 dashboard 仍保留较多原型式展示面板
- V4 记忆衰减/去噪、题材自动学习守护回退、可观测趋势与告警已落地首版，并已支持按题材分桶阈值配置与本地告警通道

## 最新验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q` -> `26 passed`
- `python scripts/run_layered_tests.py v4` -> 通过
- `python scripts/run_layered_tests.py quality api import` -> 通过
- `python scripts/run_layered_tests.py frontend import v4` -> 通过
- `pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py tests/test_narrative_v2_workbench_quality_enrichment.py tests/test_narrative_v2_workbench_context_api.py -q` -> `25 passed`
- `pytest tests/test_narrative_v2_workbench_context_api.py tests/test_narrative_v2_imported_contexts.py tests/test_narrative_v2_workbench_quality_enrichment.py -q` -> `16 passed`
- `python scripts/run_layered_tests.py api import frontend` -> 通过
- `python scripts/run_layered_tests.py api import v4 frontend` -> 通过
- `python scripts/run_layered_tests.py` -> 通过（core/quality/api/frontend/import/v4 全层）
- `python scripts/run_claude_acceptance_review.py` -> 通过（产出 `artifacts/acceptance/claude-acceptance-20260426T065834Z.md`）
- `npm test` -> `16 passed`（layered frontend）
- `npm run build` -> 成功

## 下一步计划

1. 把 `V3` 留存目标函数正式接入代码层
2. 把 `V3` 生成控制层接入现有生成/推荐链路
3. 把 `V4` 的人物关系 / 性格 / 压力模型继续细化为可配置模块接口
4. 将当前本地 report 驱动的真实章节 contract 扩展为线上真实章节服务 API（替换文件源）
5. 为 V4 题材自动学习守护策略补线上配置项（阈值可调、灰度开关）
6. 将 V4 本地告警通道扩展到远端通知（IM/Webhook）并补最小值班手册
