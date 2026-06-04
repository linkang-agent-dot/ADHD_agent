---
name: x3-branch-check-before-write
description: 写 X3 配置前必须 git branch --show-current 确认在目标分支，避免被 user 在另一窗口切换分支后误 commit 到错分支
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2698066a-6dc9-4d48-8e43-b75b32db6c72
---

# 写 X3 配置前必须确认分支

## 规则
在每次 `git commit` X3 配置改动前，**必须**先执行 `git branch --show-current` 并确认是预期的分支。

## Why
X3 `gdconfig` 仓库经常多人/多窗口并行：
- 用户可能在另一个 WPS/终端切到尼罗优化分支做别的事
- Sub-agent 跑期间用户可能 `git checkout` 切走
- Excel COM 写文件不感知 git 分支，写完直接 commit 会落到当前分支

2026-05-25 X3NEW-736 修复期间踩坑：
1. 18:32 我在 dev-summer-love-song push 完 734
2. 18:45 用户自行切到 dev_nile_optimization_v1 做尼罗优化（我没察觉）
3. 18:53 用户在 dev_nile_optimization_v1 commit ef201de
4. 19:53 我接着写 Rank.xlsx 改 736 → commit 直接落到 dev_nile_optimization_v1（错分支）
5. 必须 cherry-pick 到 dev-summer-love-song + reset 清理 dev_nile_optimization_v1

整套挽救流程涉及 git reset --hard（破坏性操作），需要用户授权，浪费 5+ 轮对话。

## How to apply
1. 每次 `git add` + `git commit` X3 配置文件前，先 `git branch --show-current`
2. 如果分支不对，先 `git checkout <目标分支>` 再 commit
3. 在长会话/多 sub-agent 流程里，**每次 sub-agent 写完文件、回到主会话准备 commit 时**都要重新确认一遍分支
4. 派写入 sub-agent 时，在 prompt 里要求 sub-agent 写完后报告"当前分支是 X"，主会话据此核对

## 关联
- [[reference_x3_gdconfig_repo]] — X3 配置仓库路径和分支命名规范
- [[reference_x3_score_activity]] — 实战案例 X3NEW-734/736
