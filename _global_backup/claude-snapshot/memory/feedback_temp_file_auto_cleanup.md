---
name: ""
description: 我本次任务造的中间/临时文件，做完默认直接清理，不列清单问用户
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a541a2f5-c8ab-4e7e-b8b5-3ea2868f77b8
---

任务做完后，**我自己在过程中产生的中间/临时产物**（一次性脚本、中间图 white/black/alpha-check、分析用 json 等），**默认直接删除，不要列「保留/删除」清单去问用户**。清错了用户会主动反馈。

**Why:** 用户嫌每次清理前都问很啰嗦（"别乱问了"）。

**How to apply:**
- 区别于 CLAUDE.md「删文件/清理中间产物前先列清单确认」——那条针对**用户的/已有的非临时文件**；**我自己造的 session 临时产物**默认清，无需确认。
- 保留：最终交付物（成品图、配置、记录性 json 如 DK→GUID 映射）。删除：纯过程中间件。
- 见 [[feedback_cleanup_checklist_first]]（旧规则，已被本条对"自产临时文件"细化覆盖）。
