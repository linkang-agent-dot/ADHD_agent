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

## 案例3：X3NEW-1952 单日抽奖计数误判已满（2026-07-10 调查中，服务端计数体系代码锚点）
- **案情**：玩家1848973@2050，本轮窗口(07-04~06)只成功抽1次(2000钻)即被判"已达单日上限"(OneDayMax=150)；客服原单AI-33449关键事实=**同公会多人同时被判满、当天没人参与过**→指向全服共享状态而非单人存档。
- **计数体系锚点**（server\GameServer.Hotfix\PlayerMeta\Activity\ActivityMeta.LuckyWheel.cs）：入口OnStartLuckyWheelReq:17；判满CheckCanStartLuckyWheel:192-237（:217 dailyUsedCount vs OneDayMax→错误码**1017008**）；+1在:53-64（10连/100连只产生1笔流水，数仓换算次数=金额÷2000）。存储=玩家activityDict[activityId].luckyWheelData{dailyUsedCount/dailyUsedFreeCount/totalUsedCount}，**proto无日期/轮次字段**，"单日"全靠外部重置。
- **重置链路**：每日清零=ActivityLuckyWheelCondition.cs:28-57（⚠️:37 活动关闭期跳过不清；⚠️ActivityMeta.cs:175-178 conditions循环无逐条try/catch，前面异常会让后面活动漏日更）；换期重建=OnAddActivity new luckyWheelData。全服级=ServerActivityLuckyWheelMeta.cs:28-35 每日清零 obtainSRewardCount（对应SRewardSeverNum=3全服每天超奖上限）。
- **已排除（有实据）**：①跨轮残留（数仓：玩家上轮仅1付费+2~3免费，全服上轮单日最高80次没人到150）②OneDayMax配置错（三分支一致=150；1010/1023=99999）③错误码误映射/免费付费混计/读错字段（代码验过）。
- **已排除(续)**：④全服超奖(SRewardSeverNum=3)——满了只切普通奖池照常成功、客户端零引用无禁用面 ⑤多转盘并行串数据——全链严格按activityId解析 ⑥1017009兜底失败——拒绝前必先扣款，数仓无第二笔扣款流水反证 ⑦玩家级每日重置断——07-05该玩家三转盘免费抽全部成功入账，重置正常。
- **🔴 最大反转(07-13)**：**投诉对象根本不是转盘**——L2建单把俄语Карнавал(狂欢节)按字面归因到幸运大转盘(101001中文名带"狂欢节")属归因错误。真凶=「公会狂欢/派对」功能族(酒馆升级触发全员领钻石、参与名额10/10)：同期AI-33288(名额满10/10多公会)/33501/33455/33419/33486/33368 跨服(1910/2030/2050/2060/2080/2120/2180/2230)集体爆发"每日限额未重置"，全部始于07-02/03，与 gdconfig master 07-02~03 合入海妖×酒馆联动(X3NEW-681/686)时间吻合。**最终结论(已锁定)**：真凶=联盟红包(UnionRedEnvelope,X3NEW-548狂欢派对,Item_2400xx酒馆升级掉红包)的**客户端三处BUG**（07-02随版本上线）：①免费+付费合计误比免费单桶上限10→本地弹"已达每日上限"**请求不发**（服务端无感知、数仓断档）②点开过的红包ID持久化PlayerPrefs永久拉黑→跨天跨重启不可领="每日不重置"观感 ③主界面硬编码dailyLimit=10按合计判。**07-04已修**（client commit 2b868eda7fd, qa_shaorui），=X3NEW-1880同族（该单已解决、热更上线、并入7玩家07-06起流水恢复）。服务端红包链路无辜（07-06加诊断日志1小时后还原）。处置=1952改归因关联1880；副产品：服务端抽奖不校验count可负数倒扣计数(建议修)、100连按钮显示条件恒false。红包代码锚点：领取UnionMeta.RedEnvelope.cs:54/175-185(每日上限,免费付费分桶各10)/206-208(名额GotNum>=limit)；日清UnionMeta.cs:119→OnDayUpdateForRedEnvelope:410。
- **📌 L2建单归因陷阱(通用教训)**：俄语/多语客诉里的活动名(Карнавал/Carnival)≠中文活动名字面匹配；先用玩家行为流水验证"他到底玩没玩得动被投诉的功能"再定调查对象——本案玩家转盘抽得好好的，转盘查了三轮全是无用功。
- **客户端预检坑**：客户端本地同构判满、不过**根本不发请求**→数仓只有1笔流水≠服务端只判1次。

## 案例4：X3NEW-1906 指针停大奖格但没中（2026-07-13 已定性=纯显示BUG）
- **根因**：客户端跳过动画路径不摆指针——`ActivityMeta.LuckyWheel.cs:58-61`(客户端) isSKipAnim开着或>10连(100连强制)时直接弹结算不进动画链；指针滞留 `UIActvLuckyWheel.cs:329 ResetTurntableArrow` 的初始0度；**0度格=奖励组内Order=0第一格=核心大奖**（深海组321第一行32100潜艇皮权重1/98401）→ 开跳过的玩家指针永远"指着大奖"，与结果零关联。次要变体：转动中点遮罩 `OnBtnTurntableMaskTrigger:483 ResetToEnd()` 停在中间奖励格。
- **无漏发**：发奖在服务端ack前完成(AddItemList)，结算弹窗cardIds=真实入账；数仓核查一致。
- **修法**：skip分支弹结算前按 cardIds 最后一个奖励补摆指针角度 `-(360/格数)×index`；遮罩路径同理；或初始角改两格中间的中性角。防御：MoveNextReward:381 IndexOf 未处理-1。
- **QA必现**：开"跳过动画"开关→任意抽→秒弹结算盘不转、指针恒指顶格大奖；或直接100连(强制跳过)。
- **isSKipAnim 冷知识**：跳过开关是**服务端持久化**的(OnSkipLuckyWheelAnimReq存玩家luckyWheelData)，跨登录生效——玩家"从来没见转盘转过"是正常态。
- **通用规律**：转盘奖励组第一行(Order=0)习惯放核心大奖=指针初始位，任何"不播动画"路径都会天然表现为"指针指着大奖"——同类客诉直接按此定性，先让客服问玩家是否开了跳过动画。
