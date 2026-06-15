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

**典型反例2（2026-06-10）**：修拓荒行军表情本地化，改完 i18n GSheet 就停下问「要不要导表 / 要不要重建 skill 索引」，被「开干啊，这种不用问我」。**修复/配置任务的标准收尾步骤=任务本身**：改 X2 GSheet→直接 `fwcli` 导表+push（真源=GSheet，不导不进游戏）；改 X3 tsv→直接 push+触发 jolt（见 [[workflow_x3_auto_jolt_export]]）；修复中发现工具缓存坏→顺手重建（如 x2-localization 的 `scan_all_keys.py`/`build_translation_memory.py`），别只报「坏了」。用户视角「修好」=改动可验进游戏，不是「GSheet 改完」。**收尾≠外发**：仍要先商量的是面向外部/难回退的（部署上线、邮件文案定稿、删用户内容）。收尾照做但**做完必端到端验证+如实报结果**（导表 SUCCESS/FAILURE、commit、复查实际值）。

**判断线**：
- **可逆 / 标准套路 / 只动我自己或临时产物 / 让本次改动生效的收尾**（stash、pull --rebase、push 自己的分支、清自己的临时文件、导表让配置生效、重建工具缓存）→ **直接做**。
- **真正要确认的**：不可逆破坏（硬删用户文件、force push、reset --hard 丢他人提交）、改共享真源、对外发布。
- 别把"理论上可能有风险"当借口在常规操作上反复请示。stash 能 pop、commit 能 revert、本地操作能回滚——这些都算可逆。

见 [[feedback_temp_file_auto_cleanup]]（同源问题：该自己利落做的事别反复问）。
