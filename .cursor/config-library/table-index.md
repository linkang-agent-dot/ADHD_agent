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
| 2160 | activity_metro_grade |
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
| 2118 | 1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M | — |
| 2120 | 1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0 | — |
| 2121 | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc | — |
| 2135 | 1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc | `2135_dev` |
| 2148 | 1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw | `2148_dev` |
| 2171 | 1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4 | `2171_dev` |

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
