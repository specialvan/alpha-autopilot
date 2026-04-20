# novel-fusion-autopilot 接口草案评审任务单

## 任务名称

评审 `alpha-autopilot` 到 `novel-fusion-autopilot` 的接口迁移草案。

## 评审目标

确认该小说章节推荐原型是否具备迁移到正式工程的最小可行接口。

## 评审范围

### 必看文档
- `novel_fusion_autopilot_interface_draft.md`
- `novel_fusion_autopilot_migration_plan.md`
- `PRD.md`
- `PROJECT_STATUS.md`
- `TECH_BOTTLENECKS.md`
- `CODEx_REVIEW_PACKAGE.md`

### 必看代码
- `alpha_autopilot/narrative.py`
- `alpha_autopilot/feature_matrix.py`
- `alpha_autopilot/planner.py`
- `alpha_autopilot/trainer.py`
- `alpha_autopilot/versioning.py`
- `alpha_autopilot/training_log.py`
- `train.py`
- `recommend.py`

## 重点检查项

1. `StoryState` 数据契约是否足以表达章节上下文
2. `FeatureMatrix` 是否适合作为可解释评分核心
3. `ChapterPlanner` 是否能作为章节推荐服务雏形
4. 训练日志和版本快照是否支持复盘与回滚
5. 迁移边界是否清晰，是否避免与 `novel-fusion-autopilot` 过早耦合
6. 接口命名是否便于后续工程化重构

## 评审输出要求

- 接口是否可用
- 哪些字段需要补充
- 哪些服务应继续抽象
- 哪些部分不建议直接迁移
- 是否建议进入下一阶段正式集成

## 预期结论

如果评审通过，则可以把当前原型作为 `novel-fusion-autopilot` 的章节推荐基础模块接口蓝本。
