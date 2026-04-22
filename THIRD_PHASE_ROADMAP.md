# 第三阶段路线图：逆向拆解质量层与推荐价值进化

## 1. 阶段定位

第三阶段聚焦两件事：

1. 建立 `V3 Reverse Decomposition Quality Layer`
2. 把高质量拆解数据正式接入推荐价值与训练链路

目标不再只是“系统能推荐”，而是让系统能基于高质量章节拆解记录稳定学习、稳定解释、稳定演化。

## 2. 当前已完成

### 2.1 `V3` 设计与计划

- 已完成 `V3 Reverse Decomposition Quality Layer` 设计文档
- 已完成 `V3` 可执行 implementation plan

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

### 3.1 质量层正式入链

把 `matrix_projection.json` 与 admission 结果接入现有训练主链路。

### 3.2 章节上下文正式化

让 `mapped_chapter` 从当前聚合式 context 升级为真实章节上下文来源。

### 3.3 workbench 结果联动

让 `V2 Workbench` 能直接查看：

- reverse outline
- style DNA
- checkpoint 结果
- admission 状态

### 3.4 corpus QC

补齐批量层质量控制：

- taxonomy 覆盖
- style drift
- low-confidence concentration
- approved / provisional / rejected distribution

## 4. 阶段任务拆分

### 4.1 任务组 A：训练链路接入

- 定义 V3 projection -> 训练输入映射
- 让训练链路区分 approved / provisional / rejected
- 增加训练批次 summary

### 4.2 任务组 B：上下文 API 正式化

- 定义真实章节 context contract
- 提供章节级 state mapping
- 提供章节级 compare baseline

### 4.3 任务组 C：workbench 展示联动

- workbench 接 reverse-outline 结果
- workbench 接 style DNA
- workbench 接 checkpoint / admission

### 4.4 任务组 D：Corpus QC

- 批量质量报告
- label drift / style drift 检查
- 低质量样本筛除

## 5. 当前风险

- `V3` 目前是启发式 prototype，质量高于无治理拆解，但还不是最终生产规则
- `matrix_projection` 尚未正式进入训练主循环
- `mapped_chapter` 还不是完整章节 API

## 6. 最近验证

- `pytest tests -q -k "v2 or v3"` -> `19 passed`
- `npm test` -> `7 passed`
- `npm run build` -> success

## 7. 下一步优先级

1. `V3 projection` 正式接入训练链路
2. `V3` 结果进入 `V2 Workbench`
3. 补真实章节上下文 API
4. 补 corpus-level QC
