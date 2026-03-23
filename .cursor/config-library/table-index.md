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

## 常用 SheetID

| 编号 | SheetID |
|------|---------|
| 1111 | 1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws |
| 1168 | 1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA |
| 2112 | 1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E |
| 2118 | 1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M |
| 2120 | 1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0 |
| 2121 | 1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc |

未知表查索引：
```powershell
$env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'
gws sheets spreadsheets values get --params '{"spreadsheetId": "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c", "range": "fw_gsheet_config!A1:F300"}'
```
