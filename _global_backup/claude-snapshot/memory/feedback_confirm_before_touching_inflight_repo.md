---
name: feedback-confirm-before-touching-inflight-repo
description: 仓库里有未推送提交/WIP时，merge/rebase/pull前先把在途清单摊给用户确认处理方式，不要自行开搞
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dd8529f5-e28c-4a9f-b119-d3347299de36
---

对**有在途工作的仓库**（未推送提交、stash、脏工作区）执行 merge / rebase / pull / reset 前，先列清单（哪些提交、哪些 WIP、各自会怎样）给用户确认处理方案，确认后再动。

**Why:** 2026-06-12 帮用户 pull x3-project client 时，本地有 11 个未推送的世界杯竞猜提交+WIP prefab，我 stash 完直接就 merge，被用户打断："现在已有在推送状态的东西，需要先跟我确认再处理"。在途提交是用户的工作资产，怎么合、何时推由用户决定。

**How to apply:** ① `git log origin/x..x --oneline` + `git stash list` + `git status -s` 三件套摊现状；② 给出方案（合不合/推不推/谁先谁后）等确认；③ 执行时明确承诺"不 push"之类的边界并遵守。授权范围精确对齐，同 [[feedback_ask_before_modifying_user_content]]。

**反向坑（2026-06-12 同日实测）：并行 Claude 会话会把"我"的未提交改动当无关 WIP 暂存掉**。症状=改完没提交的文件突然"working tree clean"+ 内容回到旧版、自己的 check 全绿（其实跑在被还原的文件上=假干净）。第一反应查 `git stash list`（对方通常起名"WIP-xx(非本次)"），用 `git checkout 'stash@{n}' -- <我的文件>` 只取回自己的文件，别 pop 整个 stash（里面混着对方已另行提交的行，pop 会撞）。预防：同仓多会话并行时，改完尽快 commit（哪怕分两笔），别让改动裸奔在工作区。
