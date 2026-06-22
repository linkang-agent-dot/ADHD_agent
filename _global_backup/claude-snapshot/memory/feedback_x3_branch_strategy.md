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

## ⚠️ dev 与 dev_festival 严重分叉（2026-06-18 实测，切分支前必看）
两个 X3 仓的 `dev` 和 `dev_festival` **不是"dev+节日"的关系，是两条大幅分叉的线**：
- x3-project：`dev_festival` 相对 `origin/dev` = **领先163 / 落后907 提交、4106 文件差异**。切到 dev 基底 = 巨量 checkout + 拉 LFS，且会把节日已提交代码在工作树里还原成 dev 版。
- gdconfig 同理分叉（但储蓄罐相关表 Pack500031/PiggyBank行46/Item7002 两条线上内容恰好一致，ID 空号也一致——属巧合，**别假设两条线配置相同**，切分支后必重核 ID/文件）。
- 所以"切到 dev"≠"切到当期节日线"。节日批次活动默认该待在 dev_festival；用户说"dev"时**确认是字面 dev 还是泛指当期线**。
- 本案(异国美酒每日双档)：用户**明确要 dev 基底单独分支**(`X3NEW-wine-piggy-daily-dual`)，已照做并在 dev 上重核 ID/客户端文件通过（与 dev_festival 一致）。

## ⚠️ 改文件的脚本"试跑"必须确认路径真被改到临时目录（2026-06-18 踩坑）
拿 sed 改脚本里硬编码的 `TSV_DIR` 想跑临时副本时，**Windows 路径反斜杠在 sed 里转义易失败→替换没生效→脚本实际跑在真仓库上**（本案 apply 脚本就这样把 3 张 tsv 误改进真 gdconfig）。教训：跑会写文件的脚本前，先 `echo`/`grep` 确认替换后的路径**真的指向临时目录**再执行；或脚本直接支持 `--dir` 入参，别靠 sed 改源码。
