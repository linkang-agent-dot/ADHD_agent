# 表编号 → 页签速查

| 编号 | 页签 |
|------|------|
| 1011 | cn（i18n 全语言）|
| 1111 | item |
| 1118 | building |
| 1120 | drop |
| 1168 | get_access_group |
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
| 2135 | activity_package |
| 2136 | activity_cycle_period |
| 2138 | activity_proto_module |
| 2141 | activity_without_gacha_pool |
| 2142 | activity_without_gacha_reward |
| 2154 | activity_without_gacha_floor（爬塔层数配置，含 use_item 每层用的道具）|
| 2160 | activity_metro_grade |
| 2168 | activity_hud_entries |
| 2169 | activity_hud_entry_style |

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

## 新版机甲抽奖（5月节日，金字塔爬塔）关键信息

| 项 | 值 |
|----|-----|
| 2112 activity_id | **21127807**（constant: event_hallo_mecha_gacha_2026）|
| 2112 注释 | 机甲gacha-节日自选通用-新版 |
| 2154 爬塔层数配置 | 每层 use_item = **11112175**（惊喜锤），消耗 1/2/5/8/12/16 |
| 惊喜锤道具 | ID=**11112175**, display_key=**15119532**, lc_name=`LC_ITEM_mecha_gacha_item` |
| 惊喜锤翻译（TM） | Lucky Hammer / Marteau Chanceux / Glückshammer / ラッキーハンマー / 행운의 망치 |
| 2111 activity_calendar 行 | **21117153** → 21127807（2026-04-10 新增）|

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

未知表查索引：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F300"}'
```
