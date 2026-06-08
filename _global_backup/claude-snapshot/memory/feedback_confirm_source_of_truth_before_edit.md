---
name: ""
description: "动手改任何配置前，先确认这张表的\"真源 + 改动进游戏的管线方向\"，再决定改哪里；改完验\"做到了\"不只验\"做了\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6565b844-cec5-4422-8f6c-2bcaa630fe94
---

改任何项目的配置前，**先回答两个问题再动手**：① 这张表的**真源**是什么？② 我的改动通过什么**管线**进游戏（方向是哪边流向哪边）？确认完再决定改哪里。

各项目配置管线**根本不同，不能跨项目想当然**：
- **X3**：真源 = `tsv`（导表已迁 tsv 缓存，直接改 tsv 不碰 xlsx）。见 [[reference_x3_tsv_export_migration]]
- **X2 / P2**：真源 = **GoogleSheet**，`GSheet → 导表 → 本地 tsv`。tsv 是**下游产物**，直接改会被下次导表覆盖（白干）。改 X2 配置必须写 QA GSheet，SheetID 用 `gsheet_query.py resolve <表号>` 现解。见 [[reference_x2_config_library]]

**Why**：2026-06-04 修 X2 拓荒节 BP 排行榜文案/获取途径时，我把 X3"直接改 tsv"的肌肉记忆套到了 X2，又被"dev_festival 最近提交都是改 tsv"这个弱信号带偏，直接改了 `x2gdconf/fo/config/*.tsv`。错有两层，根子同一个：
1. **方式错**：没确认 X2 真源就开干。把"数据物理躺在仓里 tsv"当成"该改 tsv"，忽略了管线方向（X2 从 GSheet 流向 tsv）。讽刺的是 `x2-gsheet.mdc`（同会话已读）白纸黑字写过"必须写回 QA GSheet"，答案在上下文里仍被习惯盖过。
2. **没 double-check**：把"Edit 返回成功"当成"改动会生效"——机械成功 ≠ 落地有效。漏掉了 CLAUDE.md"端到端反查 GSheet+TSV+分支三层"里的 GSheet 层（恰是没碰的那层）。全靠用户发现才纠正。

**How to apply**：
- 动手前一句话自检：「这表真源是 ___，我的改动走 ___ 路径进游戏，所以我该改 ___」。答不上来就先查，别凭别项目习惯或"最近提交碰了啥"推断。
- 改完别只看工具回成功，反查"这条改动到目标了吗"——尤其真源在 GSheet 时，必须确认 GSheet 已写、再导表，而不是只动 tsv。
- 弱信号（别项目习惯、最近 commit 碰的文件）≠ 强确认（真源/管线方向）。冲突时以强确认为准。
- 同源病：用户已指明答案/路径时，先信任落地，别过度自证绕路（这次还跑去翻客户端代码）。

**强制落地点（不靠本 memory 召回）**：已写进 quality-gate `config-checklist.md` 的 block 规则「改对地方(真源)」——task-checker 跑 type=config 验收时确定性检测「X2/P2 手改了 x2gdconf tsv 而没写 GSheet」并拦收工。**前提**：开 X2 配置工作时建的 pending_verify marker 要带 `project:x2`（type=config），否则 gate 不路由这条。详见 [[quality-gate]]。

关联：[[feedback_verification_end_to_end]]（三层反查）、[[feedback_config_chain_first]]（先追引用链）
