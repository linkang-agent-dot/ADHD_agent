---
name: workflow-x3-feature-wipe
description: X3 整体撤除一个功能(代码+prefab全清)的手法——index-only revert + 生成代码结构化摘块，唯一入口=KB\方法论\活动程序开发\X3_功能整体撤除手法_代码prefab全清.md
metadata: 
  node_type: memory
  type: project
  originSessionId: b54fc303-b33c-4132-a6ab-f5d147cb6b06
  modified: 2026-07-28T14:46:14.101Z
---

# X3 功能整体撤除（推倒重做 / 砍功能）先读这个

**唯一入口**：`C:\ADHD_agent\KB\方法论\活动程序开发\X3_功能整体撤除手法_代码prefab全清.md`
**可复用脚本**：同目录 `tools\feature_strip.py`（结构化摘除生成代码里某功能的全部痕迹，自带零残留 + 大括号配平双校验）

四条最容易翻车的：

1. **开工前必问三件事**：配置仓要不要一起清（不清 → 下次导表 proto/bytes/CfgProtos 自己长回来，必须提前讲明白，否则被当成漏清）/ 清到哪条分支（功能 commit 常已在 origin/dev）/ feature 分支和 worktree 留不留。
2. **别在主仓工作区干**。X3 主仓基本永远是脏的（别的会话在途）。走 **index-only revert**：`GIT_INDEX_FILE` 临时 index + `read-tree` + `apply --cached` + `write-tree`/`commit-tree`/`push`，不落工作区、不额外 checkout 十几个 G，**且不要动本地分支 ref**（一移用户满屏红）。
3. **补丁回退要逐文件不逐 commit**（`git apply` 整份原子生效，一个文件挂会连环崩），用 `-C1` 放宽上下文、别用 `--3way`。**生成代码永远打不上补丁**——合并 dev 后跑过 proto/DK 重生成会重排+让号（本次 flashSaleData 67→70），这批必须结构摘块：两份 `Protos/activity.cs`、`activity.proto`、`msgid.def`、ActivityConst/MetaConst/ErrCode/SysOpReason/TEventType。
4. **push 后必须复核真实父提交**（`git log --format="%H %P"` + 对真实父提交再 diff 一次）。X3 主仓常有别的会话同时推，`old..new` 里的 old 可能不是你 fetch 时那个；只看"推成功了"不够。

首个案例 = [[project_x3_flashsale_reskin]]（2026-07-28 马戏节限时抢购，清除提交 973997a92ce，120 文件 19.7 万行纯删除零新增）。
关联 [[workflow_x3_merge_conflict_audit]] · [[reference_x3_new_actvtype_playbook]] · [[workflow_x3_multiagent_worktree]]
