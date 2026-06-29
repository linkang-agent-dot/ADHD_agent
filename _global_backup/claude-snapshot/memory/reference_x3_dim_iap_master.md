---
name: x3-dim-iap
description: X3 数仓维表 dim.iap 添加节日礼包主数据的链路、字段映射、分类口径（每个节日都要做这步）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 14757c79-a7fe-46fc-9d73-3fecd89a43da
---

# X3 dim.iap（数仓礼包维表）节日礼包主数据添加

X2 有 iap-sync-to-master skill（QA表→礼包维表）。X3 对应需求 = 把节日 Pack 补进**数仓主数据表 dim.iap**。
和 X2 不同：X3 的 dim.iap **已有自己成熟的分类口径**，要照抄现有节日行（尤其尼罗 210601-210615 = 直接模板），别套 X2 的 NAME_RULES。

## 表位置
- **目标主数据表**：GSheet `1Pblighke8cHVMrGVuN60A9Cz-yBSKO8JKZ0my2ntCqU` 页签 `dim.iap`（数仓维表，~4277行；同 spreadsheet 还有 dim.asset/dim.activity/dim.task 等全套 dim.*）
- **源**：X3 Pack 表 `C:\x3\gdconfig\tsv\Pack__Pack.tsv`（col0=ID, col7=Price→PackPrice ID非USD, col9=PackType, col13=Content=RewardID）
- **名称源**：i18n `C:\x3\gdconfig\tsv\i18n\Text__Text.tsv`，key=`TXT_Pack_Name_{id}`（col0=key可能合并|分隔, col3=中文, col4=en）；免费礼包/锚点常无 pack name key

## dim.iap 字段（A–N）
A iap_id(Pack ID纯数字) | B 中文名 | C 英文名 | D iap_price(USD) | E iap_type | F iap_type2 | G iap_type3 | H iap_type4 | I iap_type5(bool) | J iap_type6 | K iap_type7 | L iap_type8(道具资产ID列表) | M note | N iap_rank

## 节日礼包分类口径（照抄尼罗 210601-615）
按 **PackType** 定 G：
- 链式礼包 PackType=11 → `E=节日活动 / F=节日活动-节日资源包 / G=节日活动-节日资源包-链式套装 / H=节日礼包`
- 锚点道具弹窗 PackType=15 → 同上但 `G=节日活动-节日资源包-道具弹窗`
- `I=false`；**M(note)留空**——"节日礼包"标在 H(iap_type4) 不在 note；N=0
- L=礼包发放道具ID列表（如 1146,1002,2022 = 券+钻+VIP；免费礼包只有券）
- 名称：免费链式行=`免费礼包/Free Pack`（惯例，无i18n key）；锚点行=所售券道具名（211012-015=道具1146「世界杯冠军抽奖券」）；付费链式名取 i18n
- 其他类型行参考现有：英雄皮肤`英雄皮肤-英雄皮肤-商店常驻/-道具弹窗`、外观`外观-外观-活动礼包`、装饰`酒馆-经营建设-链式套装`、主城三件套`酒馆-经营消耗-活动礼包`

## 按礼包内容定分类（content→tag 速查，最关键）
分类靠**礼包发什么道具(L列内容)**判，不是只看 PackType（PackType=16 在尼罗装潢/外观/主城三件套/世界杯应援上都出现过，单看它定不了类）：
| 礼包内容 | E / F / G | H | M |
|---|---|---|---|
| 节日券+钻+VIP 资源包(链式 free/paid 交替) | 节日活动 / 节日活动-节日资源包 / -链式套装 | 节日礼包 | 空 |
| 节日券锚点(单买多档同名) | 节日活动 / 节日活动-节日资源包 / -道具弹窗 | 节日礼包 | 空 |
| 家具/装饰特惠(151xxx 家具) | 酒馆 / 酒馆-经营建设 / -链式套装 | **空** | 空 |
| 主城三件套(152xxx 地板墙纸横梁) | 酒馆 / 酒馆-经营消耗 / -活动礼包 | 节日礼包 | 空 |
| 岛屿/城市皮肤(81xxx)、头像框(80xxx) | 外观 / 外观-外观 / -活动礼包 | 节日礼包 | 空 |
| 英雄晋升皮肤(5301xxx) | 英雄皮肤 / 英雄皮肤-英雄皮肤 / -商店常驻 或 -道具弹窗 | 节日礼包 | 空 |
- ⚠️判断点(可被用户否):①国家应援礼包(世界杯894xxx,48国×4档,PackType16,发1146券+助威头像框1148/表情1149宝箱)归到`节日活动-节日资源包-链式套装`(与世界杯主礼包同族,统一世界杯券产出包)②头像框归`外观`(无独立头像框桶,外观最近)

## 操作铁律
- **先 backup 再写**：`gs.backup_tab(SID,'dim.iap')`（duplicateSheet 便宜，4277行无压力）→ 用户明确要求过
- 节日 Pack 行在 dim.iap **可能已半填**（id/price/asset 有，E–H/名称空）——这时是「补分类」不是「append新行」，按 id 定位逐行 `update_range A{row}:N{row}`，保留已有 D/L/N
- 行**非连续**（字符串排序+夹杂别的id，如 211010@2523 / 21101@2524 / 211011@2525）→ 必须按 id 定位行号，别假设连续块
- 写完逐行反读校验（E=节日活动 & G含节日资源包 & H=节日礼包）

## ⚠️ BP购买包 130020/130021 是「22个节日BP共享同一对iap_id」——改名有跨节日归因副作用(2026-06-26)
- `130020`(进阶$9.99)/`130021`(至尊$19.99) = **所有节日积分BP(ActvType22)共用的购买包**(`BattlePassScore.tsv` col5恒=`130020|130021`,22个节日引用:春风饮酒2207/烧烤2210/.../元旦2233/尼罗2234/情人节2236/春节2238/世界杯2242/深海2244)。dim.iap **一个iap_id=一行=一个名**→**无法按节日拆BP收入**(同包卖给所有节日)。
- 原名「高级/至尊护航令 Premium/Supreme Escort Pass」(护航令=最早用它的BP,名沿用)。2026-06-26 用户要求改「世界杯通行证-进阶/至尊」(行758/759 B/C列,已backup)——**用户明确知情下override**:改后尼罗/情人节/深海等21个节日BP购买在数仓也显示「世界杯通行证」。**改这俩前必须提醒此副作用**(追引用链=`awk -F'\t' '$5~/130020/' BattlePassScore.tsv`)。要按节日拆BP收入只能用**活动ID(ActvOnline 102243等)**不能用iap名。

## 已处理 / 待办
- 2026-06-25：世界杯主礼包 211001-211015、世界杯国家应援 894010-894483(192行)、深海节 211016-211031(16行) 已全部补全分类并校验(未分类=0)
- 逐行写慢(208行≈数分钟,gws逐次spawn node)：行数多时改 run_in_background；偶发瞬时报错(本次211031)→反读 E空 即补写
- 工具脚本走 [[reference_gsheet_toolkit]] `gsheet_utils.py`，别现写
