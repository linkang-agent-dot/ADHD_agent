---
name: x2-flashsale-placeholder
description: X2 限时抢购礼包显示占位数据(限购2222/价格555/默认头像)的诊断与根因——活动跑了旧配置，重开活动或重新热更即修
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f5d0e986-b7f5-42c6-ab46-30c79d5d6a9b
---

X2 限时抢购（限购礼包）货架里礼包显示**占位/默认数据**（典型：限购 `2222`、价格 `555`/`9999` 钻、剩余 `222/300`、默认人物头像、占位名）时：

**先判是配置还是运行时——看包类型差异：**
- **vm 直购包**（activity_package 里 `Cost={"typ":"vm",...}` + `CostLimit` 内嵌）显示**正常**，
- **IAP 包**（价格/限购靠跨表查 `iap_config`→`iap_template`）显示**占位** ——
- → 这个组合 = 配置本身没问题（vm 包内嵌数据能渲染），是 **iap_config/iap_template 跨表数据没被运行时加载到**。

**最常见根因（2026-06 拓荒节实测）：活动在 flash-sale 配置提交之前就部署了，服跑的是旧配置。**
- flash-sale 配置（`activity_special` 库存 val / `iap_config` / `iap_template` 价格）即使已在本地工作区正确，若**提交时间晚于上一次热更/部署**，服上就没有这批数据 → IAP 包占位。
- **修复：重开活动（重新部署）或对该服重新热更最新配置**，让它加载当前 dev 分支配置即可。拓荒节 `21127367` 重开后占位消失。

**诊断三类数据来源**（X2 限时抢购）：
- 钻石价/档位价：vm 包在 `activity_package.Cost`；IAP 包在 `iap_template.Price`
- 库存(剩余 total)：`activity_special.tsv` 的 flash_sale_gacha 组件 `Status` 列每包的 `val`
- 限购次数：vm 包 `activity_package.CostLimit`；IAP 包 `iap_template.Limit.limit_cnt`

**若重开/重热更后仍占位**：才往客户端方向查（新 IAP id 不在客户端包 / product_id 没在充值后台上架）。详见 [[workflow_x2_table_import]] [[feedback_x2_i18n_duplicate_key]]。

## 限时抢购时长 / 节奏配置位置（2026-06-04 改时长沉淀）
全在**表 2121 activity_special**（SheetID 用 resolve `2121_x2_activity_special`，真源 GSheet，列 `A_ARR_array`=col L，单位**秒**）：
- `flash_sale_buy_duration`：每波抢购**持续时长**，`[3600,3600,3600]`=每波 60 分钟（3 个值=3 波各自时长）。改时长改这个，如 180 分钟=`[10800,10800,10800]`。
- `flash_sale_buy_opentime`：活动开启后**多久进入抢购**，`[7200,36000,64800]`=2h/10h/18h（对应文案"UTC 2:00、10:00、18:00 开启"）。
- 一个时长组件可被多活动共用：21217032=沙滩节+占星节共用，212101145=拓荒节。改前用 activity_config 反查哪些活动引用了该组件 id。
- 配套文案 = i18n key **`IAP_flashsale_schedule_desc`**（"…开启并持续60分钟"，全限时抢购共用一条，17 语言）；改时长记得同步它（17 语言里"60"都是阿拉伯数字，直接 60→180）。

**换皮残留待留意**（拓荒实例，非显示 bug）：限时抢购换皮后 `iap_config/iap_template` 的描述常残留"S6春节限时抢购礼包"；`recharge_actv`/`actv_base_id` 可能仍指占星/夏日底座（影响累充归属，不影响货架）；raffle 奖池(activity_flash_sale_raffle)若复用底座奖池会开出旧节日的包。

## 🔴 限时抢购换皮必 fork「抽奖奖池 2187」+ 累计道具(2026-06-09/10 X2-43094「抽不了奖/开不了箱」沉淀)
限时抢购整套 = **5 个 2121 组件**(flash_sale_buy_duration / **flash_sale_gacha**(主) / flash_sale_popup / **flash_sale_raffle** / flash_sale_buy_opentime) + 货架包(2135) + IAP(2013) + **虚拟货 2186 activity_flash_sale_virtual**(售卖节奏系数,通用) + **抽奖池 2187 activity_flash_sale_raffle**。占星母版组件 21217032-036、拓荒 212101145-149。
- **累计道具(机制道具)= flash_sale_gacha 的 `reward`(col4 抽奖券/HUD累计货币) + `arg2`(col7 皮肤随机宝箱 box)**。占星专属 `11119549`(抽奖道具)/`11119550`(class=flash_sale_reward_box)；拓荒换皮**误借了 gacha 活动的内圈货币 `111111315/111111316`**(套了 gacha 卷轴齿轮图标)→ X2-43094 报"抽奖券用了 gacha 道具图标"。⚠️ 315/316 同时被 gacha 活动(multi_gacha 212101356 吃316、cost 212101358 吃315×10)消耗，**不能改它俩的 display_key**(连累 gacha)。正解=机制对齐占星(reward→11119549、arg2→11119550)；但**只改组件没用**——发累计道具的礼包(2013 IAP 的 other_items)也得把机制道具一起换成 11119549，否则产出端还发旧道具、玩家身上没新道具→**抽不了奖**(踩过：只改组件 push 上去直接改崩抽奖)。
- 🔴 **开箱断点 = flash_sale_raffle 的奖池没 fork**：`flash_sale_raffle`(拓荒212101148) 的 `status` 把货架包→奖池 id(21870001/002/003)；这些奖池在 **2187 表**,其 `category_param.drop` 的 `actv_package` 列出"开箱开出哪些货架包"。**2187 全表只有 21870001-003 三行,且占星/拓荒共用,drop 内容写死=占星货架包 21353103-108**。拓荒 fork 了货架包(213521232-240)/IAP,却没 fork 奖池→开箱去开占星包(占星活动下线取不到)→**开不了箱**。
- **修法二选一**：① 原地改这 3 行 2187 的 drop(21353103-108→拓荒 213521232-237,1:1同权重)——0新增行,但占星那套也跟着指拓荒包(占星不再上才安全)；② fork 新池(21870004-006)+改 212101148 的 status val 指新池(占星可能重开就用这个)。
- **教训**：raffle 奖池(2187)是藏在 flash_sale_raffle.status 里的**间接引用**(不在 2112 components 表面),和 [[x2-config-library]] 里 actv_links 不 fork 是同类坑;限时抢购换皮 checklist 必加"2187 奖池 fork + 累计道具(reward/arg2)用本节日专属 + 发累计道具的 IAP 包同步换"。

## 限时抢购「开箱/抽奖」客户端代码链路 + 卡死诊断(2026-06-10 X2-43094 查 x2client 坐实)
X2 限时抢购**完全复用 P2 的 MayFestival LimitTimeBuy 模块**,代码在 `D:\UGit\x2client\client\Assets\P2\GameScript\`(`UIActivityMayFestivalLimitTimeBuyModule.cs` / `ActivityMayFestivalLimitTimeBuyModule.cs`),X2 侧只有空壳 `UIActivityFlashSale.cs`。本机**无 X2 服务端代码仓**(发奖逻辑在服务端,未坐实)。
- **开箱(主抽奖)数据流**：点货架格开箱 → `LimitTimeBuyGacha()` 发 **`PioneerDayFlashSalePrizeDrawReq{actvID}`** → **服务端决定奖**(从奖池抽,客户端不读奖池) → 回 `PrizeDrawAck{PackageId, rewards}` → 客户端 **`m_Module.PackDic[ack.PackageId]`** 把奖显示到对应货架格。
- **两道"开不了"的门**：① 抽奖券(=flash_sale_gacha.reward 的 item, 拓荒 11119549) `< 1`→弹"去买礼包" ② **助力解锁 task**(=flash_sale_gacha.arg1 那条, `Displaykey==2`)的 state≠已领奖→点了弹提示开不了。换皮漏对齐这条 task = 门B 永远拦。
- 🔴 **开箱"动画播了但奖窗弹不出来/卡住" = `PackDic[ack.PackageId]` KeyNotFound = 服务端返回的礼包 id 不在客户端 flash_sale_gacha.status 货架集(拓荒 213521232-240)**。典型成因:**服务端跑的配置还是旧 2187 奖池(掉占星包 21353103-108),返回占星包 id,拓荒客户端 PackDic 没有→崩**。本质 = **客户端/服务端 flash-sale 配置版本不一致**(改了 2187 但没构建+部署到那台服,或服跑的不是改过的分支)。
- 🔑 **诊断口诀**:开箱"卡住没奖窗"先查两条——① 服务端 2187 奖池产出的 actv_package ⊆ 客户端 flash_sale_gacha.status 货架集;② **push≠生效**,配置改完必须构建+部署到测试服那条分支 + **重开活动**才会重读 2187。客户端代码本身没 bug,别去改客户端/重出包(前提:11119549/11119550 已正常导表进客户端 item 表、11119550 class=flash_sale_reward_box)。
- **皮肤随机宝箱(item 11119550)是另一条独立流程**(点宝箱入口→`UIItemHelper.UseItem`按 class=flash_sale_reward_box 派发→服务端读 11119550 的 category_param.drop 发奖),**跟主抽奖按钮无关**;之前怀疑"开箱读箱子drop"已排除——主抽奖走服务端 PrizeDraw 读奖池。
