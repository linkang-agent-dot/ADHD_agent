---
name: x3-actvtype
description: X3 ActvOnline.ActvType 数字→玩法的权威定义位置，及世界杯/周卡重编号(64→71/63→70)踩坑
metadata: 
  node_type: memory
  type: reference
  originSessionId: 33fe5727-08d6-48d3-80a0-91952eddfd74
---

## 权威枚举位置（查 ActvType 数字含义先看这里）

`C:\x3-project\client\Assets\Scripts\CSShared\Common\Const\ActivityConst.cs`（client/server 共享，CSShared）。
**别信 server 端 handler 文件里的注释**——如 `ActivityMeta.WeeklyCard.cs` 顶部写「自选周卡 ActvType=63」是**过时残留**，真值见上面 const。

部分关键值（节日付费类）：
| ActvType | const | 玩法 |
|---|---|---|
| 60 | MECHA_WHEEL | 双圈机甲转盘 |
| 61 | NEW_QUEUE | 新兵排队充值 |
| 63 | CHAIN_PACK | 链式礼包（阶梯礼包，如装饰阶梯礼包 106101/106103） |
| **64** | **CHOICE_GIFT_PACK** | **三选一礼包**（读 `ActvPack.PackList`） |
| 65 | COIN_PUSHER | 推币机 |
| 67 | RED_PACK | 联盟红包 |
| 70 | WEEKLY_CARD | 活动自选周卡 |
| 71 | WORLD_CUP_GUESS | 世界杯竞猜（二选一助威礼包，**不读 ActvPack.PackList，改用 iGame customParam 两礼包池**） |

## ⚠️ 重编号踩坑（2026-06-22 zhangli commit 2c516fe）

世界杯竞猜开发期**借用 64（三选一礼包）号**，专用代码(X3NEW-1432)落地后 zhangli 把竞猜行批量 **64→71**、周卡 **63→70**。
- 坑：这次 batch **误把真三选一礼包 109002 一起 64→71**，导致它挂在世界杯竞猜 type 上、服务端无视它配的 ActvPack(PackList=2025003-006)→活动坏。正确值应留 **64**。
- 判 type 对错的硬法：① `ActvPack` 有 PackList = 走 64(三选一)，不是 71(竞猜)；② 看 71 桶里有没有名字/描述不是「竞猜」的行(那就是被误扫的)；③ 64 桶空 = 三选一被搬空的信号。
- 注：63/64/70/71 在重编号前后语义不同，看历史版本的「64」要先确认是哪个时间点的号。

**How to apply:** 查 X3 某活动 ActvType 该填几，先读 `ActivityConst.cs`(client CSShared) 拿数字↔玩法，别用 server handler 注释；遇到世界杯/周卡相关 type 警惕 64↔71、63↔70 的重编号历史。详见 [[reference_x3_config]]。
