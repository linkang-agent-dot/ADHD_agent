---
name: reference_x3_worktree_cleanup
description: C:\X3 下 gdconfig 一堆 worktree 哪些能删的三步安全判定法
metadata: 
  node_type: memory
  type: reference
  originSessionId: a547f8e5-b67e-45e6-ac45-392e1175419f
---

# X3 gdconfig worktree 清理：能否安全删的三步判定

`C:\X3\` 下 `gdconfig` 是主仓（挂 `dev_festival`），其余 `gdconfig-*` 都是 `git worktree`。判「哪些能删」别凭目录名猜，跑 `git worktree list` 后对每个按下面三步过。

**核心前提**：`git worktree remove` 只删工作目录，**不删分支 ref**；`origin/*` 远端分支更不受影响。真正会丢东西的只有两种：① 未提交改动 ② 只活在本地、远端一个分支都没有的提交。

## 三步判定（全过 = 安全删）

1. **有没有未提交改动** → `git -C <wt> status --porcelain | wc -l`，非 0 就先别删（会丢），除非确认丢弃。
2. **本地独有提交在远端有没有备份** → 关键不是"是否 merged"，而是"内容在不在远端任一分支"：
   - `git log --no-merges origin/dev_festival..<branch>` 看有没有**非 merge 的真实内容提交**；只有 merge 提交 = 零独有内容，删掉零损失。
   - 或对每个内容提交 `git branch -r --contains <hash>`，返回空 = 仅本地 = 真丢。
3. **长期共享分支**（`dev`/`dev_festival`/`qa`/`qa_sync`）的 worktree：内容只要在 `origin/*` 就随时 `git worktree add ../xx <branch>` 重拉，删本地 ref 无损。

## 常见误判（2026-07-16 实操踩到的）

- **"NO-UPSTREAM 未跟踪远端" ≠ 会丢**：deepsea-recharge/turntable 分支没跟远端，但独有的全是 `Merge dev/qa` 提交、零内容，删掉零损失。
- **"ahead 35/482 commits" ≠ 有独有工作**：feature 分支基于 dev 会天然领先 dev_festival 一大截；handbook-v2 领先 411 但已并入 origin/dev。要看的是**非 merge 内容提交在不在远端**，不是 ahead 数字。
- **本地 qa 领先 origin/qa 35 个**：那 31 个内容提交全已在 `origin/dev_festival`（qa 只是把 dev_festival 合进来没 push），删本地 qa 零损失。判据永远是"内容在不在远端"。
- **非 git 残留目录**：`git worktree list` 不列、但磁盘上有（如曾出现的 `gdconfig-qa-m3`，`.git` 都没有）→ 直接 `rm -rf`。

## 删除命令模板

```bash
cd /c/X3/gdconfig
git worktree remove /c/X3/gdconfig-<name>     # 干净才成功；有改动加 --force(慎)
git branch -D <branch>                         # 顺手删本地 ref（远端不受影响）
rm -rf /c/X3/<非git残留目录>
```

跟 [[workflow_x3_multiagent_worktree]]（多 agent 并发用 worktree）配套：那篇讲怎么开，这篇讲怎么收。
