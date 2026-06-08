---
name: ""
description: git stash/pull/rebase/push 等常规可逆操作直接执行，别当高风险决策找用户确认
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a541a2f5-c8ab-4e7e-b8b5-3ea2868f77b8
---

**常规、可逆的操作直接做完，不要停下来找用户确认**——否则就是"墨迹/变笨"。

**典型反例(本次踩的)**：x2client 我自己的提交已就位，只有一批**无关的未跟踪文件**挡住 pull。标准做法就是 `git stash -u → pull --rebase → push → stash pop`，全程可逆。我却把它当"要不要动别人文件"的高风险决策去问用户，被批"墨迹/变笨了"。

**判断线**：
- **可逆 / 标准套路 / 只动我自己或临时产物**（stash、pull --rebase、push 自己的分支、清自己的临时文件、重命名/移动自己的中间件）→ **直接做**。
- **真正要确认的**：不可逆破坏（硬删用户文件、force push、reset --hard 丢他人提交）、改共享真源、对外发布。
- 别把"理论上可能有风险"当借口在常规操作上反复请示。stash 能 pop、commit 能 revert、本地操作能回滚——这些都算可逆。

见 [[feedback_temp_file_auto_cleanup]]（同源问题：该自己利落做的事别反复问）。
