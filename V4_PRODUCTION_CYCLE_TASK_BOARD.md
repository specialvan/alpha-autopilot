# V4 生产周期任务板（单任务执行制）

## 1. 执行规则

1. 每个生产周期只允许一个 `Active` 任务。
2. 只要当前任务未验收通过，不启动下一个任务。
3. 每个任务必须有固定验收命令与验收报告落盘路径。
4. 每轮交付必须回写任务状态、风险与下一任务候选。

## 2. 当前周期

- active_task_id: `T04`
- active_task_name: 远端告警通道
- cycle_status: `ACCEPTED`
- acceptance_command: `python scripts/run_v4_production_cycle.py T04`
- acceptance_report_root: `artifacts/production_cycles/t04/`
- next_task_candidate: `T05`

## 3. 任务池（按生产周期串行）

| Task ID | 任务名称 | 目标 | 主要交付物 | 验收命令 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `T01` | 生产周期基线门禁固化 | 把“单任务执行 + 单任务验收”机制写入脚本与任务板 | `scripts/run_v4_production_cycle.py`、`tests/test_run_v4_production_cycle.py`、本任务板 | `python scripts/run_v4_production_cycle.py T01` | `ACCEPTED (2026-04-26)` |
| `T02` | 双路径强制验收 | 将 `v4_enabled=true/false` 双路径纳入周期门禁 | 增量测试与门禁脚本配置 | `python scripts/run_v4_production_cycle.py T02` | `ACCEPTED (2026-04-26)` |
| `T03` | 生产指标与阈值 | 定义并落地 P95/错误率/fallback 结构化指标 | 指标聚合与告警阈值配置 | `python scripts/run_v4_production_cycle.py T03` | `ACCEPTED (2026-04-26)` |
| `T04` | 远端告警通道 | 将本地告警扩展为 IM/Webhook 远端路由 | 告警路由实现与值班校验 | `python scripts/run_v4_production_cycle.py T04` | `ACCEPTED (2026-04-26)` |
| `T05` | 灰度与回滚流程 | 固化放量条件、回退触发条件、回滚脚本演练 | 发布治理文档与演练证据 | `python scripts/run_v4_production_cycle.py T05` | `PENDING` |
| `T06` | 生产验收收口 | 汇总任务证据并形成可审计发布包 | 周期报告与交接清单 | `python scripts/run_v4_production_cycle.py T06` | `PENDING` |

## 4. 周期验收定义

- `PASS`：任务验收命令返回 0，且生成报告文件。
- `FAIL`：任一验收命令失败或报告未落盘。
- `ACCEPTED`：`PASS` 且任务板状态更新为 `ACCEPTED`，可进入下一任务。
