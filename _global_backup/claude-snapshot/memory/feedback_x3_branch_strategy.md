---
name: x3-branch-strategy
description: X3 配置改动直接在当前活跃分支上做，不要每个改动新建专属分支
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 22c25965-252c-40fd-9575-d6ee02470233
---

## 规则

X3 gdconfig 仓库的所有配置改动（不论节日优化、累充改造、活动调整等），都**直接 commit + push 到当前活跃开发分支**（通常是 `dev-summer-love-song` 或类似的当期分支）。

**不要**自作主张为某项功能或改动新建专属分支（如 `dev_nile_optimization_v1`）。

**Why:** 2026-05-25 尼罗优化时我建了 `dev_nile_optimization_v1` 想隔离改动，用户反应"这是啥分支啊...你建的吗"，让我"重传一遍到夏日分支"。X3 团队习惯所有改动汇在当期活跃分支上批量导表 + 回归，新建小分支反而增加 jolt 触发次数、MR 管理成本，且让回归曲线不连续。

**How to apply:**
- 改 X3 配置前先 `git branch --show-current` 确认在哪
- 如果当前在 `master` 或非活跃分支，问用户该切哪个，不要默认新建
- 如果当前已经在活跃分支（如 `dev-summer-love-song`），直接改 + commit + push 在该分支上
- 只在用户明确要求"新建分支"时才新建
