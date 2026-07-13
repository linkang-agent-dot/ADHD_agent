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

## 🟢 API 直发（2026-07-03 打通，可不走 UI）
- **端点**：POST `https://webgw-cn.tap4fun.com/ark/mails/send/players`（prod；与 UI 上传 CSV 完全等价——UI 只是前端把 `[1146*5]` 解析成 assets JSON）。鉴权同 gm-send：headers `Authorization: Bearer <token>` + `clientid/gameid/regionid`，读 `.igame-auth.json`（见 [[reference_igame_gm_send]]）。
- **payload**：`{"to":[{"serverId":"2080","playerId":"1879472","assets":[{"assetType":"PROP","id":"1146","amount":1}],"extension":""}],"content":[{"lang":"ru","title":..,"body":..,"collectionId":-1},...多语言多条...],"mailCategoryId":1,"sendType":-1,"validPeriod":1920(小时=80天),"customParams":"","rewardVersion":"","remark":"..."}`。serverId/playerId/id 均**字符串**，amount 数字。多语言直接塞 content 数组，不用另导多语言 CSV。
- **路由/查询工具**：`~\.claude\skills\igame-skill\`（`igame-routes.json`=1090 全接口路由表；`scripts\igame-query.js` 直打网关）。发件箱 `write "email/outbox/getMailList" '{"pageIndex":1,"pageSize":5}'`；详情 `read "email/outboxDetail/getMailDetail" '{"id":<mailId>}'`。

## ★一条龙 CLI 直发工具（2026-07-03·发奖/补发统一走它）
- **工具**=`~\.claude\skills\igame-skill\scripts\igame_mail_send.py`（一条龙:CSV+多语言JSON→自动建payload→缺省dry-run→`--send`真发）。用法：
  - `python igame_mail_send.py --csv 奖励.csv --content content.json --remark "事由_人数_日期"`（dry-run，打收件数/道具合计/语言/remark）
  - 加 `--send` 真发；`--status <mailId>`查状态(2=待审/3=派发中/1=已发)；`--outbox [N]`查发件箱
- **`--csv`**=X3奖励CSV(GBK·6列`server,user,[1146*N],,,`·无表头)。**`--content`=多语言JSON `{lang码:{title,body}}`**(不是转置CSV)。**从生成器的`多语言邮件_{key}.csv`转JSON**=按表头`语言名-码`split取码+行1标题+行2正文(脚本见发奖工作流)。
- **★发送流程铁律**：①`--send`后网关返`success:true`只是**登记**·status=2**卡审批** ②**必须有人去iGame后台放行**(status2→才真派发) ③放行后`--status <mailId>`看sentAt/to[].failReason确认真发出 ④最终数仓入账收口 ⑤**建议先发1人金丝雀验格式再发全量**。
- **🔴两个已修bug(2026-07-03)**：①**`build_from_csv`原`rows[1:]`把无表头CSV首行当表头跳→每封漏发第1个玩家**。修=自动判表头(`start=1 if 首列非数字 else 0`)。②**发后盲取发件箱`data[0]`报mailId→抓到最顶别的草稿(误报"V2礼包"/同一id)**。修=**按刚设的remark精确匹配**发件箱找真实mailId。**接管教训:发后真实mailId永远按remark去发件箱查,别信盲取top**;每次remark设唯一(事由_人数_日期)才好匹配。
- **✅首例实战(2026-07-03)**：世界杯竞猜3场发奖=mailId **4725589(西奥6687)/4725590(葡克6426)/4725591(瑞阿6459)**·全status2待审·remark`世界杯竞猜命中_{场}_{数}_20260703`。产出`KB\产出-数值设计\X3_世界杯\发奖csv\content_{key}.json`。
- **⚠️ 审批流**：提交后 status=2 待审（需人在 iGame 后台放行，不自动过），网关 success 只是登记；判真发出看 detail 的 `sentAt/gsResponse/to[].status`，最终以数仓入账为准。**status 枚举（20260703 实测·两单对照修正版）**：workflow 流水 8=已提交 → **7=审批通过**（审批人必须是另一人，如龚亮；过审后 0=发送中 → 1=已发送，全程秒级）；**3=驳回/撤回（终态，不会再发！）**——提交人自己在 UI 操作自己的单容易点出 3。detail/列表 status：2=待审、1=已发送(sentAt回填)、3=驳回/撤回。⚠️别把 3 当"派发中"傻等（首日金丝雀单 4725437 就是这样卡的），卡住先拉 `getMailWorkflow` 对照流水。**-2=换单作废的旧单（2026-07-10 实测）**：世界杯 M5-M8 四封旧单查出 -2，实际发奖早已用新单完成——见 -2 别下"没发"结论，先查发件箱有无同 remark/名单的后继新单。
- **发送脚本范式**：payload 写 UTF-8 JSON 文件 + python urllib 读文件 POST（别把西里尔文塞命令行 argv）。已固化完整 CLI=`~\.claude\skills\igame-skill\scripts\igame_mail_send.py`（`--csv 导入.csv --content 多语言.json --remark ..` 一条龙构建，**缺省 dry-run、加 --send 才真发**；`--status <mailId>` 查单、`--outbox N` 查发件箱；用法见 igame-skill/SKILL.md「X3 玩家邮件直发」节，bulk-mail-reissue SKILL.md 文末有 X3 路由指回）。20260703 世界杯券补发首用（金丝雀1人→放行→全量；payload 范例存 `KB\产出-补发邮件\X3\20260703_世界杯奖券回收补发\api_payload_*.json`）。

## 关联
- P2/X2 用 [[reference_bulk_mail_reissue]] 的 assetType JSON 格式；X3 用本格式。
- 补发前核查是否已发，避免重复补偿（见 [[reference_bulk_mail_reissue]] reason 核查规则）。
