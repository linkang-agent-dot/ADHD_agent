# X3 dev 推送遇到远端并发推进

- 日期：2026-08-06
- 任务：马戏节排行榜排序与寻宝世界榜奖励调整
- 现象：本地提交 `ae459ae5` 后执行 `git push origin dev`，pre-push 检查无硬拦截，但远端因已有新提交返回 `fetch first`，非快进拒绝。
- 根因：开工时本地 `dev` 与 `origin/dev` 同步，但编辑/导表期间其他人向共享 `dev` 推送了新提交。
- 处理：不强推；先 fetch 并审查远端新增提交是否触碰本轮四张 TSV，再把本地单提交 rebase 到最新 `origin/dev`，重跑定向 diff/导表后推送。

## rebase 阶段 Reward TSV 冲突

- 现象：目标业务 ID 在远端未变，但 `git rebase origin/dev` 于 `Reward__Reward.tsv` 产生内容冲突；tsv_merge_pro 报 23 项需人工处理及一条 81901 内容守恒断言。
- 根因：本轮把 81901~81906 旧行替换为新 col0 段，同时远端在同一大表追加/调整了其他奖励行；按行三方合并无法自动证明“旧组删除 + 新组重建”与远端新增互不冲突。
- 处理：进入官方 `x3_skill_conflict.md` 流程，按 RewardID/ItemID 语义合并：保留远端全部非目标行，目标 81901~81908 使用本轮新结构；完成双向丢行审计和全量 ExportTable 后再继续 rebase。
- 状态：open
