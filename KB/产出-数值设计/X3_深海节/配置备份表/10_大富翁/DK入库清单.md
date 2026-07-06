---
tags: [kind/产出, domain/配置换皮, proj/X3, fest/深海节, year/2026]
---

# 大富翁 新 DK 入库清单（新建一套·全新 DK 名）

> 新活动(ContentID 2803)用**全新 DK 名**注册到深海正式版 png，**不覆盖原航海之路 DK**（原 2801 保持不变）。
> DK 名为建议，实际入库时定；入库后填进对应 tsv 字段。
> 正式版根：`KB\产出-本地化与美术\X3\深海节\10_大富翁\_FINAL_正式版\`

| # | 建议新 DK 名 | 指向 png（正式版） | 填进配置字段 | 尺寸 | 状态 |
|---|---|---|---|---|---|
| 1 | DK_img_Activity_Monopoly_deepsea_bg | 00_地图_深海_540x960 | ActvOnline 102803.ActvImg | 540×960 | ✅出 |
| 2 | DK_img_island_deepsea_start | 01_岛_起始_潜艇基地 | Event EG199(起始).DKImg | 184×224 | ✅出 |
| 3 | DK_img_island_deepsea_diamond | 02_岛_钻石_蓝水晶(复用island_2_lv5) | Event EG200(钻石) Lv1.DKImg | 184×224 | ✅复用图 |
| 4 | DK_img_island_deepsea_treasure | 03_岛_宝藏_代币 | Event EG204/205(宝藏).DKImg | 184×224 | ✅出 |
| 5 | DK_img_island_deepsea_mystery | 04_岛_神秘_珊瑚问号 | Event EG206(神秘).DKImg | 184×224 | ✅出 |
| 6 | DK_img_island_deepsea_lucky | 05_岛_幸运_珊瑚宝箱 | Event EG201/202/203(幸运).DKImg | 184×224 | ✅出 |
| 7 | DK_icon_deepsea_coin | 06_代币_深海代币 | Item 1202.DK_图标 | 256² | ✅出 |
| 8 | DK_icon_deepsea_pearl | 07_道具_珍珠贝 | Item 1204.DK_图标（珍珠贝·走神秘宝藏机制·零程序）| 256² | ✅出 |
| 9 | DK_icon_deepsea_compass | （未出·深海罗盘骰子图标）| Item 1203.DK_图标（普通抽卡/骰）| 256² | ⬜TODO |
| 9b | DK_icon_deepsea_compass_pay | （未出·深海海神罗盘付费骰图标）| Item 1205.DK_图标（付费骰）| 256² | ⬜TODO |
| 10 | DK_img_Activity_icon_Monopoly_deepsea | （未出深海 HUD icon） | ActvOnline 102803.ActvIcon | 124×136 | ⬜TODO |
| 11 | DK_Role_deepsea | （深海角色 Spine 待美术） | ActvVoyage 2803.DK_RoleMedel | — | ⬜TODO(暂DK_Role_Bunny占位) |

注：
- 1~7 = 本期可入库换皮（新活动用，原 2801 不动）。
- 3 钻石：复用 island_2_lv5 的蓝水晶 png（新 DK 指向它即可），但需「取消升级」程序钻石才会用到（见 README ③）。
- 8/9 待出美术；10 待程序新增 ProgressItemID 道具。
