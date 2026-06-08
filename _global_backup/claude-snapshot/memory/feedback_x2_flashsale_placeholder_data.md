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
