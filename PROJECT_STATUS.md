# 项目进度表

## 当前阶段

- 项目名称：小说章节智能推荐引擎原型
- 目标目录：`D:\workspace\alpha-autopilot`
- 治理结构：Baseline = `v1/v2`，Increment = `v3`，Experimental = 隔离探索
- 当前状态：`v2` 推荐工作台已独立落地，`V3` 逆向拆解质量层已完成首个可执行切片

## 进度清单

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 叙事状态模型 | 已完成 | 已具备 `StoryState`、`CharacterState`、规则/搜索/评估基础抽象 |
| 特征矩阵原型 | 已完成 | 已具备训练、版本、日志、历史聚合基础 |
| `v2` 核心域 | 已完成 | `alpha_autopilot_v2` 已具备 rule / search / evaluation / validation |
| `v2` API | 已完成 | 已提供 `/api/v2/recommendation/preview` 与 `/api/v2/workbench/contexts` |
| `v2` 前端工作台 | 已完成 | 已从嵌入式实验面板升级为独立 `V2 Workbench` 路由 |
| PlotPilot 测试资产迁移 | 已完成 | 已迁入本地 `.env.local` 与测试样本，生成 workbench contexts |
| `V3` taxonomy / schema | 能力完成 | 已冻结章节功能、style DNA、checkpoint 基础契约 |
| `V3` heuristic decomposition pipeline | 能力完成 | 已支持章节拆解、evidence span、checkpoint、admission 分级 |
| `V3` PlotPilot report import | 能力完成 | 已支持从 PlotPilot report 转换为 `reverse_outline_records` |
| `V3` 本地构建脚本 | 能力完成 | 已支持生成 `reverse_outline_records.jsonl` 与 `matrix_projection.json` |

## 当前已知风险

- `mapped_chapter` 目前优先使用后端聚合上下文与导入夹具，还不是完整真实章节 API
- `V3` 拆解 pipeline 目前是启发式版本，适合作为质量层原型，不代表最终生产判定质量
- `V3` matrix projection 已可导出，但尚未正式接入现有训练主链路
- 前端 dashboard 与 workbench 已分离，但 dashboard 仍保留较多原型式展示面板
- 目前状态表中的“能力完成”不等于“主链路接入完成”

## 最新验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `npm test` -> `5 files passed / 7 tests passed`
- `npm run build` -> 成功

## 下一步计划

1. 把 `V3` 的 `matrix_projection.json` 接入现有训练链路
2. 用真实章节上下文替换当前聚合式 `mapped_chapter` 来源
3. 把 `V3` 的 reverse-outline / style DNA / checkpoint 结果接入 `V2 Workbench`
4. 增加 `V3` corpus-level QC 与 admission batch report
