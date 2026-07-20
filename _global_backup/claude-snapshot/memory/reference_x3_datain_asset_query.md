---
name: x3
description: X3 Datain 查皮肤/道具拥有率、R级分布、付费额的正确口径——asset_id 带类型前缀是最大坑
metadata: 
  node_type: memory
  type: reference
  originSessionId: 490ce72b-3baa-4614-9fe0-430f6331e079
---

X3 Datain（TRINO_HF, v1090）查外显/道具的**拥有率、R级分布、付费额**。脚本走 `C:\ADHD_agent\skills\ai-to-sql\scripts\_datain_api.py` 的 `execute_sql(sql,'TRINO_HF')`。

## 🔴 最大坑：asset_id 带类型前缀（裸 ID 全返 0）
`ods_user_asset` / `dl_active_user_asset_balance_d` 里 **asset_id 是带类型前缀的字符串**，不是裸数字 ID：
- 道具：`Item_5303401`（英雄皮肤道具）、`Item_81101`(岛屿皮肤道具·永久)/`Item_81103`(3天)/`Item_81104`(7天)
- 皮肤本体：`Skin_1011`（岛屿皮肤解锁，岛屿皮肤的"拥有"看这个）、`Hero_1034`（英雄）、`FurnitureSkin_1003`（家具皮肤）
- ⚠️ `asset_id='5303401'`（裸）→ **0 条**；必须 `asset_id='Item_5303401'`。`change_type` 也是字符串，用 `change_type='1'`（不是 `=1`，否则 varchar=integer 报错）。
- **不知道前缀就反查 `dim_asset`**：`SELECT asset_id,asset_name FROM v1090.dim_asset WHERE asset_name LIKE '%海风旅者%'` → 给出真实 asset_id。
- ⚠️**英雄本体别用 `Hero_10xx`**（dim_asset 里有但 ods_user_asset/余额快照**流水全零**=假资产形态，2026-07-10 实证）：英雄获得的真实形态=**`Item_50xxx`「英雄-XX」**（规律=50000+英雄尾号：爱莉希雅 Item_50040/霍普金斯 Item_50034/诺娃 Item_50055；晋升形态带后缀如 Item_500341）。查英雄保有一律 `asset_id='Item_50xxx' AND change_type='1'`。

## 拥有率（曾获得=拥有，外显永久）
```sql
SELECT count(distinct user_id) owners
FROM v1090.ods_user_asset
WHERE asset_id='Item_5303401' AND change_type='1'
  AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 1880   -- 1-88/89服
```
- 岛屿皮肤拥有口径优先用 `Skin_xxxx`（解锁本体）；英雄皮肤用 `Item_530xxxx`（道具，皮肤"使用后获得"）。
- 拥有率分母：MAU = `ods_user_login` 近30天去重(`partition_date>='YYYY-MM-DD'`，partition_date 是 **varchar**)；或累计登录总玩家。

## 拥有者 × R级分布
join `dl_user_rlevel_all_info`（按日快照，game_cd=1090，rlevel=chaoR/daR/zhongR/xiaoR=超/大/中/小R；表不全→未命中=未分级）：
```sql
WITH o AS (SELECT DISTINCT user_id FROM v1090.ods_user_asset WHERE asset_id='Item_5303401' AND change_type='1' AND <服段>)
SELECT COALESCE(r.rlevel,'未分级') lv, count(DISTINCT o.user_id) c
FROM o LEFT JOIN (SELECT user_id,rlevel FROM v1090.dl_user_rlevel_all_info WHERE game_cd=1090 AND partition_date='<最新>') r
  ON CAST(o.user_id AS varchar)=CAST(r.user_id AS varchar)
GROUP BY 1
```

## 拥有者付费额
join `ods_user_order`（pay_status=1；USD: `currency_type IN ('usd','TOKEN') ? actual_charge : pay_price`）。可算终身付费 / 某活动礼包付费（iap_id IN 礼包集）。礼包名反查 `dim_iap.iap_id_name`。

## 🔑 reason_id + reason_sub_id：按来源拆资产变动（隔离竞猜/免费领取等）
`ods_user_asset` 有 **`reason_id`(来源类型)** + **`reason_sub_id`(来源具体id)** + reason_sub_id_level/reason_status。这是按「为什么获得」拆资产流水的关键（订单表拆不出免费/非付费时用它）。
- Item_1146(世界杯抽奖券)获取 reason_id 分布(2026-06-27实测)：**`buy_gift`(买礼包,reason_sub_id=礼包号)** / `activity_battle_pass_score_reward`(BP) / `activity_reward`(累充/签到等) / item_op_activity_unclaimed_reward。
- **竞猜参与(含免费!)的正确查法**=`asset_id='Item_1146' AND change_type='1' AND reason_id='buy_gift' AND reason_sub_id LIKE '894%'`,按 reason_sub_id 分组=每个竞猜礼包的领取(免费档894xx0=进界面+选队=触达;付费894xx1/2/3=买家,与订单表对得上)。
- **界面触达率代理**=免费竞猜领取distinct人数 / 55服DAU(`ods_user_login` distinct,同期);竞猜无UI曝光埋点([[reference_x3_config]]),免费参与率是最佳触达代理(领免费=必进界面选队)。2026-06-27 D0实测=2192/6375=34.4%,付费23人/0.36%,免费→付费转化1.05%。
- 通用:任何"买礼包/免费领礼包"参与都可用 `reason_id='buy_gift' + reason_sub_id=礼包号` 拆,不限竞猜。
- 📈**竞猜免费→付费漏斗发现(2026-06-29实测,累计D0-D3)**:免费档参与4532人;各付费档买家 $4.99=29/$9.99=23/$19.99=12人(随价递减);**免费→$9.99转化率=23/4532=0.51%**;★**$9.99买家100%先领过免费包**(0人不碰免费直接买付费)→验证"免费竞猜=付费入口/漏斗顶"飞轮设计成立,免费引流是付费前置。算法:免费=reason_sub_id%10=0,$4.99/$9.99/$19.99=%10=1/2/3,转化=两集合 pid(user_id||server_id) INTERSECT。
- ⚡**ods_user_asset 近实时(2026-06-29实证)**:`created_at`/`event_start_time` = **timestamp(6) 北京时间**(time_zone_name=Asia/Shanghai),ETL 滞后仅~10min(etl_time)→**可做小时级/实时分析**(不像订单表 T+1)。⚠️SQL 比较 created_at 必须用 `TIMESTAMP '2026-06-29 13:00:00'` 字面量(timestamp≠varchar,直接字符串比报错)。免费档=`CAST(reason_sub_id AS INTEGER)%10=0`(竞猜免费包894xx0,结尾0)。重复领取查法=`GROUP BY user_id,server_id,reason_sub_id HAVING count(*)>1`;玩家跨小时去重重叠用 `INTERSECT`。
- ⚠️**活动奖励类拆不出单个cfgId**:`activity_reward`/`activity_daily_free_reward`/`activity_resign` 的 **reason_sub_id 都是空**,且 **asset 表 activity_id 列全空**(没用)→无法把签到(101403)等精确锁到单活动。只有"买礼包"(buy_gift)带reason_sub_id=礼包号。签到的最佳口径=`reason_id='activity_daily_free_reward'`(每日免费奖励·签到走它,但可能含其他每日免费活动,非严格101403);补签=`activity_resign`(给Item_1002钻·小众·付费玩家0)。
- **付费玩家触达对比口径(2026-06-27 D0实测)**:付费玩家=`ods_user_order pay_status=1`当日distinct(55服);触达=JOIN asset对应reason的distinct user。结果:付费玩家499,**竞猜触达316/63.3%**(buy_gift 894%) vs **签到94.2%**(daily_free_reward)。付费玩家碰竞猜概率≈普通DAU(34.4%)的2倍。⚠️今日订单数仓T+1延迟(订单max分区滞后1天),"今天"无数据时用最新可用日。

## 道具获取量「异常增加」排查口径（2026-07-06 Item_11005 案）
- **先看绝对量再定级**：低流通道具的小时倍数放大（5~10倍）可能只是 +30个/小时的正常波动，别按倍数直接报事故。
- 三步：小时聚合对基线（前2天同时段+当天其余23h）→ 窗口内按 reason_id+reason_sub_id 拆来源 → 按 user_id+server_id 看集中度（少数人高频=疑刷；同服一批人=活动结算潮；全服普涨=运营发放）。
- **`shopitem_buy_item` 的 reason_sub_id 格式 = `{ShopID}_{ShopItemID}`**，直接反查 `C:\x3\gdconfig\tsv\Shop__ShopItemCfg.tsv` 秒定位商品/货币/单价/限购（如 1501_1501017 = 争霸赛商店1501 商品1501017）。
- 定性铁证=对价配对：每笔入账同毫秒应有对应货币扣减；多玩家秒级同 timestamp 是 BI 批量落盘特征、非脚本。
- ⚠️ **定性前必须回看 ≥2 个完整业务周期**：本案初查只回看 6 天恰落在周期谷底，得出「该商品 07-04 才放量」的错觉，差点把双周例行误判成新事件；拉长到 6 周后确认每期结算都有同款峰。
- **公会争霸赛周期锚点（监控白名单可用）**：双周制、**周六结算**（实测 06-06→06-20→07-04，下期 07-18），结算邮件=MailTemplate 2000029（徽章 Item_1123 入账 `reason_id='Mail' AND reason_sub_id='2000029'`，另 2000035=击败奖励），结算日大峰+3~5 天领取衰减尾 → 结算后 1~3 天争霸赛商店（Shop 1501）兑换小峰。「兑换峰与 2000029 同期出现」= 正常，勿报异常；峰值逐期抬升=参赛服数自然增长（57→62→75 服）。
- **BI 道具异常告警系统（bi-docs.tap4fun.com/数据分析报告/Asset_anom/，报告名 `x3_anom_report_{Item}_{时间}.html`）**：脚本 `X3_asset_detect_anomolyV02.R` 每小时扫 104 个道具；两阶段判定=①S-H-ESD(α=0.005)+涨幅>30% 预筛 → ②R1 单渠道暴起(贡献≥30% 且>14d同时段P99×4)/R2 少数人刷量(人均×10 且人数更少) 命中才推钉钉。数据源 `dm.asset_hour_detail`+ods 明细。报告 Part3 有 100 天 ESD 历史清单——**争霸赛双周周六凌晨潮每期都被统计层检出**（04-11 起 7 期全在），07-05 之前未推送疑因系统 6 月中后才上线（待向数据部核实）。误报白名单建议：归因=争霸赛商店(1501_*)且当日有 2000029 邮件峰→只记录不推送。
- **「同时段采样」监控的盲区（2026-07-06 实证）**：用户的道具获取监控=每天只采 10~11 点档对比 30 天。争霸赛兑换潮往期集中在**北京凌晨 4~6 点**（玩家时区活跃段），10 点档一直没量所以从未报警；07-05 报警纯属 1270 服公会碰巧 10:16~10:45 集中兑换。教训：①同时段采样天然漏掉发生在其他小时的周期性事件，排查"为什么之前没报"先拉结算日全天分小时分布；②该监控名义"人均"实际按总量触发（历史 10 点档人均 4.0/5.0 的单人多买日均未报，总量 35 才报）——判读报警先核实际生效口径。建议规则：总量异常 且 当日无 2000029 结算邮件峰才报警。

## 养成线缺口/饱和度三件套查法（2026-07-14 手册推广案实测，源自尼罗回归饱和度法）
问"某养成线还有多少付费空间"用三个数拼：①**需求宽度**=近30天 `change_type='2'` distinct 消耗人数；②**需求强度**=消化率(消耗量/获取量，数量列=`change_count` 需 TRY_CAST，80%+=供不应求)；③**库存薄度**=`dl_active_user_asset_balance_d` 最新分区 `approx_percentile(balance,0.5)` 中位余额 ÷ 人均日耗 = runway 天数（≤2天=到手即耗=缺口敞开）。⚠️两坑：balance 快照**无 server_id**（不分服段，只能全局）；`reason_id='buy_gift'` **含免费礼包**（付费供给要交叉订单表口径，别直接当付费量）。X3 核心养成材料 asset_id 速查：美酒7002/万能信物52001-3/传奇技能书19003/阅历1008/木板55100/金属55101/屏障55004/秘币1143/**海妖驯养经验1142**/海妖碎片220002-3/装备袋165905（全带 `Item_` 前缀）。海妖线付费货架=2009招募链式/2014秘币弹窗/2810驯养链式/30009经验周卡；秘币100%付费无免费渠道。**消耗者等级分布查法**：`ods_user_asset` 事件行自带 `player_level` 列(事件时点等级),按 change_type='2' 分桶即得"哪个等级段在耗这条养成线"(2026-07-14实测:改装/海妖消耗量89%/84%在20级后)。**系统解锁点真源**=gdconfig `FunctionUnlock__FunctionUnlock.tsv`(c8玩家等级/c7开服时间闸门);⚠️命名映射:海妖=机甲(枚举SirenMecha,机甲转盘mecha_wheel_reward发的就是驯养经验1142)。实测结果见 [[project_x3_hero_handbook]] 缺口段。

## 其他表
- `dl_active_user_asset_balance_d`：活跃用户资产**余额快照**（无 server_id，要 join 用户→服）。注意：皮肤"用后解锁"余额可能为0，拥有看 ods_user_asset 的 change_type='1' 流水更准。

## 工具选择
- **按道具ID查拥有/付费明细 → 用 ai-to-sql（Trino 明细查询）**，不要用 `datain-skill`（那是聚合指标 DNU/留存/付费，查不了单道具拥有）。

实战来源：2026-06 深海节查海风旅者(Item_5303401,41人/超R5)、赛米拉(Item_53017,17人)、月心珍珠(Skin_1011/Item_81101,30人/人均终身$22k)。

## 抽奖/开箱大奖皮肤「获取价格」查法（2026-07-10 夏日皮肤案）
- 链路：ActvOnline 开箱行(ActvType15)→ContentID→`ActvCrafting__ActvCrafting.tsv`(消耗券/奖池组/里程碑组)→**大奖皮肤不在奖池也不在花瓣兑换,走 Mail 发放**(夏日=邮件模板1000018)→数仓 `asset_id='Item_53xxxxx' AND reason_id='Mail'` 圈获得者→JOIN 订单表算这批人在开箱族包上的花费。
- 夏日恋语实测(5/29-6/8·88服)：皮肤=永恒誓约·赛米拉(Item_5301702)15人获得,**获取价中位$370/均值$366($210-550),零白嫖**;开箱族总流水$11,775÷15件=$785/件;15人窗口总付费人均$1,070。**皮肤价$370≈货架天花板$495的3/4**(渗透15/245买家=6%)。⚠️结论修正(07-10用户纠正):夏日开箱**本身带排行、鲸鱼冲榜意愿没问题**(顶部是把$495货架买光的)——板子不在"没循环"而在**排行投放物不值得继续掏+货架封顶限制冲榜弹药**;定向方向=**皮肤分层投放**:普通皮肤走量+高级皮肤(互动场景+属性技能+华丽妆造)当排行头奖,冲榜消耗无上限=绕开货架天花板给top1%开深度;先例=海风旅者带专属技能"商会互惠条约",配置链路见[[reference_x3_cosmetic_attribute_chains]]。

## UI 曝光/触达 + 转化率代理口径（2026-06-29 异国美酒储蓄罐双档回归实测）
**X3 有两套 UI 点击埋点表**：`v1090.ods_user_click`（基础）+ `v1090.ods_pb_user_click`（更全，列 control_id/from_page_id/to_page_id/json_attrs/business_name）。但**覆盖不全**——只埋了主界面/活动队列(UIActivityNewQueue)/卡包(UICardPackResult)/推币机(UICoinpusher*)/联盟(UIAlliance*)等少数界面；`to_page_id` 整列为空（页面维度没上报）。~~储蓄罐/获取途径面板无埋点~~ **⚠️已过时(2026-07-17 更新)：储蓄罐 HUD 改造(MR!668)自带三埋点，07-09 起有数**——点击 `piggybank_hud_click`(ods_pb_user_click)、曝光 `piggybank_hud_show` + 登录弹窗 `piggybank_obtain_popup`（表=`v1090.ods_pb_client_application_log`，**界面show类事件走这张表**，列 event_name/json_attrs/sid，created_at 北京时间；别搜 ods_pb_application_log 那名字不存在）。储蓄罐触达从此用真埋点，不再用下面的货币消耗者代理（代理法保留给其他无埋点界面）。查某界面曝光前先 `SELECT control_id,count(distinct user_id) FROM ods_pb_user_click WHERE partition_date=... AND control_id LIKE 'UIxxx%' GROUP BY 1` 确认有没有埋点。
- **没曝光埋点时的触达/转化代理**：用「持有/消耗某货币的玩家」做曝光上界（这群人才会进该货币的获取途径面板看到卡）。异国美酒储蓄罐案：分母用**当日消耗异国美酒玩家**(`ods_user_asset asset_id='Item_7002' AND change_type='2'` distinct)，分子=当日储蓄罐买家(订单 iap_id IN 档位 distinct)，转化率≈2.7–2.9%。注明「分母是曝光上界、真实曝光更少→真实转化率更高」。
- **付费转化曲线读法**：转化率(买家/货币使用者)几乎不动 + ARPPU 大涨 = 改造靠「深度」(老买家买更深)不靠「广度」(拉新买家)。回归付费深度款时这是关键判据。

## 礼包蚕食归因法（2026-06-29 异国美酒储蓄罐回归实测，做"新礼包有没有抢其他礼包生意"必用）
判断一个新礼包/新档对其他礼包的蚕食，**只能跟"卖同一纯货币"的礼包比，且要按实际发放内容拆分**，否则会把无关礼包的波动赖到新礼包头上（实测教训：差点把"凌霜武道挑战""英雄豪礼"的下滑算成储蓄罐蚕食，其实它们绑特定英雄/掺钻石）。三步：
1. **找全投放该货币的礼包**：`SELECT reason_sub_id, count(*) FROM ods_user_asset WHERE asset_id='Item_<货币>' AND change_type='1' AND reason_id='buy_gift' AND <日期段> GROUP BY reason_sub_id`（reason_sub_id=礼包/Pack id；buy_gift 才带 sub_id，见上文）。
2. **拆每个礼包实际发放内容**：`SELECT reason_sub_id, asset_id, count(*) FROM ods_user_asset WHERE reason_id='buy_gift' AND reason_sub_id IN (...) AND change_type='1' GROUP BY 1,2`，再 `dim_asset` 译名。**只发该纯货币的=真替代品；掺钻石(Item_1002)/VIP点数(Item_2022)/英雄信物(Item_510xx,如信物-凌霜/夜玫瑰/维奥莱特)的=不可比，剔除**（绑英雄的按英雄上新/退场周期走，与新礼包无关）。
3. **只对"真替代品集合"算前后流水差**=该新礼包的蚕食额；新礼包增量 − 蚕食 = 对该货币直接销售的净增。实测：储蓄罐+$435/天，纯异国美酒礼包(11600系，只发Item_7002)−$125/天 → 净增~+$310/天；其余英雄礼包波动不算。
- ⚠️ 别用"全品类大盘前后差"下结论：大盘可能恰好被无关礼包的生命周期波动掩盖（实测大盘看着-0.6%持平，但拆开后净增是正的）。
- 关键道具id：Item_1002=钻石、Item_2022=100VIP点数、Item_7002=异国美酒、Item_510xx=英雄信物(碎片)。
