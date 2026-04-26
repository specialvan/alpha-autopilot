# Review Evidence（Codex）

评审环境：

- CWD: `D:\workspace\alpha-autopilot`
- Branch: `codex/history-review`
- Date: 2026-04-24

## 1) 测试与构建证据

### Python 全量测试

命令：

```powershell
pytest tests -q
```

结果：

```text
33 passed in 0.42s
```

### 分层测试（core/quality/api/import/frontend）

命令：

```powershell
python scripts\run_layered_tests.py core quality api import frontend
```

结果要点：

- core: 6 passed
- quality: 6 passed
- api: 7 passed
- import: 4 passed
- frontend(vitest): 5 files / 10 tests passed

### 前端构建

命令：

```powershell
cd ui-react
npm run build
```

结果：

```text
vite build ... ✓ built in 627ms
```

### 静态检查

命令：

```powershell
ruff check alpha_autopilot alpha_autopilot_v2 alpha_autopilot_v3 backend scripts tests
```

结果：

- 4 个 `F401`（未使用导入），无更高等级阻断错误。

## 2) 关键问题复现实验

### 2.1 `imported_contexts` 对坏 JSON fail-closed

实验：构造 `reverse_outline_records.jsonl` 含坏行，调用 `NarrativeV2WorkbenchService.list_contexts()`。

输出：

```text
JSONDecodeError
Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

对应代码：

- `backend/app/services/narrative_v2/imported_contexts.py:64`
- `backend/app/services/narrative_v2/imported_contexts.py:79`

### 2.2 `NarrativeV2WorkbenchService` 默认共享 `HistoryService` 实例

实验：创建两个 service 实例，比较 `history_service` 对象 ID。

输出：

```text
True
```

对应代码：

- `backend/app/services/narrative_v2/workbench_service.py:14`

### 2.3 README 推荐入口与主后端路由不一致

实验：比较 `backend_app` 与 `backend.app.main` 路由是否含关键接口。

输出：

```text
backend_app False False
backend.app.main True True
```

含义：

- `backend_app` 不含 `/api/v2/workbench/contexts` 与 `/api/history`
- `backend.app.main` 才含主链路接口

对应代码：

- `README.md:44`
- `backend/app/main.py:17-23`

### 2.4 ledger 读取对坏行无容错

实验：构造坏行 JSONL，调用 `read_ledger_entries`。

输出：

```text
JSONDecodeError
```

对应代码：

- `alpha_autopilot_v2/validation/ledger.py:32`

