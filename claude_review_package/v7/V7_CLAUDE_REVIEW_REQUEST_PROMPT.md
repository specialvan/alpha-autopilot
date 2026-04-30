# V7 Claude Review Request Prompt

请对以下提交执行 V7 阶段评审（第三十七轮生产化增强验收）：

## 评审目标

1. 验证治理升级事件自愈运行历史（auto-remediations）接口契约。
2. 验证自愈执行结果与历史记录字段的一致性。
3. 验证历史分页能力在值班消费场景下的稳定性。
4. 验证 dry-run 与 apply 两类轨迹均可审计追踪。

## 重点检查项

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations`
  - 计数字段：`total_records/malformed_line_count`
  - 分页字段：`limit/cursor/next_cursor/has_more`
  - 记录字段：`action/executed/emitted/pruned/emitted_event_id/auto_prune_*`
- 关联核验：
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`

## 输出要求

请按以下结构输出：
1. 阻塞问题（P0）
2. 高优先修复（P1）
3. 可后续迭代优化（P2）
4. 可验收结论（是否通过第三十七轮生产化验收）
5. 第三十八轮建议切片（按 PR-AA 编号）