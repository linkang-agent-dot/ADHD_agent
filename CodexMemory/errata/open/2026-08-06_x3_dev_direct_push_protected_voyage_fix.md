# X3 dev 直接推送被受保护分支拒绝

- 日期：2026-08-06
- 任务：提交航海奖励随机修复到 dev。
- 现象：构造了基于最新 `origin/dev` 的单文件提交 `ed528ab8246`，直接 push 到 `dev` 被 GitLab pre-receive 拒绝。
- 根因：x3-project 的 dev 是受保护分支，只允许 feature branch + MR；本轮虽已读过仓库知识库，执行提交时仍误试直推。
- 处理：把同一提交推到独立 feature 分支，创建显式 `target_branch=dev` 的 MR。
- 状态：open。
