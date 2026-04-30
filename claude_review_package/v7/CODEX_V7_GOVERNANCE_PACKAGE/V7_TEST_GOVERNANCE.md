# V7 Test Governance

## 1. 必跑类型

- 单元测试：受影响模块必须全过。
- 集成测试：`/api/narrative/v7/*` 关键链路必须全过。
- 回归测试：`v1/v2/v3/v6` 默认路径不得退化。
- 离线评估：至少 1 个核心效果指标 + 1 个守护指标。

## 2. 禁止项

- 禁止以 `skip/xfail` 代替应通过用例。
- 禁止只做人工口头验收。
- 禁止无评估证据进入主线候选。

## 3. V7 特殊关注

- NQM 采样耗时与 token 成本要单独监控。
- 开篇门禁、反模式、死锁路由必须测试 override 分支。
- 阈值版本更新必须有审计快照。

## 4. 验收记录

- command_log:
- test_summary:
- offline_metrics:
- rollback_rehearsal_result:
