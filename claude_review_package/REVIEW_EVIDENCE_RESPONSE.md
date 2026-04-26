# Review Evidence Response

## 结论

这份证据链是有效的，足以证明当前系统并非整体失效；但它同时也证明了若干真实风险仍然存在。此前那版评审如果把已经修复或已经不再成立的内容继续当作阻断项，就需要打回并重写口径。

## 证据链的有效部分

### 1. 全量测试与分层测试通过

证据显示：

- `pytest tests -q` -> `33 passed`
- 分层测试覆盖 `core`、`quality`、`api`、`import`、`frontend`
- `npm run build` 成功
- `ruff check` 仅有低级别导入警告

这说明当前项目不是“不可用”状态，评审不能再用整体失效的口径。

### 2. 坏 JSON fail-closed 复现成立

证据链明确显示：

- `NarrativeV2WorkbenchService.list_contexts()` 遇到坏 JSONL 会抛 `JSONDecodeError`
- 定位到 `backend/app/services/narrative_v2/imported_contexts.py:64` 和 `:79`

这说明质量工件读取缺少容错，单个坏记录会拖垮 workbench contexts。

### 3. 默认共享 `HistoryService` 实例复现成立

证据链显示：

- 两个 `NarrativeV2WorkbenchService` 实例共享同一个 `history_service`
- 定位到 `backend/app/services/narrative_v2/workbench_service.py:14`

这说明服务层仍存在隐式共享耦合，边界不够清晰。

### 4. README 启动入口与主后端路由不一致

证据链显示：

- `backend_app` 不含 `/api/v2/workbench/contexts` 与 `/api/history`
- `backend.app.main` 才含主链路接口
- 但 README 仍指向 demo 启动方式

这会误导联调、评审与验收入口。

### 5. ledger 读取对坏行无容错

证据链显示：

- `read_ledger_entries` 遇坏行会抛 `JSONDecodeError`
- 定位到 `alpha_autopilot_v2/validation/ledger.py:32`

这说明审计链路仍有单点脆弱性。

## 需要打回的过时评审结论

以下结论如果还被写进最终评审，就应打回：

- “系统整体不能启动”
- “前端/后端整体不可交付”
- “所有导出链路都因 repository.store 崩溃”
- “feedback 向 metrics 写入 dict 导致属性错误”
- “历史筛选 reset 不能清空”
- “导出 URL 必然硬编码 127.0.0.1:8000”

这些如果已经被修复或不再成立，就不该继续作为当前阻断项。

## 应保留的真实问题

### P1

1. 质量工件坏 JSON 会打崩 workbench contexts
2. `NarrativeV2WorkbenchService` 默认共享 `HistoryService` 实例
3. README 启动入口与主后端入口不一致

### P2

4. 历史时间线的窗口化语义不够明确
5. ledger 读取坏行无容错

## 推荐的最终评审口径

应改为：

> 证据链证明项目并非整体失效，但当前仍存在若干可验证的 P1/P2 风险。评审需要移除过时阻断项，保留仍成立的真实问题，并把风险描述收敛到当前代码状态。

## 处理建议

1. 打回过时阻断
2. 保留仍成立的 P1/P2 风险
3. 重新分级严重性
4. 用当前证据重新撰写最终评审结论
5. 明确主后端入口，避免 demo 与主线混淆

## 一句话总结

这份证据链是有效的，但评审结论需要基于它重新校准：**打回过时结论，保留真实风险，重写最终口径。**