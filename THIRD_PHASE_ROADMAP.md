# 第三阶段路线图：读者留存目标函数与生成控制层

## 1. 阶段定位

第三阶段属于 `Increment` 层，聚焦的是在不破坏 `v1/v2` 基线稳定性的前提下，为系统追加新的顶层目标函数与生成控制层。

本阶段的核心目标是：

> 让系统不只生成结构正确的小说内容，而是生成更能留住读者继续阅读的内容。

这意味着 `V3` 不是替代 `v1/v2`，而是在其基础上向上追加一层“留存驱动”的控制能力。

范围锚点：

- 第三阶段权威范围以 `PHASE3_SCOPE_ALIGNMENT_2026_04_24.md` 为准。
- 历史表述“推荐价值自适应进化”仅作为背景，不覆盖当前执行范围。

## 2. 当前已完成

### 2.1 `V3` 设计与计划

已完成 `V3` 方向说明与初版需求整理，明确了：

- 读者留存目标函数
- 生成控制层
- 标签重定义
- 留存导向评估与反馈闭环

### 2.2 `V3` 首个代码切片

已完成：

- taxonomy 冻结
- decomposition schema
- heuristic reverse decomposition pipeline
- evidence span / checkpoint / admission 分级
- PlotPilot report -> `reverse_outline_records` 导入转换
- 本地构建脚本

### 2.3 本地测试资产

已完成：

- PlotPilot 样本迁移
- 本地 `.env.local` 复制
- `workbench_contexts.json`
- `reverse_outline_records.jsonl`
- `matrix_projection.json`

## 3. 当前阶段目标

### 3.1 留存目标函数落地

把“留住读者”抽象成显式目标函数，避免系统继续停留在“结构正确但不抓人”的状态。

### 3.2 生成控制层落地

把情绪、节奏、爽点、悬念、冲突、钩子等标签真正接入生成决策，而不是只用于展示或局部分析。

### 3.3 章节上下文正式化

让 `mapped_chapter` 从当前聚合式 context 升级为真实章节上下文来源。

### 3.4 workbench 结果联动

让 `V2 Workbench` 能直接查看：

- reverse outline
- style DNA
- checkpoint 结果
- admission 状态
- 留存目标与生成控制建议

### 3.5 corpus QC

补齐批量层质量控制：

- taxonomy 覆盖
- style drift
- low-confidence concentration
- approved / provisional / rejected distribution
- 留存风险分布

## 4. 阶段任务拆分

### 4.1 任务组 A：目标函数与控制层

- 定义留存目标函数
- 定义生成控制层输入输出
- 定义标签到决策的映射

### 4.2 任务组 B：训练链路接入

- 定义 V3 projection -> 训练输入映射
- 让训练链路区分 approved / provisional / rejected
- 增加训练批次 summary

### 4.3 任务组 C：上下文 API 正式化

- 定义真实章节 context contract
- 提供章节级 state mapping
- 提供章节级 compare baseline

### 4.4 任务组 D：workbench 展示联动

- workbench 接 reverse-outline 结果
- workbench 接 style DNA
- workbench 接 checkpoint / admission
- workbench 接留存建议

### 4.5 任务组 E：Corpus QC

- 批量质量报告
- label drift / style drift 检查
- 低质量样本筛除
- 留存风险检查

## 5. 当前风险

- `V3` 目前仍需进一步实现目标函数与控制层的代码落地
- `matrix_projection` 尚未正式进入训练主循环
- `mapped_chapter` 还不是完整章节 API
- 留存指标需要避免做成单一模板规则，否则会再次生成八股文

## 6. 最近验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `npm test` -> `7 passed`
- `npm run build` -> success

## 7. 下一步优先级

1. 留存目标函数正式接入
2. 生成控制层正式接入
3. `V3` 结果进入 `V2 Workbench`
4. 补真实章节上下文 API
5. 补 corpus-level QC

## 8. 一句话总结

第三阶段不是继续强化“结构化辅助”，而是把“留住读者”变成系统的显式目标函数，并用生成控制层把情绪、节奏、爽点等标签真正变成决策变量。

## 9. 收尾结论（2026-04-24）

- 第三阶段按当前权威范围完成收口：目标函数、控制层、主链路受控接入、分层测试门禁、文档对齐。
- 进入维护窗口后，`V3` 不再接收范围外需求，仅处理缺陷修复与稳定性增强。
- 阶段剩余项转后续增量：真实章节上下文 API、更深层反馈回写、跨题材扩展验证。
- 收尾细项与测试证据见 `V3_PHASE_CLOSEOUT_2026_04_24.md`。
