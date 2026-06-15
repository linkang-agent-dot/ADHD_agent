---
name: feedback-surface-problems-not-thrash
description: 遇到工具异常/自己不确定立刻一句话反馈用户，别手搓一次性脚本、别混用工具输出硬怼；改配置走现成 skill 不自己硬干
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9b18c7d9-d21a-45bf-902a-6bff0eec2a0f
---

2026-06-09 X2-43094 限时抢购抽奖券 bug：自己上手改配置把活动改崩（抽不了奖），之后又一路越查越乱、反复手搓脚本卡在工具机制上，被用户批"太夸张了 / 有问题不反馈、净搞工具问题阻塞"。

**三个自造的"工具问题"（工具本身没坑，全是我用拧了）：**
1. 拿 `gsheet_query` 输出的 "row N"（它的内部序号，比真实表格行号少 1）去拼 A1 地址给 `gsheet_utils.update_range` 写 → 写到邻行、差点改坏 `212101145`。**定位/写都按 ID 走，写前先 `get_values` 核对 B 列 id**（技术细节见 [[x2-config-library]] 的 gsheet_query 行号偏移条）。
2. `gsheet_query` 输出本就干净无乱码，却再套自己手写的 python 解析 + `errors='replace'` → 造出代理字符 `\udcxx` 崩溃、后台任务空输出。**直接用工具原样输出，别再加一层手搓解析。**
3. 改换皮配置（限时抢购累计道具）**没走现成 `p2-x2-reskin` + `x2-config-download` skill**，自己改 GSheet + 手搓 merge 脚本 → 只改了机制组件没改发道具的礼包 → 抽奖闭环断了改崩。

**Why:** 现成 skill/工具够用且验证过；手搓一次性脚本、混用工具输出、跳过 skill 流程，是自造问题的根源；遇到不确定不反馈、闷头连发工具调用硬怼，会把进度全卡住还可能改坏线上（本次直接把抽奖改崩）。

**How to apply:**
① 改配置类任务先认现成 skill（换皮=p2-x2-reskin、导表=x2-config-download、写回=x2-gsheet.mdc 规矩），按流程走，别自己硬干、别手搓一次性脚本（复用 gsheet_utils 等现成工具，见 [[feedback-sheet-edit-review-efficiency]]）。
② 一碰到「工具行为异常 / 我自己不确定」（行号对不上、乱码、活动机制没搞懂、改完没生效、后台不出结果），**立刻停下来用一句话告诉用户**，别连续多次工具调用去硬怼工具机制。
③ 改完发现"调用成功但结果不对"，先怀疑自己用法 / 先停下反馈，不要立刻深挖工具内部、不要越改越多。
④ 可逆操作可直接做（见 [[feedback-decisive-on-reversible-ops]]），但「改崩了/不确定根因」属于该停下反馈的情形，不是该硬冲的情形。
