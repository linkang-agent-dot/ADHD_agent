---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 深海节 · 09 最佳酒馆 — 配置备份表

> KB 配置备份，非 live tsv。**纯配置·无程序·仅换背景**（玩法/数值/榜单全不变）。分支 dev_festival。
> 复用源 = **10071702 为爱干杯**（情人节酒馆，ActvType7）。

## 这个是什么
ActvType=7 跨服酒馆赛事（最佳酒馆系列）。积分冲榜 + 世界级排名奖。**仅换深海背景**，玩法/数值/积分/榜单全沿用。

## 关键发现：最佳酒馆系列共享一套逻辑
最佳酒馆系列（10071701 启程补给站 / 10071702 为爱干杯 / 10071703 千灯贺新岁）**全部 ContentID=717 + RankID=131 共享**——积分(ActvScore)、排行、奖励是一整套，各节日只新增一条 ActvOnline 换 TC + 背景 + GroupId。
→ 深海酒馆 = **只加 1 条 ActvOnline 10071704**（系列 max 10071703 + 1），**ActvScore / 排行 / 奖励一律不碰**。
（⚠️ 注意区分：10071801 蓝莲花宴是 ContentID=718 的**另一套**积分游戏，不是最佳酒馆系列。这就是 [[reference_x3_score_activity]] 说的「ScoreID 易混淆·落地点名具体 ContentID」——本模块明确 **ContentID=717**。）

## 表清单
| 表 | 新增 | 文件 | 模板 |
|---|---|---|---|
| `ActvOnline__ActvOnline.tsv` | **10071704**（ContentID **717 复用**） | `ActvOnline_新增10071704.tsv` | 10071702 |
| ActvScore 全套 | **不新增**（CID717 共享） | — | — |

## 关键改动（vs 10071702 模板）
| 字段 | 10071702 | 深海 10071704 | 说明 |
|---|---|---|---|
| ID | 10071702 | **10071704** | 系列 max+1 |
| ContentID | 717 | **717（不变）** | 共享积分逻辑 |
| RankID | 131 | **131（不变）** | 共享跨服榜单 |
| TimeController | 1514 | **1830** | 深海主 TC |
| GroupId | 138 | **140** | 深海活动组 |
| ActvImg（背景） | DK_img_Activity_VD_bg_12 | **DK_img_Activity_deepsea_tavern_bg** | ⚠️待入库（**美术第一批已出**：`09_最佳酒馆\最佳酒馆背景_选定.png`，远航酒馆内景·无人物） |
| ActvIcon（HUD入口） | DK_img_Activity_VD_icon_6 | **DK_img_Activity_deepsea_tavern_icon** | ⚠️待入库 |
| ActvName/Desc | 为爱干杯 | 远航酒馆（深海版） | i18n 扫描生成 TXT |

## ⚠️ 待补
1. 背景 DK 入库（背景图已出，裁尺寸+入库填 ActvImg）；HUD icon 待出+入库。
2. TopResource（1134|1135 情人节代币）→ 确认深海是否换深海代币 or 复用（"数值不变"倾向复用，待确认）。
3. ActvRule（1015）/ ActvName-Desc → i18n。

## 落地顺序
背景图裁尺寸 + DK 入库 → 插 1 条 ActvOnline 10071704 → i18n → 过 gate → commit → 导表。
**配置先备份·分支后续与深海节一起合并。**

_生成 2026-06-22；dev_festival。最简模块：一条 ActvOnline 行，CID717/RankID131 全复用。_
