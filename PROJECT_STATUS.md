# 项目进度表

## 当前阶段

- 项目名称：小说章节智能推荐引擎原型
- 目标目录：`D:\workspace\alpha-autopilot`
- 当前状态：`v2` 推荐工作台已独立落地，`V3` 已建立读者留存目标函数与生成控制层，`V4` 已进入人物关系与性格驱动剧情生成规划

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
| `V4` 人物关系驱动剧情 | 规划中 | 正在补剧情自然长出来的关系抽象 |
| `V4` 人物性格驱动选择 | 规划中 | 正在补压力下事件选择的性格抽象 |
| `V4` 外部压力驱动爆发 | 规划中 | 正在补断粮、威胁、羞辱、限时等压力模型 |

## 当前已知风险

- `mapped_chapter` 目前优先使用后端聚合上下文与导入夹具，还不是完整真实章节 API
- `V3` 的留存目标函数如果实现成单一模板规则，可能重新导向八股文
- `V4` 如果直接落成固定桥段库，会失去“剧情自然长出来”的核心价值
- `matrix_projection` 已可导出，但尚未正式接入现有训练主链路
- 前端 dashboard 与 workbench 已分离，但 dashboard 仍保留较多原型式展示面板

## 最新验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `npm test` -> `7 passed`
- `npm run build` -> 成功

## 下一步计划

1. 把 `V3` 留存目标函数正式接入代码层
2. 把 `V3` 生成控制层接入现有生成/推荐链路
3. 把 `V4` 的人物关系 / 性格 / 压力模型继续细化为代码模块接口
4. 用真实章节上下文替换当前聚合式 `mapped_chapter` 来源
5. 把 `V3` 的留存指标结果接入 `V2 Workbench`
6. 增加 `V3` / `V4` corpus-level QC 与留存反馈闭环