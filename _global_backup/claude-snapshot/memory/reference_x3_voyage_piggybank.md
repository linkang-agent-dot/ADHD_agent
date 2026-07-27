---
name: reference-x3-voyage-piggybank
description: X3 大富翁(Voyage)存钱罐实现机制+复购化(加档$49.99/$99.99+UTC0日刷)评估结论；动这个模块先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4cf1282b-7643-418f-9527-24446c5a16c2
  modified: 2026-07-27T03:50:21.185Z
---

# X3 大富翁（Voyage）存钱罐 · 机制与复购化评估（2026-07-27 勘探）

⚠️ 与异国美酒储蓄罐（Gift/PiggyBank 表系统，[[project-x3-piggybank-hud]]）是**两套系统**，别混。

## 现状机制（代码核实）
- **配置**：`ActvVoyage` 表三字段 = `PiggyBankPackID`（单档，只有一个）/ `PiggyBankTriggerStep` / `PiggyBankNeedCount`。
- **服务端** `server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.Voyage.cs`（~:536）：走步出指定点数 → `voyageData.piggyBankCount++`，**只累计不拦截、不设 bought、购买不消耗 count**；购买判定全在客户端。
- **购买** = 普通 Pack 走 gift 系统；限购靠 `Pack.BuyCount` vs `giftInfo.purchaseNum`（客户端 `ActivityMeta.Voyage.cs CheckCanShowVoyagePiggyBankRedPoint` :92-128）。现状单档 $19.99 单笔买断。
- **UI**：`UI\Actv\UIActvVoyage.cs`（存钱罐段 ~:956）。

## 复购化需求评估（8-10月需求点4：加 $49.99/$99.99 档 + 各档 UTC0 日刷复购）
**结论=能搞，3-5 人天**（配置 0.5-1 / CSShared 日重置泛化 0.5 / 客户端多档 UI+红点 1-2 / 测试 1；服务端计数逻辑不分档=零改）。
- 多档 = ActvVoyage 加字段 + Pack 克隆新档（各档独立 Group，抄美酒双档先例）。
- UTC0 日刷 = 泛化 MR!718「购买时间戳取整到 UTC 当日 0 点」机制（现只对 ResourceID 7002 生效，改成按 Group/标记字段触发），一处改三层口径自动对齐。
- ⚠️ **排期硬约束**：取整改动在 CSShared → GameServer 主程序集，**必须随服务端完整发版，禁只热更 Hotfix**（美酒罐 MR!718 已踩实）→ 需求要挂正式版本（0.3x）。
- **✅UI 已拍板（2026-07-27 用户）**：单卡自动切档 + **手动切档按钮**（循环切三档，可跳看/买任意档）。自动切规则默认=显示第一个今日未买档（美酒罐同款）；已买档显示该档 UTC0 倒计时。
- 余 1 点待拍：储蓄进度三档共用（现状天然成立·已按此实现）vs 各档独立阈值（要再加配置字段）。

## ✅代码已落地（2026-07-27，x3-project `feature/voyage-piggybank-tiers` 已push，commit `bfe6718bb2f`）
- worktree=`C:\x3-wt-piggybank`（sparse：server+Scripts+Protobuf+依赖4路径+scripts+.githooks；junction 20条已建）。基于 origin/dev_festival。
- 6文件+307行：①CfgProto ActvVoyage 加 `PiggyBankPackID2/3`（字段13/14=tag104/112，手写照生成物样式）②新建 CSShared `VoyagePiggyBankPacks`（DataModel命名空间；从CActvVoyage收集档位礼包ID，Cache按Instance引用失效防热重载stale；RoundToUtcDayStart）③`GiftData.ChangeGiftBuyInfo` 购买时间戳对存钱罐档取整UTC0（MR!718机制泛化，注意 **dev_festival 上没有 MR!718 原实现**——美酒那套在此分支仍是三层特例，将来 dev 合入时 ChangeGiftBuyInfo 会撞小冲突，union即可）④客户端 ActivityMeta.Voyage 红点改"任一档可买"+`IsVoyagePiggyTierBuyable`/`GetVoyagePiggyTierCdEndTime` ⑤UIMonopolyPigBanck 自动选档+切档按钮+CD倒计时（`BtnSwitchTier`/`TxtTierCd` 节点缺省兼容=退化单档现状）。
- **验证状态**：dotnet 三 Hotfix 0错误✅；客户端 Unity 编译**未验**（客户端文件 dotnet 不碰）；端到端未测。
- **待做**：①gdconfig 配置（ActvVoyage 加两列+TableProtoGen 重生成；新档 Pack 克隆=价格$49.99/$99.99+各档独立Group+ColdTime24h+BuyCount清空；**现有档280001/280003 也要同改** BuyCount1→空+ColdTime+Group；现状 Pack=PackType16/Price111/限购1/无CD无组）②新档产出数值待策划 ③prefab 拼 BtnSwitchTier+TxtTierCd ④本地服+GM推时间端到端 ⑤验完合回 dev_festival（非保护，自助合并）。
- sparse worktree 踩坑复证：.githooks 被截断（checkout --还原）；pre-commit 要 scripts/ 在 cone（报"未找到 check_video_assets.py"→sparse add scripts 即过）。
