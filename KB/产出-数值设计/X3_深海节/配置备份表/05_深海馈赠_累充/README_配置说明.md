---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 05 深海馈赠（累充）— 配置备份表

> KB 配置备份，非 live tsv。**复用换奖励·无程序**。分支 dev_festival。
> 复用源 = **世界杯累充 100597**（ActvType5，用户同意按世界杯当模板）。

## ID（已扫·free）
节日累充块（1005xx-1006xx），世界杯=100597/CID597 → 深海 **AO `100598` / CID `598`**（均已验证 free ✅，与 memory ID 表一致）。

## 表清单
| 表 | 新增 | 文件 | 模板 | 状态 |
|---|---|---|---|---|
| `ActvOnline__ActvOnline.tsv` | **100598**(CID598) | `ActvOnline_新增100598.tsv` | 100597 世界杯累充 | ✅骨架 |
| 累充档位奖励（ActvTask TaskType902 等） | 待补 | — | — | ⛔数值待复盘 |

## 累充机制（见 [[reference_x3_recharge_isolation]]）
ActvType5 累充 = `ActvRechargePoints=1` + **`RechargePointPackWhitelist`（哪些 Pack 的充值计入本累充）** + ActvTask(TaskType902，各档 Parameter1=累充门槛) 三表协同。

## 关键改动（vs 100597 模板）
- ID 100598 / ContentID 598 / TC **1830** / GroupId 140 / 列1 26深海节-累充 / ActvName=深海馈赠。
- ActvImg+ActvIcon=深海 DK（**美术第一批已出累充背景**：`05_深海馈赠_累充\累充活动背景_选定.png`，沉船宝藏+潜艇，待入库）。
- **RechargePointPackWhitelist=【待补】**：世界杯白名单是 211002-211015+894xxx；深海要换成**深海节 Pack 块白名单**（211016-211020 等深海礼包 + 通用 894xxx 累充包段）→ 落地时按深海实际 Pack 列。

## ⛔ 待补（数值待复盘）
1. **10 档累充档位 + 各档奖励**（gacha 道具 $0.5/个 ROI50%）→ **数值待夏日复盘**（总览定调）。配在 ActvTask(TaskType902，各档 Parameter1 门槛) + 对应 Reward。
2. ✅**【已定·用户拍板 2026-06-22】05 累充顶档只投「抽奖道具」**（深海罗盘券 **1150**，大量发放）——**不投潜艇皮**。潜艇皮 Item15065 归 **01 转盘核心大奖独占**，两边不再重复。各档奖励仍以 gacha 抽奖道具(1150)为主 + 养成料，具体档位数值待夏日复盘。
3. 航迹皮肤（第4档$200外显）ID 待确认。
4. RechargePointPackWhitelist 深海 Pack 列表（依赖深海各礼包 Pack ID 落定）。
5. TopResource(1146 世界杯券) → 深海代币 or 复用。
6. ActvRule(15013) / 名字 → i18n。

## 落地顺序
夏日复盘定档位数值 → 深海 Pack 块定 → 填白名单 + ActvTask 档位 + Reward → 美术 DK 入库 → 插 ActvOnline 100598 → i18n → 过 gate → commit → 导表。
**配置先备份·分支后续与深海节一起合并。**

_生成 2026-06-22；dev_festival。骨架按世界杯模板；档位数值待复盘；✅顶档已定=只投抽奖道具(深海罗盘券1150)·潜艇皮归01转盘独占。_
