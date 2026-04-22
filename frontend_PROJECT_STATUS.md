# 前端项目进度表

## 当前阶段

- 项目名称：小说章节智能推荐前端工作台
- 当前状态：总览 dashboard 保留，`V2 Workbench` 已升级为独立路由和决策驾驶舱

## 进度清单

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 总览 dashboard | 已完成 | 现有 `v1` 总览、训练、反馈、历史面板仍可用 |
| 路由壳 | 已完成 | 已引入 `react-router-dom`，支持 `/` 与 `/v2/workbench` |
| `V2 Workbench` 页面壳 | 已完成 | 已具备独立 top bar、三栏布局、独立样式 |
| Context Rail | 已完成 | 已支持 source、chapter context、override、state diff |
| Decision Surface | 已完成 | 已支持 top action、候选结果、score breakdown 基础展示 |
| Validation Rail | 已完成 | 已支持 rule summary、validation record、run history |
| workbench 上下文接线 | 已完成 | 已优先拉取 `/api/v2/workbench/contexts`，失败回退本地 seed |
| 路由与页面测试 | 已完成 | 已覆盖 router smoke test、workbench page interaction、helper tests |

## 当前已知风险

- `V2 Workbench` 目前是决策工作台，不是完整作者工作台
- `Context Rail` 的章节上下文仍是聚合式 live context，不是完整章节域模型
- workbench 的 compare / history 仍是会话级前端状态，不是完整持久化历史
- dashboard 与 workbench 视觉语言已统一，但信息架构仍有进一步压缩空间

## 最新验证

- `npm test` -> `5 files passed / 7 tests passed`
- `npm run build` -> 成功

## 下一步计划

1. 把 reverse-outline / style DNA / QC 结果引入 `V2 Workbench`
2. 增加真实章节上下文映射，而不是仅用聚合 state
3. 增强 compare baseline 选择与历史对比可视化
4. 继续压缩 dashboard 原型区块，突出 route-based workflow
