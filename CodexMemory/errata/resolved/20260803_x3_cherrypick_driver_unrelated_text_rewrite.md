# X3 TSV 驱动在 cherry-pick 时改写无关 i18n 引号格式
- 日期：2026-08-03
- 任务：仅把马戏 15 个礼包主数据名称配置从 dev_festival 单提交传播到 qa，并为 master 准备纯净 MR
- 现象：cherry-pick `239f43d7` 后，目标提交原本只改 Text 2 行，但相对 qa/master 基线的结果额外重写了 `TXT_DungeonCGDesc_1007/1103/1105/1107` 等无关行的英文引号/TSV quoting；若只看 commit 原始 stat 会漏掉夹带。
- 初判根因：`merge.tsv3way.driver` 在跨分叉分支 cherry-pick 时对目标分支已有 CSV/TSV 引号表达做了规范化，导致业务值近似等价但文件 diff 扩大；单提交传播后必须按目标分支基线审计最终 diff，不能只信源提交的文件/行数。
- 状态：open

---
## 复核结论（2026-08-03，Claude 批量分诊）
- 成立(跨模型,高价值)。护栏已写入 workflow_x3_merge_conflict_audit.md:单提交传播后必须按目标分支基线审计最终diff
- 状态：resolved
