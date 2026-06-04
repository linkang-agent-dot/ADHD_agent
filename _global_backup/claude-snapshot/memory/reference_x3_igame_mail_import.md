---
name: x3-igame
description: "X3 批量发邮件导入CSV格式（GBK/道具信息列用[ID*数量]）—— 与 P2 的 assetType JSON 完全不同"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d85a4e25-0b5a-4f0e-862d-4d42bcee2238
---

X3 iGame 批量发邮件/补发导入表格式（**与 P2 的 `{"assetType":"item",...}` JSON 不一样**，别用 bulk-mail-reissue skill 的 P2 输出直接发 X3）。

## 格式（GBK 编码，逗号分隔）
6 列：`服务器 ID,玩家 ID,道具信息,礼包信息,虚拟资产信息,自定义`
- 道具放在 **「道具信息」**列，写法 `"[道具ID*数量, 道具ID*数量]"`（方括号 + `ID*数量`，多个逗号分隔，整列加引号）
- 礼包/虚拟资产/自定义 列一般留空
- **没有标题/正文列**——邮件标题正文在 iGame 界面单独填
- 例：`1440,711471,"[1142*1000, 220001*20]",,,`

## 样例文件
`C:\Users\linkang\Pictures\X3验收\海妖任务补偿_批量导入.csv`（X3 真实导入样例，GBK）

## 道具ID = 配置表 ItemID（数字，不是 datain 的 Item_xxxx）
如 一封情书(夏日/情人节抽奖券)=1134、女王恩典卷(尼罗抽奖券)=1128、钻石=1002。
礼包内含道具：Pack.Content→Reward.RewardID→多行 ItemType/ItemID/MinNum，见 [[reference_x3_config]]。

## 关联
- P2/X2 用 [[reference_bulk_mail_reissue]] 的 assetType JSON 格式；X3 用本格式。
- 补发前核查是否已发，避免重复补偿（见 [[reference_bulk_mail_reissue]] reason 核查规则）。
