---
name: reference-x3-luckywheel-complaint-check
description: X3 幸运转盘(ActvType=10)「中大奖未到账」客诉的数仓核查口径与已验证结论范式（AI-33203 尼罗黄金卷轴案）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6662964b-398d-4bbb-a4b2-089beb425648
---

# X3 转盘客诉核查口径（源自 AI-33203，2026-07-03）

**配置链**：ActvOnline(101023, Type=10 LUCKY_WHEEL) → ActvLuckyWheel(ID=ContentID=1023, 消耗券+RewardGroup+OtherRewardGroup) → ActvLuckyWheelReward(奖池档位, 权重) → ActvLuckyWheelOtherReward(里程碑=**累计抽奖次数**)。发放=服务端 `ActivityMeta.LuckyWheel.cs` AddItemList 直接入包不走邮件；SReward 档抽中有全服跑马灯。客户端指针落点由服务端返回的中奖 cfgID 反查，**不存在动画与发放不一致的代码路径**。

**数仓核查五步**（ods_user_asset, asset_id 必须带前缀 Item_xxx）：
1. 查道具入账：`reason_id=lucky_wheel_reward` 的该道具流水（免费抽=无对应券消耗；付费抽伴随 `reason_id=lucky_wheel` 的券扣减）。
2. 对账里程碑：券消耗次数+免费抽次数 ≈ 截图里的累计进度（如 47/1500），吻合=数仓视角完整。
3. 生涯总量对账：该道具历史入账总和 vs 截图持有量。
4. 反证发放链路健康：查全服同档位（如 change_count=1000）同 reason 入账笔数——别人正常到账=非系统性故障。
5. 大奖档验证：SReward 档抽中会有跑马灯记录，玩家无记录=没中。

**高频误读模式**：同一奖池 4 档共用同一道具图标（×1/×20/×200/×1000），玩家抽中 ×1（权重25%）误认成 ×1000（权重0.2%）。核查后属玩家误读、非BUG，不补发。

**坑**：数仓小时级 ETL 有 ~1h 延迟窗口；stg 实时层(hive catalog)无权限；北京时间口径换算玩家时区（俄区"当天"从北京 05:00 起）；`query_trino.py` 必须带 `--datasource TRINO_HF`，结果默认 100 行截断（逐资产拆查绕开）。

## 案例2：AI-33423 海洋女王10连抽（2026-07-06，判定=误读不补发）
- **「Queen of Sea/海洋女王」= 30留活动组 ActvGroup 119**（新服吃 30留，不在深海节铺开范围 1170~2010），转盘 ActvOnline **101010** / ContentID=1010，消耗 **Item_1067 珊瑚币**：商店 3000钻/张（shopitem 1011_1000042），单抽1张 / **10连=9张=27,000钻**；奖池组307/里程碑组3007。另有常驻钻石直扣转盘 ActvLuckyWheel 1001（2000/18000钻）。
- **核查范式升级——「扣款孤儿」检查**：把玩家窗口期全部 `lucky_wheel` 扣券与 `lucky_wheel_reward` 入账按时间戳配对（正常 20~40ms 内成组入账），无孤儿=发放完整；再加券购销对平（获得总量=消耗总量、balance 归零）。
- **新误读模式**：10连奖励按同道具聚合只显示 ~5 行，全是资源型小奖且两轮内容雷同、无大奖视觉冲击 → 玩家（尤其短时间连抽多轮/多转盘）把「没中显眼奖励」当「没发奖励」。「放下手机再拿起没收到」也属此类——奖励实际即时入包。

## 转盘身份速查表 + 快筛法（2026-07-06）
| 转盘 | 活动 | ActvOnline/ContentID | 消耗品 | 单抽/10连 |
|---|---|---|---|---|
| Queen of Sea 海洋女王 | 30留组 ActvGroup 119（新服） | 101010/1010 | Item_1067 珊瑚币(3000钻/张, shopitem 1011_1000042) | 1张/9张 |
| Abyssal Compass 深海罗盘 | 深海节（部署范围仅 1170~2010 共59服，单号13933跨服大池） | 101025/1025 | Item_1200 深海藏宝图(节日任务/签到产出) | 1张/10张 |
| 常驻钻石转盘 | 常驻 | ActvLuckyWheel 1001 | 钻石直扣 | 2000/18000钻 |

**快筛两板斧**（可秒排非本玩家/张冠李戴工单）：① 用 i18n 反查客诉里的英文活动名锁定活动（`TXT_ActvOnline_ActvName_1010xx`）；② 查「该服当日有没有该消耗品流水」做部署范围快筛——0 行 = 该服没开这活动。但注意：**AICS 工单的活动名/道具名是 AI 转译，可能整个走样**（实测「女王恩典卷 Queen's Grace Scroll」被译成「藏宝图转 Abyssal Compass」）——名字对不上时别急着判"非本玩家"，先走下面的流水反查法。

## 工单活动名不可信时的流水反查法（AI-33423 第二单验证）
1. 玩家全量消耗扫描：`change_type='2'` 按 reason_id+asset_id 分组，抽奖类 reason 主要两个——`lucky_wheel`（转盘）和 `gacha_draw`（酒馆招募，奖励 reason=`gacha_reward`）。
2. 逐笔「扣款孤儿」配对：每笔抽奖消耗后 ≤1s（实测 20~40ms）应有成组奖励入账，孤儿=疑似真BUG。
3. **查"道具消失"必查回收对 reason**：`item_op_activity_close_item_recycle`（活动到期系统回收未用券）与 `..._recycle_replace`（19分钟内邮件折算补偿，MailTemplate 101111「道具回收」，尼罗券=100钻/张）成对出现——玩家把"券被回收"误读成"抽了没给奖"是高频客诉源，回复时引导查「道具回收」邮件。
4. 道具身份映射：Item_1128=女王恩典卷(尼罗返场转盘101023/ContentID 1023) · Item_7001 英雄美酒(日常任务宝箱 daily_task_box_reward 产出)/Item_7002 异国美酒=酒馆招募。

相关：[[reference_x3_datain_asset_query]] [[reference_x3_config]] [[Jira API Access]]
