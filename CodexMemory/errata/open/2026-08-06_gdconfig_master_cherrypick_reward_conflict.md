# gdconfig master 单改动传播 Reward 冲突

- 日期：2026-08-06
- 任务：把马戏节寻宝世界榜奖励从 qa 传播到 master MR
- 现象：在基于 `origin/master` 的隔离分支 cherry-pick `7fc8c079` 时，`Reward__Reward.tsv` 出现 22 项需裁决冲突，并触发 Reward col0 漂移防护（16040001 / RewardID 81901）。
- 根因：master 比 qa 落后 176 个提交，目标奖励组/seq 在两条分支上已有不同历史；虽然只传播一个业务提交，底层 Reward 行不能直接按补丁文本套用。
- 处理：保持 cherry-pick 状态，加载官方 `x3_skill_conflict.md`，按 RewardID 业务键和三方内容逐项裁决；禁止整表选 ours/theirs，完成后跑严格三方审计、列守恒和 ExportTable。
- 状态：open
