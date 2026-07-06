---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 08 许愿池 — 配置备份表

> KB 配置备份（一个功能一个文件夹），非 live tsv。**纯配置·无程序·仅换背景**（玩法/数值/名字全不变）。
> 分支 = **dev_festival**（已确认）。

## ⚠️ 模板修正（重要·避坑）
memory ID 表里写的「夏日模板 ID」有部分**已被世界杯活动原地覆盖**（如 100597/102240 现在是世界杯累充/BP，不是夏日）。
**正确做法 = 在 dev_festival 按 ActvType 取「最近的同类节日行」当模板**，新 ID = 该 ActvType 现存 max+1。
- 许愿池(ActvType50)现存：105009 星愿之池 / 105010-105012 许愿池 → **模板取 105012（26春节许愿池）**，新 = **105013**(max+1) ✅与 ID 表一致。

## 这个是什么
ActvType=50 全服共建许愿池。$4.99 可重复抽，连抽赠礼。**玩法/数值/名字全不变，仅换深海背景图**（总览定调）。

## 表清单
| 表 | 新增 | 文件 | 模板 |
|---|---|---|---|
| `ActvOnline__ActvOnline.tsv` | **105013**（ContentID 5013） | `ActvOnline_新增105013.tsv` | 105012 春节许愿池 |
| `ActvWishingPool__ActvWishingPool.tsv` | **5013** | `ActvWishingPool_新增5013.tsv` | 5012 |

## 链路（怎么串）
`ActvOnline 105013`(ContentID=5013, ActvType=50) → `ActvWishingPool 5013`(同 ContentID 索引) → 奖励组 **RewardGroup=105 + RewardGroup2=103**（**全复用 5012，不新增奖励行**，玩法数值不变）。

## 关键改动（vs 5012 模板）
| 字段 | 5012 模板 | 深海 5013 | 说明 |
|---|---|---|---|
| ContentID | 5012 | **5013** | max+1 |
| TimeController | 1515 | **1830** | 深海主 TC |
| GroupId | 136 | **140** | 深海活动组 |
| ActvImg（全屏背景） | DK_img_Activity_CNY_bg_14 | **DK_img_Activity_deepsea_wishingpool_bg** | ⚠️待入库（深海背景） |
| ActvIcon（HUD入口） | DK_img_Activity_CNY_icon_8 | **DK_img_Activity_deepsea_wishingpool_icon** | ⚠️待入库 |
| WishingPool.DK_PoolImg（水池图） | DK_img_Activity_CNY_bg_17 | **DK_img_Activity_deepsea_wishingpool_pool** | ⚠️待入库 |
| RewardGroup / RewardGroup2 / PackID / Numble | 105 / 103 / 1002001 / 6 | **全复用不变** | 玩法数值不动 |

## ⚠️ 待补
1. **深海许愿池背景美术未出**（memory 标「第一批漏了」）→ 需出：全屏背景 + 水池图（水底光柱+漂浮许愿币/贝壳/珍珠·明亮青绿）。出后 DK 入库填上面 3 个 DK 名。
2. ActvRule（规则文案 16026 春节）→ 复用 or 深海版，i18n 时定。
3. ActvName/Desc 已改深海描述（"在深海许愿池许下心愿…"）→ i18n 扫描生成 TXT。
4. TopResource（许愿币 1138|1139|1140 春节）→ 确认深海许愿池用同货币 or 深海代币（"数值不变"倾向复用，待确认）。

## 落地顺序
深海背景美术出 → DK 入库(3个) → 插 ActvOnline 105013 + WishingPool 5013 → i18n → xlsx+tsv 一致过 gate → commit → 导表。
**配置先备份·分支后续与深海节其余模块一起合并。**

_生成 2026-06-22；分支 dev_festival。纯配置仅换背景，骨架已配，只待背景美术 + DK 入库。_
