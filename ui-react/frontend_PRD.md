# React 前端工程需求说明书

## 1. 目标

将 `alpha-autopilot` 的静态工作台升级为 React 版本，以便后续接入真实后端接口、状态管理与组件化维护。

## 2. 目标能力

- React 组件化拆分
- 页面结构与静态版保持一致的业务语义
- 为推荐结果、训练日志、版本快照预留数据绑定位置
- 支持后续接入真实 API
- 保持量化工作台风格的高信息密度界面

## 3. 组件范围

- `Sidebar`
- `Hero`
- `MetricsGrid`
- `StoryStatePanel`
- `MatrixPanel`
- `RecommendationsPanel`
- `FeedbackPanel`
- `LogsPanel`

## 4. 技术要求

- React 18/19 风格均可兼容
- 使用 TypeScript
- 使用 Vite 构建
- 样式保持现代化面板布局
- 组件与数据解耦

## 5. 验收标准

- 组件可独立维护
- 目录结构清晰
- 能直接在浏览器运行
- 后续可平滑接入真实 API
