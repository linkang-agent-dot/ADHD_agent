---
name: feedback-continue-agent-use-sendmessage
description: 给正在后台跑的 agent 追加/修改范围，用 SendMessage(to=agentId)，别用 Agent 工具（会起新 agent 撞车）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3207bccb-3ad7-4461-b28a-0397e71ef12e
---

给一个**已经在后台跑的** subagent 追加范围、改指令、纠正方向时，**用 `SendMessage(to=<agentId>)`**（agentId 形如 `a4a18c7fb546e1bb8`，来自 spawn 结果），消息会排队到它下个工具轮次送达、上下文不丢。

**踩坑（2026-07-02 X3 i18n 补 key 实操）**：想给在跑的 fix agent 追加 3 个字段的补建范围，误用了 **Agent 工具**（subagent_type=general-purpose）——结果**新起了一个独立 agent**，它会自己开 worktree、往同一分支(dev)推同一张 Text 表 → 跟原 agent 撞车（双改/双推/双 jolt）。发现后立即 `TaskStop` 杀掉新 agent（幸好刚起没建 worktree、无残留），再改用 `SendMessage` 发给原 agent 才对。

**判据**：
- 要**继续/追加/纠正**一个已存在的 agent（保留它的上下文和在途工作）→ `SendMessage(to=agentId, message=...)`。
- 要**全新起一个**独立任务的 agent → `Agent` 工具。
- 别把"给某 agent 补充说明"当成"再派个 agent 做补充部分"——后者在多 agent 同仓/同分支/同文件场景会静默撞车。

**Why**：Agent 工具永远 spawn 新 agent；它不认 agentId、不会"续上"某个在跑的 agent。SendMessage 才是"对现有 agent 说话"的通道（`to` 可用 agentId 续已完成/在跑的 agent，或 teammate 名）。

相关：[[reference_x3_multiagent_worktree]]（多 agent 同仓用 worktree 隔离，正是"撞车"要防的场景）。
