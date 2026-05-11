# 表编号 → 页签速查

> **配置前必读**: 每张表的完整字段定义、JSON 格式、跨表追踪链见 → [table-schema.md](table-schema.md)

| 编号 | 页签 |
|------|------|
| 1011 | cn（i18n 全语言）|
| 1111 | item |
| 1118 | building |
| 1120 | drop |
| 1168 | get_access_group（**7列，读参考行必须用 A:H**）|
| 1211 | buff |
| 1387 | city_effect |
| 1511 | display_key |
| 1920 | hero_data |
| 2011 | iap_config（A_STR_constant，IAP 产品定义）|
| 2013 | iap_config（道具/礼包内容）|
| 2111 | activity_calendar |
| 2112 | activity_config |
| 2115 | activity_task |
| 2116 | activity_item_exchange |
| 2118 | activity_rank_rewards |
| 2119 | activity_ui_template |
| 2120 | activity_ui_module |
| 2121 | activity_special |
| 2122 | activity_rank_rule |
| 2124 | 掉落表（drop）— 通用掉落配置，随机礼包是其中一种模块 |
| 2135 | activity_package |
| 2136 | activity_cycle_period |
| 2138 | activity_proto_module |
| 2141 | activity_without_gacha_pool |
| 2142 | activity_without_gacha_reward |
| 2154 | activity_without_gacha_floor（爬塔层数配置，含 use_item 每层用的道具）|
| 2160 | activity_metro_grade |
| 2168 | activity_hud_entries |
| 2169 | activity_hud_entry_style |
| 3510 | metro_minigame_activity_group — 挖矿活动组装枢纽（详见下方 35xx 章节）|
| 3516 | metro_minigame_level — 子关地图 |
| 3517 | metro_minigame_level_group — 关卡分组 |
| 3518 | metro_minigame_research — 科研树 |
| 3525 | metro_minigame_hero_data — 矿洞英雄 |

## 常用 SheetID（P2 项目）

| 编号 | SheetID | gsheet_query 别名 |
|------|---------|------------------|
| 1111 | 1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws | `1111_P2` |
| 1118 | 1ES3syKlMbqqmZezWFCzwL0elIdrgvisiUTnBwJNRHrk | `1118_dev` |
| 1168 | 1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA | `1168_dev` |
| 1511 | 1Zs5l2MPz9nTDSV6VsAZAFsGRxRW0nLsGj2u1lF3PBQY | `1511_dev` |
| 2011 | 1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc | `2011_dev` |
| 2013 | 1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY | `2013_dev` |
| 2112 | 1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E | `2112_dev` |
| 2115 | 1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY | `2115_dev` |
| 2154 | 1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo | — |
| 2118 | 1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M | — |
| 2120 | 1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0 | — |
| 2121 | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | — |
| 2135 | 1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc | `2135_dev` |
| 2148 | 1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw | `2148_dev` |
| 2171 | 1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4 | `2171_dev` |

## 1168 get_access_group 字段说明

**⚠️ 共 7 列（A~G），读参考行必须用 `A:H` 范围，用 `A:F` 会漏掉最后一列。**

| 列 | 字段名 | 说明 |
|----|--------|------|
| A | `A_INT_id` | 行 ID，格式 `1168XXXX`，当前最大 `11684900` |
| B | `S_STR_comment` | 备注（中文说明） |
| C | `A_STR_constant` | 常量名（通常为空） |
| D | `C_STR_item_label` | 道具标识，4010/4011 皮肤填对应的颜色 ID（如 `40106201`） |
| E | `C_ARR_access_group` | 获取途径数组，机甲皮肤通常 `[{"id":11531001,"args":["2112活动ID"]}]` |
| F | `C_MAP_lc_name` | 显示名，固定填 `{"typ":"lc","txt":"LC_ITEM_item_cap"}` |
| G | `C_MAP_label_name` | 标签名，固定填 `{}` |

**新增机甲皮肤行模板：**
```
["新ID", "机甲名-皮肤名", "", "4011颜色ID", "[{\"id\":11531001,\"args\":[\"2112活动ID\"]}]", "{\"typ\":\"lc\",\"txt\":\"LC_ITEM_item_cap\"}", "{}"]
```

**⚠️ 踩坑记录（2026-04-28）**：读参考行时用了 `A664:F664`（只查6列），漏掉 G 列 `C_MAP_label_name`。写入时 G 列靠 Google Sheets 自动继承了 `{}`，碰巧正确，但属于隐患。**根本原因**：查参考行范围不够宽，正确做法是始终用 `A:H` 及以上。

---

## 机甲主题皮肤配置（4010 + 4011 + 1111）

| 表号 | tab 名 | SheetID |
|------|--------|---------|
| 4010 | mecha_skin | `1KWNZXyhUlI4UyREfENWe7yZvHSxWgpEtMv5T10G2X7w` |
| 4011 | **mache_colour**（拼写有误，非 mecha）| `1nl7w3Vfm1Wgv2ih5xKcPdLaIwfxv-ArWztVUSBlPnKY` |

- 皮肤 ID 编码：`401 0 [mech_num] [group] 01`，巨象 mech_num=6
- 颜色 ID 编码：`401 1 [mech_num] [group] 01`
- 3个 URL 字段在 4011：`gacha_banner_url`[21]、`gacha_reward_url`[22]、`gacha_select_url`[23]
- 模型 DK：填 4010 col[3][5] + 4011 col[5]；图标 DK：填 4010 col[11] + 4011 col[14] + 1111 col[6]
- 配置生成器：`cases/mecha_skin_elephant_jungle/config-output.html`
- 完整运维文档：`cases/mecha_skin_elephant_jungle/progress.md`

---

## 新版机甲抽奖（5月节日，金字塔爬塔）关键信息

| 项 | 值 |
|----|-----|
| 2112 activity_id | **21127807**（constant: event_hallo_mecha_gacha_2026）|
| 2112 注释 | 机甲gacha-节日自选通用-新版 |
| 2154 爬塔层数配置 | 每层 use_item = **11112175**（惊喜锤），消耗 1/2/5/8/12/16 |
| 惊喜锤道具 | ID=**11112175**, display_key=**15119532**, lc_name=`LC_ITEM_mecha_gacha_item` |
| 惊喜锤翻译（TM） | Lucky Hammer / Marteau Chanceux / Glückshammer / ラッキーハンマー / 행운의 망치 |
| 2121 升层参数行 | **21219608**: type=`floor_gacha_upgrade_floor`, reward=星星进度(111111020), array=[1,7,12,16] |
| 2111 activity_calendar 行 | **21117153** → 21127807（2026-04-10 新增）|
| 2111 activity_calendar 行 | **21117154** → 21129005 拓荒节卡包BP（2026-04-30 新增）|
| 2130 battle_pass SheetID | `1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M`，tab `activity_battle_pass` |
| 2131 battle_pass_level SheetID | `1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs` |

### 节日卡包BP IAP链路
```
2112 活动(21127803/21129005) → battle_pass组件(21301541)
  → 2130 A_MAP_pkg → IAP 2013(2013450086) → 2011(2011380052)
    → 条件: actv_base_id=21127803（通用，所有节日版本共享）
```

### 永久增产特权道具（item_buff 类，彩蛋节卡册）

| 道具 ID | 注释 | buff ID | buff source | lc_desc key |
|---------|------|---------|-------------|-------------|
| 11114464 | 永久资源增产特权15%-钢材 | 121140941 (arg1=0.15) | 12136009（礼包） | must_have_energy_item_desc6 |
| 11114465 | 永久资源增产特权20%-钢材 | **121141501** (arg1=0.2) | **12136017（节日卡册）** | **must_have_energy_item_desc8** |

- 新增 1011 ITEM key：`must_have_energy_item_desc8`（ID:1011144342）= "永久提升钢铁产出速度20%"
- 新增 1211 buff：`121141501`，category=12121002（IronProduct），source=12136017
- 1213 source 12136017 = 来源节日卡册（LC_EVENT_fes_card_collection_album）
- ⚠️ item_buff 类同名道具不同数值（15%/20%）可能共用同一 lc_desc key，改配置时必须检查 lc_desc 是否匹配实际 arg1

### 2182 coinpusher 表（推币机怪物配置）
- SheetID: `17fo14HLBiOCfkHhDooyIMudTrGCoDg15BvRdBcgIE2M`
- 当前使用页签: `小丑版本`
- 当前使用行: `21820009`（小丑宝箱怪）/ `21820008`（套装版本）
- 关键字段 `A_ARR_MonsterDrop`:
  - `id` = 币种道具 ID（如 11112721=银币, 11112722=金币）
  - `val` = 触发掉落的道具 ID（**不是数量！** 如 11112724=币堆道具）
  - `arg2` = 实际触发数量数组（如 [40,50,60] 对应不同 schema）
- ⚠️ 客户端容易把 `val`（道具ID）误当数量显示到规则文案里

### X2 项目配置

| 表 | SheetID | 备注 |
|----|---------|------|
| 配置索引 | `1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc` | tab: `fw_gsheet_config` |
| 1011 i18n | `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg` | EVENT tab 超过 7200 行，搜索需分段 |
| 1011 国服 i18n | `1JLYxVequku6nBW4kJUkAfnJCFv7p_M7nsANSctpXpAE` | — |
| 2011 iap_config | `1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY` | QA tab: `iap_config_x2qa`；活动专属 tab 如 `26挖蛋` |
| 2013 iap_template | `1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E` | QA tab: `iap_template_x2(qa)` |
| 2112 activity_config | `1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo` | — |
| 2115 activity_task | `1rXVuN_j2C_4D1e29KhbpRt0AJOy2w681MPv_gMu3TgM` | tab: `activity_task_master（线上）`，含中文需用 Python API；H列=`A_ARR_reward` |
| 2135 activity_package | `1Agp8e-FfSz0ixLIVFwUIjvlkU69gB7D39URWnjzRvbs` | 活动 tab 如 `26巨猿` |

- X2 i18n 暂存区 tab: `AI翻译页签`（sheetId=338656897）
- ⚠️ gws CLI 无法直接访问含中文的 tab 名（如 `26挖蛋`、`activity_task_master（线上）`），需通过 gid 或 Python API

#### X2 占星节卡包 item ID（2115 奖励用）
| item_id | 名称 | LC Key |
|---------|------|--------|
| 11114014 | ~~圣诞1-2星活动卡包~~（旧，已替换） | lc_item_card_pack_name_9 |
| 11114016 | ~~圣诞2-3星活动卡包~~（旧，已替换） | lc_item_card_pack_name_11 |
| **11114017** | 占星节1-2星活动卡包 | lc_item_card_pack_name_12 |
| **11114018** | 占星节1-3星活动卡包 | lc_item_card_pack_name_13 |
| **11114019** | 占星节2-3星活动卡包 | lc_item_card_pack_name_14 |

占星节 2115 task group：
- `2115115`：gacha积分任务（9行，task_id 2115111083-2115111091）
- `2115116`：七日任务（50行，task_id 2115111093-2115111142）

#### X2 节日投放检查规则
- 看到“XX节 / 2026 / 节日”相关活动、礼包、BP、限时抢购时，不能只查 `2112` 活动组件和 `2135` 礼包行是否存在，必须继续检查对应投放内容是否同主题。
- 检查链路：`2112.activity_components.package` → `2135.A_INT_iap` → `2011.A_MAP_time_info.actv_base_id` / `A_ARR_iap_status` → `2013.A_INT_config_id` / `A_ARR_*_items` → `1111 item` 道具注释和 LC key。
- 判断标准：`2011` 的 `actv_base_id` 要挂到当前活动底座；`2013` 奖励道具不能混入其他节日专属投放（如夏日节 BP / gacha 道具）。大富翁类道具可为通用复用，但 BP 道具必须检查是否为当前节日对应 BP。
- `2135 activity_package` 的 `A` 列是 `p2_title`，真正 ID 在 `B` 列。新增行时不要用 `len(values)+1` 或按表格尾部空白网格写入；必须检查 `B/A_INT_id` 的连续区间。如果中间有空行再接旧数据，需要插行后把新增行放进连续区，避免 `fwcli` 在空 ID 行解析失败。
- 写入/复查 `2013 iap_template` 时，范围至少到 `AE` 列，`AE = A_INT_country_use_type`。不要用 `A:AD` 当作全字段范围，否则复查会漏掉国家使用类型列。
- 例：`21127357` 占星节-2026-限时抢购触发链可挂到 `21127223`，但 `2013` 模板含 `11119453` (`LC_ITEM_summer_2025_bp_item_title`) / `11119473` (`LC_ITEM_summer_2025_gacha_item_title`)，属于夏日节 BP/gacha 投放混入，需要确认或替换。

#### X2 26挖蛋活动（wonder_egg）LC key
- `wonder_egg_pkg`（ID: 1011087409）→ CN: 能量充盈礼包，EN: ENERGY FULL PACK
- `wonder_egg_pkg_desc`（ID: 1011087410）→ CN: 使用稳定剂开启宝盒以获得所有奖励！

### 2171 装饰技能表 (event_decroation_skill)
- SheetID: `1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4`，tab: `装饰技能`
- 追踪链: 2148(event_decoration_level) 的 `A_INT_decroation_paint_skill` → 2171 的 `A_INT_id`
- 常见 BUG: lc_name 引用了错误的 key（如 _attack_name 和 _increase_name 混用）
- 验证方法: 查 1211 buff 表确认实际 buff 效果（如 12117029="骑兵受到射手伤害减少"），再对比 LC 文案是否匹配

### 推币机活动 LC key 命名约定
- 推币机相关 LC key 在 i18n 表中**不带 `LC_` 前缀**，统一以 `coin_pusher_xxx` 开头
- 例：`coin_pusher_click_tips`、`coin_pusher_ultimate_box_received_tip`
- 游戏代码引用时会自动加 `LC_` 前缀（如 `LC_coin_pusher_xxx` 或 `LC_minigame_coin_pusher_xxx`）
- 创建新 key 时直接命名为 `coin_pusher_xxx`，不要写 `LC_` 也不要写 `minigame_`

### 图标一致性追踪点（处理 HUD/按钮/礼包图标不一致类 BUG）
一个 gacha 活动里锤子/道具图标会在多处引用，BUG "图标不一致" 需要检查：
1. **1111 item** — 道具本身的 `display_key`（如惊喜锤 15119532）
2. **2168 activity_hud_entries / 2169 activity_hud_entry_style** — HUD 右上角显示样式
3. **2119 activity_ui_template / 2120 activity_ui_module** — 活动界面内的按钮图标
4. **礼包相关配置（2135 activity_package）** — 礼包里的道具图标引用
追踪思路：以 1111 里的 display_key 为基准，检查 2-4 处引用的图标是否都指向同一个 display_key 或资源。

## 1111 item 表常用字段

| 列 | 字段名 | 说明 |
|----|--------|------|
| col[5] | `C_INT_display_order` | 显示排序 |
| col[16] | `C_ARR_display_labels` | 道具在客户端的显示分类，数组，一个道具可显示在多个分类中。**控制道具是否在背包显示**。常见值：`bag_other`(背包-其他)、`bag_resource`(背包-资源)等 |
| col[17] | `A_ARR_use_labels` | 道具使用标签，数组，**也控制道具是否在背包显示**。常见值：`bag`(背包可见)等 |
| col[20] | `S_INT_use_now` | 获得后立即使用，0=否 1=是 |

### 背包显示控制
道具不进背包需要**同时**改两个字段：
1. `C_ARR_display_labels` — 去掉 `bag_xxx` 相关值（如 `bag_other`）
2. `A_ARR_use_labels` — 去掉 `bag`
两个字段都控制背包显示，缺一不可。

---

## P2 挖矿系统 35xx 表清单（metro_minigame）

> 27 张表，归属 fw_gsheet_config 的「地下矿场」分类。配活动关卡时重点关注 3510/3516/3517/3518/3525。

### 核心配置链

```
3510 activity_group  →  3517 level_group  →  3516 level (子关地图)
     ├─ research     →  3518 research
     ├─ hero_data    →  3525 hero_data
     └─ iap_scene    →  2013 iap_template
```

### 完整表清单

| 编号 | 表名 | SheetID | 说明 |
|------|------|---------|------|
| **3510** | metro_minigame_activity_group | `1E-h-mktZ291LuyPHuwYPLYiW3XfmsyNaq819wilHYk4` | 活动组装枢纽（level_group + research + hero + iap）|
| 3511 | metro_minigame_employ_level | `1hkONbz8jp08BFl8zYCssJ5aHk8Uan8vaGI4eE11VFyg` | 召唤装备等级 |
| 3512 | metro_minigame_employ_times | `1Cw1VUc0AtP3BKDYQaznL-lKtSqkna5ePEcB8riEpDnQ` | 召唤次数 |
| 3513 | metro_minigame_map_units | `185AaYL1BStcHUtSCOHPpmxfSyjyALuTF2E3gUurBOvU` | 地图单元类型 (35130xxx) |
| 3514 | metro_minigame_rock_drop | `1SIkgA0K9ZDm-nEtXjbNpk8l8UB-4V9XA0QCyM8iVISU` | 矿石掉落 (35140xxx) |
| 3515 | metro_minigame_production | `1vCXY0VqS_eliuBDJYyUO5u_hKAnbP-kC14m9c9Dcam0` | 生产槽位 (351500xxx) |
| **3516** | metro_minigame_level | `1jKEzkMLphbaNK1QOwZ4Qhu3cbUPGsunm4WBxSi51UD4` | 子关地图（1088行，35160xxx~35165xxxx）|
| **3517** | metro_minigame_level_group | `1x4aOdaHemkGlrLpemjblJP8lmGrv4xNgDpoF9zfT4C4` | 关卡分组（377行，35170xxx~35171xxx）|
| **3518** | metro_minigame_research | `1jcj0FN1V04whz386qBaunEyPkfhHFNty-6R6b1GeiBw` | 科研树 (3518xxx) |
| 3521 | metro_minigame_buff | `1haCZl_AJuTT1K_HydMR1JBw1GI4iVBSKbqpi3BCRQxo` | buff (35212xxx) |
| 3522 | metro_minigame_buff_category | `1YN-mwHLvXmDa9uF3IxwqGj3800HXKI84kAeU3b3T5Y4` | buff 分类 |
| 3523 | metro_minigame_buff_source | `1WcBzKwvWPYtX_IdPQ2jgELIP09YXFcxfF0glOKMayGM` | buff 来源 |
| 3524 | metro_minigame_buff_property | `1ukoiNYhTLA12-bR0HgeYQLsdSZ3OQXGK1kbcYMsa6GQ` | buff 属性 |
| **3525** | metro_minigame_hero_data | `119EoiprKhK1jn5SmnyCPtN1_uR9AEs_iDVgTr5GvZQo` | 矿洞英雄 (35251xxx~35253xxx) |
| 3526 | metro_minigame_hero_level | `1jw7eTEssnXW0aOubXIJhFLpLYP3pNqPztBX8b05amDc` | 英雄成长 |
| 3527 | metro_minigame_hero_skill | `1WpAFVoJyBpHHDjxOAEzc4kjebFTfd8bBwr_InttqL7E` | 英雄技能 (3527xxx) |
| 3528 | metro_minigame_shooting_level | `1FsBhDPlRsgfd9JmphXsD74ylIFBdPaFiVizQsb58ZHc` | 射击BOSS关卡 (35280xxx) |
| 3529 | metro_minigame_shooting_npc | `13DdLOWsYcJSPw5hOm8A6bf196HrFimyy4JrSQ7EkcF4` | 射击NPC |
| 3530 | metro_minigame_shooting_weapon | `1DJEr6x0TNZIK35BP7GFY_pX-ryhj0xJpAlNiu5puPls` | 射击武器 |
| 3531 | metro_minigame_shooting_skill | `1-6cEEBLVkv2i-lgOl7oVgupKpmtAxd4T_FEMOmw6yGE` | 射击技能 |
| 3532 | shooting_teach | `112hIZZyKsNPD89DMUhvD4C0j1osLAKdLqGTuxTwqWLo` | 射击教学 |
| 3533 | metro_minigame_hero_worker_level | `1d_0BRPN5LmfnW4RxQWmRbUolUL44182dRb29FX61aYw` | 英雄矿工等级 |
| 3534 | metro_minigame_hero_worker_power | `1rB2PamntwRgY3yZYDtHQKbEH-ha9ziak1_tqJAELn6c` | 英雄矿工战力 |
| 3535 | metro_minigame_hero_worker_skill | `1k6ir9E-LFQ-B-c6aImB5HnVi8IFiqWDJNiDWqFTBVd4` | 英雄矿工技能 |
| 3540 | kvk_uw_metro_minigame_research | `1i3elpEO3TctaO_ZKz2mhjPZAxHE4zBWrLaU86y66JBM` | 地下世界科研 (3540xxx) |
| 3541 | metro_minigame_dragon_rock | `1WmH1ElPjeHM9v8mXVCHokU9WTCBSFYMtTr2ts3nh1SY` | 龙岩BP |
| 3542 | metro_minigame_bargain_iap_rock | `1TG2K3p3vKZf910qpl393LNp8ufkhpkQJBdFk_Hy0MZI` | 砍价IAP矿石 |

### 3510 ID 编码规则

- `35103[schema][月份循环编号]` — 节日循环活动，如 35103331 = schema3 + 4月循环第31期
- `3510[schema]1xxx` — 地下世界，如 351031001
- `3510[schema]2xxx` — 地下世界(第二组)
- `3510[schema]3xxx` — 地下世界(第三组)
- 三个 schema 的差异通常**只在 hero_data**（后 5 个英雄不同），level_group/research/iap 一般相同

### 3516 ID 分段

| 前缀 | 数量 | 含义 |
|------|------|------|
| 35160xxx | 283 | 主线关卡 (关卡1~99_3) |
| 35161xxx | 364 | 活动/循环关卡 (关卡100+ & 月循环) |
| 35162xxx | 108 | 地下矿脉 |
| 35163xxx | 108 | 原服地下 |
| 35164xxx | 108 | 循环地下 |
| 35165xxx | 116 | KVK 地下奇遇 |

### 26复活节活动关卡案例 (schema3: 35103331)

```
3510: 35103331 → level_group: [35171082, 35171083, 35171084, 35171085]
3517: 35171082 → [351610821, 351610822]         (关卡82, 2子关, scale=[38,9])
      35171083 → [351610831, 351610832, 351610833] (关卡83, 3子关, scale=[57,9])
      35171084 → [351610841, 351610842, 351610843] (关卡84, 3子关, scale=[57,9])
      35171085 → [351610851, 351610852, 351610853] (关卡85, 3子关, scale=[63,9])
3516: 11个子关，research_coef=1.556, hero_coef=5.333
      BOSS: 35130606/08/10/14/48/52，hero_power 从 60000 到 270000
```

---

未知表查索引：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F300"}'
```
