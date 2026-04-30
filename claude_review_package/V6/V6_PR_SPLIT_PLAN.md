# V6 PR 拆分执行方案（PR-AA-09 ~ PR-AA-15）

## 1. 拆分原则

- 先 P0 后 P1 后 P2，避免跨优先级并行导致返工
- 每个 PR 独立可测、可回滚、可审计
- 每个 PR 默认只改 `narrative_v6` 层及必要接入位
- 每个 PR 都保留 deterministic/mock 测试路径

## 2. PR 切片总览

| PR | 分支建议 | 优先级 | 核心交付 | 主要文件 | 必跑测试 |
| --- | --- | --- | --- | --- | --- |
| PR-AA-09 | `codex/v6-aa09-seed-extractor` | P0 | `NarrativeSeed` schema + 提取服务 + API | `schemas.py`, `seed_extractor.py`, `narrative_v6.py` | `tests/test_narrative_seed_extractor.py` |
| PR-AA-10 | `codex/v6-aa10-parameterizer` | P0 | `ParameterizedCharacterProfile` 自动参数化 | `character_parameterizer.py` | `tests/test_character_parameterizer.py` |
| PR-AA-11 | `codex/v6-aa11-parallel-sim` | P0 | 2~3 路并行推演 + 排序 + 决策摘要 | `parallel_simulation.py`, `scoring.py`, `state_store.py` | `tests/test_parallel_plot_simulation.py` |
| PR-AA-12 | `codex/v6-aa12-conflict-probe` | P1 | K 轮交互冲突探针 | `conflict_probe.py` | `tests/test_emergent_conflict_probe.py` |
| PR-AA-13 | `codex/v6-aa13-event-injection` | P1 | 事件注入 checkpoint 与重算 | `event_injection.py` | `tests/test_event_injection_checkpoint.py` |
| PR-AA-14 | `codex/v6-aa14-character-interview` | P1 | 角色访谈 API + transcript 导出 | `character_interview.py`, `ui-react/*` | `tests/test_character_interview.py` |
| PR-AA-15 | `codex/v6-aa15-group-memory` | P2 | 群体记忆层与传播日志 | `group_memory.py` | `tests/test_group_memory_layer.py` |

## 3. 依赖与合并顺序

1. PR-AA-09（种子）
2. PR-AA-10（人设参数化，依赖 09）
3. PR-AA-11（并行推演，依赖 09+10）
4. PR-AA-12（冲突探针，依赖 11）
5. PR-AA-13（事件注入，依赖 11/12）
6. PR-AA-14（角色访谈，依赖 10）
7. PR-AA-15（群体记忆，依赖 09，联动 12/13）

## 4. 并行策略

- Lane A（主链路）：09 -> 10 -> 11
- Lane B（交互增强）：12 -> 13
- Lane C（角色互动）：14
- Lane D（世界扩展）：15（在 11 稳定后启动）

并行前提：

- Lane B/C/D 不得改写 Lane A 的已冻结 schema 字段语义
- 所有 lane 必须共享同一个 `schemas.py` 契约版本号

## 5. 每个 PR 的完成定义（DoD）

每个 PR 必须同时满足：

1. AC 测试通过（100%）
2. 回滚路径已写明（最多 5 步）
3. 新增可观测字段已输出
4. 不破坏现有 v2/v3/v4 回归
5. 文档同步（任务板、状态、验收清单）

## 6. 回滚约定

- PR-AA-09~11：回退路由与服务入口，恢复 V4/V3 默认决策链
- PR-AA-12~15：能力开关关闭即恢复到无增强模式
- 涉及持久化变更必须有逆向脚本或兼容期

## 7. 建议提交粒度

- 一个 PR 对应一个能力切片（不要把多个 AA 编号混在同 PR）
- 一个 PR 内按“schema -> service -> api -> test -> doc”顺序提交
- 每次提交附带验收命令与输出摘要
