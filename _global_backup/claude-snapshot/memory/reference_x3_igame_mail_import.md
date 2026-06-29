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

## 多语言邮件内容导入(标题/正文多语言·与道具csv分开导)
- 模板 `C:\Users\linkang\Downloads\[模版]导入多语言邮件内容.csv`。**转置格式**:语言做【列】(20种:英语-en/简体中文-cn/繁体中文-zh/法语-fr/德语-de/俄语-ru/日语-jp/韩语-kr/西班牙语-sp/印度尼西亚语-id/泰语-th/阿拉伯语-ar/罗马尼亚语-ro/荷兰语-nl/土耳其语-tr/葡萄牙语-po/意大利语-it/越南语-vi/波斯语-fa/波兰语-pls),字段做【行】(第1行表头=空格+20列名/第2行标题/第3行内容/第4行超链接文本内容/第5行超链接地址)。**UTF-8无BOM, CRLF, 21列**。
- 🔴**坑(2026-06-29实测):文件结尾不能有空行**——csv.writer 默认每行后加\r\n(含最后一行)→尾部多空行→iGame 把尾空行当多一行而**导入失败**。模板=4个\n(5行无尾换行)。修=写后去掉结尾\r\n。⚠️csv.reader 检查会自动忽略尾空行→审核脚本查不出,必须**字节级**(`open(rb).count(b'\n')`)核。
- ✅**统一工具**:`~\.claude\skills\bulk-mail-reissue\multilang_mail.py` 的 `write_multilang_mail(path,{lang_code:(标题,正文)})`(已处理无尾换行+20列模板);任何补偿/发奖多语言文案都用它别手拼。emoji(🏆4字节)未确认兼容,导入仍报错先去emoji。

## 关联
- P2/X2 用 [[reference_bulk_mail_reissue]] 的 assetType JSON 格式；X3 用本格式。
- 补发前核查是否已发，避免重复补偿（见 [[reference_bulk_mail_reissue]] reason 核查规则）。
