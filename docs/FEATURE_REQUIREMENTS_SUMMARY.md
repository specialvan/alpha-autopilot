# alpha-autopilot 全工程功能需求评审梳理

**生成时间**: 2026-04-27  
**仓库**: [specialvan/alpha-autopilot](https://github.com/specialvan/alpha-autopilot)  
**项目定位**: Research-oriented 小说章节推荐与写作辅助系统（Baseline + Increment 分层治理）  
**主要语言/技术**: Python + FastAPI + React + TypeScript  
**当前分支**: `codex/history-review`

---

## 📊 仓库概览（对标 PlotPilot 结构）

- **治理结构**:
  - `v1/v2`: Baseline（稳定收口）
  - `v3`: Increment（留存目标函数与生成控制层）
  - `v4`: Increment 后续生产化推进（单任务生产周期门禁）
- **当前执行状态**:
  - `T01`~`T04` 已验收通过
  - 下一任务候选：`T05`（灰度与回滚流程）
- **测试资产规模（本地快照）**:
  - `tests/` Python 测试文件：26
  - `backend/tests/` Python 测试文件：1（模块化聚合）

---

## 🎯 4 大核心功能模块（全阶段汇总）

### 1. Baseline 推荐核心（V1/V2）
- 显式叙事状态建模：`StoryState` / `CharacterState`
- 特征矩阵 + 候选生成 + 排序
- 训练、反馈、版本快照、日志闭环
- API：推荐预览、训练、反馈、历史导出

### 2. 决策工作台（V2 Workbench）
- 独立路由工作台（与 Dashboard 分层）
- context / decision / validation 三栏决策视图
- 后端 context 拉取 + 本地回退
- compare baseline 与会话态校验链路

### 3. 留存驱动增量层（V3）
- 读者留存目标函数（Retention Target Function）
- 生成控制层（标签到决策变量映射）
- projection 接入训练主循环
- quality / admission / decision contract 语义收敛

### 4. 关系-性格-压力驱动生成层（V4）
- 人物关系位移 + 性格偏好 + 外部压力建模
- 跨章节记忆（relationship/feedback）与衰减去噪
- 题材自动学习守护与可观测趋势告警
- 生产门禁脚本：双路径、指标阈值、远端告警通道（IM/Webhook）已落地到 `T04`

---

## ⚠️ 当前 5 大工程 Open Items（全工程需求评审视角）

> 注：本清单是“工程需求阻断/风险项”，用于全阶段评审与排期，不等同于 GitHub Issue 编号。

### 🔴 FR-001 顶层主需求口径未完整纳入 V4（P0）
- **症状**: `MASTER_ROADMAP.md` 与 `PRD.md` 仍以 `v1/v2/v3` 为主口径，和当前 `V4` 生产推进状态冲突。
- **影响**: 全工程评审基线不一致，可能导致需求归属与验收门禁误判。
- **建议**: 更新主路线图与 PRD，显式纳入 `V4` 阶段/子阶段及门禁要求。

### 🔴 FR-002 同名 V4 需求文档双版本分叉（P0）
- **症状**: 根目录与 `claude_review_package/V4/` 下的 `V4_REQUIREMENT_SUMMARY_AND_SCOPE.md` 第 10 节口径不同。
- **影响**: Claude/Codex 评审会出现不同验收标准，无法形成单一审计结论。
- **建议**: 选定唯一权威版本，另一份改镜像或重定向。

### 🟠 FR-003 T05 灰度与回滚流程尚未执行验收（P1）
- **症状**: 生产周期任务板显示 `T05` 仍为 `PENDING`。
- **影响**: 发布治理（放量条件、回退触发、演练证据）尚未闭环。
- **建议**: 按当前单任务周期推进 `T05` 并产出验收报告。

### 🟡 FR-004 真实章节服务 API 仍未替换 mapped_chapter（P1）
- **症状**: 当前仍以本地 report/context 为主，线上真实章节服务未完全接入。
- **影响**: 工作台“真实上下文”能力在生产环境可用性受限。
- **建议**: 进入 V4 后续任务时优先补齐线上章节服务契约替换。

### 🟡 FR-005 前端状态文档测试证据口径不一致（P2）
- **症状**: `V2/frontend_PROJECT_STATUS.md` 与 `PROJECT_STATUS.md` 的测试数字不一致。
- **影响**: 全工程评审时质量证据可信度下降。
- **建议**: 统一前端测试命令、结果、日期并回填状态文档。

---

## 📌 已完成高价值收敛（可作为评审正向证据）

- ✅ `T01`: 单任务生产周期门禁固化  
- ✅ `T02`: `v4_enabled=true/false` 双路径强制验收  
- ✅ `T03`: P95/错误率/fallback 运行时指标与阈值告警  
- ✅ `T04`: 远端告警通道（IM/Webhook）+ on-call 校验 + 失败降级本地审计  
- ✅ `T04` 验收报告：`artifacts/production_cycles/t04/v4-t04-20260426T145418Z.md`

---

## 🚀 按优先级的修复路线图（对标 PlotPilot：稳定性 → 完整性 → 新增量）

### 第一阶段：稳定性口径收敛（立即）
- [ ] 修复 FR-001：主路线图/PRD 纳入 V4
- [ ] 修复 FR-002：V4 同名文档口径统一
- [ ] 修复 FR-005：前端状态文档测试证据统一

### 第二阶段：功能完整性收敛
- [ ] 推进并验收 `T05`：灰度与回滚流程
- [ ] 推进并验收 `T06`：生产验收收口
- [ ] 修复 FR-004：真实章节服务 API 替换 mapped_chapter

### 第三阶段：后续增量能力
- [ ] V4 按题材/流量分桶灰度与策略配置上线化
- [ ] 长序列场景与跨题材稳定性回归补强
- [ ] Workbench 的生产运维观测面板增强

---

## 📦 技术栈与工程接入

| 层级 | 技术栈 |
| --- | --- |
| 后端 API | FastAPI + Uvicorn + Pydantic Settings |
| 核心逻辑 | Python（状态建模、特征矩阵、候选排序、训练反馈） |
| 前端 | React 19 + React Router 7 + TypeScript + Vite + Vitest |
| 配置与治理 | `.env/.env.local` + 分层文档治理 + 生产周期门禁脚本 |
| 数据与存储 | 本地文件/JSONL 记忆与日志（database-free 核心） |

---

## 🧪 测试与验证基线（建议作为评审最小集）

```bash
python scripts/run_layered_tests.py
python scripts/run_v4_production_cycle.py T04
pytest tests/test_run_v4_production_cycle.py -q
pytest tests/test_alpha_autopilot_v4_modules.py backend/tests/test_narrative_v4_api.py -q
npm --prefix ui-react run test
npm --prefix ui-react run build
```

---

## 🔧 开发者快速启动（本仓库）

```bash
# 后端
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn backend.app.main:app --reload

# 前端
cd ui-react
npm install
npm run dev
```

访问点：
- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`
- 前端: `http://localhost:5173`（默认 Vite 端口）

---

## ✅ Claude / Codex 建议评审 4 维度（对标 PlotPilot）

### 1. 代码质量维度
- 分层边界是否一致（Baseline/Increment 不串层）
- V4 门禁脚本与测试命令是否和文档一一对应
- 同名需求文档是否存在分叉

### 2. 功能完整性维度
- V1/V2/V3/V4 是否形成完整阶段闭环
- `T05/T06` 是否具备可执行验收定义
- 真实章节上下文 API 替换是否落地

### 3. 稳定性维度
- 双路径回退（`v4_enabled=true/false`）是否持续可用
- 运行时指标阈值告警与远端路由是否可审计
- 前后端状态文档测试证据是否同步

### 4. 部署运维维度
- 灰度与回滚流程是否有值班手册和演练证据
- 告警路由（本地 + 远端）是否具备降级与去重抑制
- 发布前门禁是否可重复执行并可追溯

---

## 一句话结论

alpha-autopilot 的“实现与测试”已经进入 V4 生产节奏，但“全工程需求口径”仍需先完成文档层统一收敛；完成 FR-001/FR-002 后再做 Claude 复审，才能得到可审计的全阶段通过结论。
