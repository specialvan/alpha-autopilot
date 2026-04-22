# V2 Documentation Backfill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the core project documents so they align with the approved `v2` architecture calibration spec and stop mixing first-stage baseline goals with second/third-stage evolution work.

**Architecture:** This plan updates the documentation layer first, not the runtime. It rewrites `PRD.md`, `novel_fusion_autopilot_interface_draft.md`, and `MASTER_ROADMAP.md` so they all reflect the same `v1` freeze, `v2` parallel calibration, `v3` future-only model. A final consistency pass removes conflicting language and verifies the rewritten documents agree with the approved spec.

**Tech Stack:** Markdown, Git, PowerShell text inspection commands

---

## File Map

- Modify: `D:\workspace\alpha-autopilot\PRD.md`
  - Rewrite the system structure, scope, and acceptance criteria so they include rule/search/evaluation/validation and reframe the current target as first-stage recalibration.
- Modify: `D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md`
  - Backfill missing top-level abstractions and contracts for `RuleCheck`, `NarrativeAction`, search, validation assets, and migration boundaries.
- Modify: `D:\workspace\alpha-autopilot\MASTER_ROADMAP.md`
  - Re-state stage boundaries so `v2` is the first-stage recalibration line and `v3` remains future work only.
- Reference: `D:\workspace\alpha-autopilot\docs\superpowers\specs\2026-04-21-v2-architecture-calibration-design.md`
  - Approved source of truth for the rewrite.

### Task 1: Rewrite PRD Baseline

**Files:**
- Modify: `D:\workspace\alpha-autopilot\PRD.md`
- Reference: `D:\workspace\alpha-autopilot\docs\superpowers\specs\2026-04-21-v2-architecture-calibration-design.md`
- Test: `D:\workspace\alpha-autopilot\PRD.md`

- [ ] **Step 1: Write the replacement outline into the PRD**

```markdown
## 3. 核心原则

1. 爆款拆解是先验，不是最终答案
2. 特征矩阵是核心，但必须可解释、可迭代
3. 系统必须先在规则约束下生成合法推进动作，再进入搜索与评分
4. 状态推演负责当前写作进程下的局部最优探索
5. 反馈闭环负责修正评价，不等同于第三阶段价值自适应进化
6. 必须保留人工可控性、版本可追溯性和验证口径

## 4. 系统结构

### 4.1 规则层
- 定义合法动作
- 定义前提不足动作
- 定义禁止原因

### 4.2 状态层
- 章节位置
- 主线进度
- 支线进度
- 冲突强度
- 情绪温度
- 节奏速度
- 伏笔负载
- 回收压力

### 4.3 搜索层
- 在合法动作集合上执行单步推演
- 为多步推演保留扩展位
- 输出候选路径而不只是裸分数

### 4.4 评价层
- 结构价值
- 连续性安全
- 情绪/爽点回报
- 伏笔与回收平衡
- 题材/阶段适配度

### 4.5 反馈层
- 记录推荐结果与真实效果差异
- 更新评价权重
- 保留训练日志与版本快照

### 4.6 验证层
- golden cases
- rule fixtures
- evaluation ledger
- 替代数据库验证口径
```

- [ ] **Step 2: Rewrite the scope and acceptance criteria**

```markdown
## 5. 开发范围

### 当前版本必须完成
- 规则层基础抽象
- 状态建模
- 单步搜索接口
- 分维度评价输出
- 训练样本读取
- 反馈记录接口
- 版本快照
- 示例数据集
- golden cases / rule fixtures / evaluation ledger

### 当前版本明确不包含
- 第三阶段推荐价值自适应进化
- 新功能与新模型能力扩展
- 完全替代数据库的结论性宣称

## 7. 验收标准

- 能使用示例样本完成初版矩阵训练
- 能对当前故事状态先输出合法动作判断，再输出排序后的章节建议
- 能输出分维度解释，而不是单一总分
- 能基于反馈进行权重更新并保留版本快照
- 能通过 golden cases 和 rule fixtures 复盘推荐结果
- 结构可继续扩展到 `novel-fusion-autopilot`
```

- [ ] **Step 3: Run a targeted check for outdated first-stage wording**

Run:

```powershell
Select-String -Path 'D:\workspace\alpha-autopilot\PRD.md' -Pattern '多步章节建议|第三阶段|价值自适应|只排序|不依赖海量数据库'
```

Expected:

```text
Only acceptable matches remain where the wording is explicitly qualified; no line should imply that third-stage evolution is part of the current baseline.
```

- [ ] **Step 4: Commit**

```bash
git add D:/workspace/alpha-autopilot/PRD.md
git commit -m "docs: rewrite prd around v2 calibration baseline"
```

### Task 2: Rewrite Interface Draft Contracts

**Files:**
- Modify: `D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md`
- Reference: `D:\workspace\alpha-autopilot\docs\superpowers\specs\2026-04-21-v2-architecture-calibration-design.md`
- Test: `D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md`

- [ ] **Step 1: Insert the missing abstraction layers**

```markdown
## 2. 总体接口分层

### 2.1 规则层
负责根据当前故事状态生成合法动作、前提不足动作和禁止原因。

### 2.2 状态层
负责接收小说上下文，构建结构化故事状态。

### 2.3 搜索层
负责在合法动作集合上执行单步推演，并为未来多步推演保留扩展位。

### 2.4 评价层
对动作或动作路径做分维度打分与解释。

### 2.5 反馈层
接收实际写作结果、人工修正或读者反馈，更新评价权重。

### 2.6 验证层
管理 golden cases、rule fixtures、evaluation ledger 和验证记录。

### 2.7 版本层
管理矩阵快照、训练记录、样本版本。
```

- [ ] **Step 2: Add the missing contracts**

````markdown
### RuleCheck

```python
@dataclass
class RuleCheck:
    action: str
    status: str  # legal / blocked / prerequisite_missing
    prerequisites: List[str]
    blockers: List[str]
    risk_flags: List[str]
```

### NarrativeAction

```python
@dataclass(frozen=True)
class NarrativeAction:
    action: str
    delta: Dict[str, float]
    explanation: str
```

### SearchResult

```python
@dataclass
class SearchResult:
    action: NarrativeAction
    rule_check: RuleCheck
    score: float
    details: Dict[str, float]
```

### ValidationRecord

```python
@dataclass
class ValidationRecord:
    case_id: str
    accepted_actions: List[str]
    blocked_actions: List[str]
    top_action: str
    notes: str
```
````

- [ ] **Step 3: Rewrite migration boundaries**

```markdown
### 保留
- 特征矩阵思想
- 规则约束 + 状态推演思想
- 训练日志
- 版本快照
- 反馈闭环
- 验证资产

### 重新实现
- `RuleCheck` / `NarrativeAction` / `SearchResult` 契约
- 真实 API 网关
- 数据校验层
- 异步任务调度
- 持久化存储接口
- UI 与交互层

### 不建议直接迁移
- `v1` 中语义已漂移的核心实现和模块路径
- 只适用于棋盘的搜索逻辑
- 与小说无关的评估维度
```

- [ ] **Step 4: Run a contract consistency check**

Run:

```powershell
Select-String -Path 'D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md' -Pattern 'RuleCheck|NarrativeAction|SearchResult|ValidationRecord|规则层|搜索层|验证层'
```

Expected:

```text
Each new contract and layer heading appears at least once, and the document no longer jumps directly from state to scoring without legality/search contracts.
```

- [ ] **Step 5: Commit**

```bash
git add D:/workspace/alpha-autopilot/novel_fusion_autopilot_interface_draft.md
git commit -m "docs: backfill v2 interface abstractions"
```

### Task 3: Rewrite Master Roadmap Stage Boundaries

**Files:**
- Modify: `D:\workspace\alpha-autopilot\MASTER_ROADMAP.md`
- Reference: `D:\workspace\alpha-autopilot\docs\superpowers\specs\2026-04-21-v2-architecture-calibration-design.md`
- Test: `D:\workspace\alpha-autopilot\MASTER_ROADMAP.md`

- [ ] **Step 1: Rewrite the stage model**

```markdown
项目演进分为三个语义层：

- `v1`：冻结中的当前原型，仅保底 MVP 与阻塞 bug 修复
- `v2`：第一阶段回炉重构线，负责抽象校准与最小闭环重建
- `v3`：未来路线图，承接稳定化、价值进化与新功能需求
```

- [ ] **Step 2: Rewrite the first-stage section as recalibration**

```markdown
## 2. 第一阶段回炉：架构校准与最小闭环重建

### 阶段目标
- 校准顶层抽象
- 冻结规则层、搜索层、评价层、验证层
- 重建最小可验证闭环

### 验收问题
- 系统是否能先判定合法动作，再进行推荐
- 系统是否能输出分维度解释
- 系统是否具备可回放的验证资产
- 系统是否能在不破坏 `v1` 的前提下并行演进
```

- [ ] **Step 3: Rewrite later-stage wording so v3 remains future-only**

```markdown
## 3. 后续阶段：稳定化与扩展
- 仅在 `v2` 合入后启动

## 4. 远期阶段：推荐价值自适应进化
- 当前不进入 `v2` 基线
- 仅作为未来路线图存在
```

- [ ] **Step 4: Run a roadmap drift check**

Run:

```powershell
Select-String -Path 'D:\workspace\alpha-autopilot\MASTER_ROADMAP.md' -Pattern '第一阶段|第二阶段|第三阶段|价值自适应|v1|v2|v3'
```

Expected:

```text
Matches show a clean split: v1 frozen baseline, v2 recalibration line, v3 future-only. No section should imply that value evolution belongs to the current rewrite baseline.
```

- [ ] **Step 5: Commit**

```bash
git add D:/workspace/alpha-autopilot/MASTER_ROADMAP.md
git commit -m "docs: realign master roadmap to v1 v2 v3 model"
```

### Task 4: Run Documentation Consistency Sweep

**Files:**
- Modify: `D:\workspace\alpha-autopilot\PRD.md`
- Modify: `D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md`
- Modify: `D:\workspace\alpha-autopilot\MASTER_ROADMAP.md`
- Reference: `D:\workspace\alpha-autopilot\docs\superpowers\specs\2026-04-21-v2-architecture-calibration-design.md`
- Test: `D:\workspace\alpha-autopilot\PRD.md`

- [ ] **Step 1: Verify the three rewritten docs share the same layer vocabulary**

Run:

```powershell
@(
  'D:\workspace\alpha-autopilot\PRD.md',
  'D:\workspace\alpha-autopilot\novel_fusion_autopilot_interface_draft.md',
  'D:\workspace\alpha-autopilot\MASTER_ROADMAP.md'
) | ForEach-Object {
  Write-Host "== $_ ==";
  Select-String -Path $_ -Pattern '规则层|搜索层|评价层|验证层|golden cases|rule fixtures|evaluation ledger|v1|v2|v3'
}
```

Expected:

```text
All three files contain the same core layer vocabulary and the same v1/v2/v3 split.
```

- [ ] **Step 2: Inspect the final diff**

Run:

```powershell
git diff -- PRD.md novel_fusion_autopilot_interface_draft.md MASTER_ROADMAP.md
```

Expected:

```text
Diff shows only documentation realignment toward the approved v2 calibration model, with no accidental code or unrelated text changes.
```

- [ ] **Step 3: Commit**

```bash
git add D:/workspace/alpha-autopilot/PRD.md D:/workspace/alpha-autopilot/novel_fusion_autopilot_interface_draft.md D:/workspace/alpha-autopilot/MASTER_ROADMAP.md
git commit -m "docs: align core project docs with v2 calibration spec"
```
