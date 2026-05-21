# 配置表知识库（P2 / X2）

> 由 table-schema.md + table-index.md 合并而成。配活动/换皮前必读。
> JSON 字段必须紧凑无空格：`separators=(',',':')`

---

## 一、快速索引（P2）

| 编号 | 表名 | SheetID | QA/主页签 | 用途 |
|--------|------|---------|----------|------|
| 1011 | i18n | `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY` | 按类别分页签 | 客户端本地化文本 |
| 1111 | item | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | item | 道具表 |
| 1118 | building | `1ES3syKlMbqqmZezWFCzwL0elIdrgvisiUTnBwJNRHrk` | building | 建筑表（含装饰本体）|
| 1127 | building_build | `1Dlyk6JRGOYoVsSohfwXzbwN8wUvwlk1fGgBTzaDKtNw` | building_build | 建筑建造入口 |
| 1142 | avatar_frame | `1jBsZOuoMz3uwYHN-Tcotn8QPBgX5LYDpUHXVu2LzpiQ` | avatar_frame | 头像框配置 |
| 1168 | get_access_group | `1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA` | get_access_group | 获取途径组合（⚠️读需A:H） |
| 1173 | chat_skin | `1mKaHyDbToHVIV9iyOQPFbJ88pwnjGy5-GeiUvRZHPBg` | chat_skin | 聊天铭牌 |
| 1211 | buff | `1qqn6vjWJ30-TW-kXzN3Aa9eS1fyoTFwPSWdXyNZbauc` | buff | buff 定义 |
| 1387 | city_effect | `1AgFJmnMyuNoyQYQXMmNSBSQLoczM6RRtbfllYZSFBDA` | city_effect | 主城特效 |
| 1511 | display_key | `1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY` | display_key | 美术资源 DK |
| 2011 | iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | iap_config_QA | IAP 产品定义 |
| 2013 | iap_template | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | iap_template_QA | IAP 道具内容/价格 |
| 2024 | iap_custom_chest | `1jQSZKXz25Xl1Xps9o0x9SbkxKHkySb7mFr2pETGgF7c` | iap_custom_chest | 自选礼包坑位 |
| 2111 | activity_calendar | `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g` | activity_calendar_QA | 活动日历 |
| 2112 | activity_config | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | activity_config_qa | 活动总配置入口 |
| 2115 | activity_task | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | activity_task_QA | 任务配置 |
| 2116 | activity_item_exchange | `14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY` | activity_item_exchange | 道具兑换商店 |
| 2118 | activity_rank_rewards | `1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M` | activity_rank_rewards | 排名奖励 |
| 2119 | activity_ui_template | `1_o6R4_vPcl9PACt_-5RZUqG5mYnWTTN7aA_sruSXGeM` | activity_ui_template(qa) | 活动UI模板 |
| 2120 | activity_ui_module | `1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0` | — | 活动UI模块 |
| 2121 | activity_special | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | activity_special_QA | 特殊组件万能表 |
| 2122 | activity_rank_rule | `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M` | activity_rank_rule(QA) | 排行榜规则 |
| 2123 | activity_popwindow | `1Kanf7FuYHMzV0jTX6xBaG49H0svCOLaiJCtMrs1afO8` | — | 弹窗配置（非cumulate！）|
| 2124 | activity_drop | `1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA` | activity_drop | 掉落配置 |
| 2130 | activity_battle_pass | `1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M` | activity_battle_pass | BP通行证总配置 |
| 2131 | activity_battle_pass_level | `1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs` | activity_battle_pass_level | BP等级奖励 |
| 2135 | activity_package | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | activity_event_pkg | 活动礼包桥接表 |
| 2137 | activity_asset_retake | `1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y` | activity_asset_retake | 活动道具回收 |
| 2141 | activity_without_gacha_pool | `1E_T34i1eLC7F3hKlsLJVlizlu9aRhBY0vzMSNN1v5do` | — | 无底Gacha奖池 |
| 2142 | activity_without_gacha_reward | `1vGzggIww1jifGGqDGqzB1RgittK62gL_3-j5EW3_X3I` | — | 无底Gacha奖励 |
| 2148 | event_decoration_level | `1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw` | event_decroation_level | 装饰升级配置 |
| 2154 | activity_without_gacha_floor | `1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo` | activity_without_gacha_floor | 爬塔层数配置 |
| 2171 | event_decoration_skill | `1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4` | 装饰技能 | 装饰技能表 |
| 2182 | coinpusher | `17fo14HLBiOCfkHhDooyIMudTrGCoDg15BvRdBcgIE2M` | 小丑版本 | 推币机怪物配置 |

**集卡册专属（6xxx系）**

| 编号 | 表名 | SheetID | QA/主页签 | 用途 |
|--------|------|---------|----------|------|
| 6001 | card_gallary_book | `1T-8EtaenFTybZzKqeRtLGWNRWlaxcPIMQScvUCTY1Dc` | 节日卡册 | 集卡Book配置 |
| 6002 | card_gallary_group | `1H1Epc0EccCDrxGpgZoIyGlpDh4WaDviOQX-r41rSvhE` | 备用 | 集卡组配置 |
| 6003 | card_gallary_card | `1TiKSm3Z6AnbclrxDS4w9O4b-Vmz6MPhQU4ll7A42z2Y` | 备用 | 集卡卡片配置 |
| 6004 | card_gallary_store | `12hakUKbpey0bnhHl4VGN6dzNk2dkyy-MEVgEOzEx1ZM` | 节日卡册 | 集卡商店配置 |

**机甲皮肤专属**

| 编号 | tab 名 | SheetID |
|------|--------|---------|
| 4010 | mecha_skin | `1KWNZXyhUlI4UyREfENWe7yZvHSxWgpEtMv5T10G2X7w` |
| 4011 | mache_colour（拼写有误） | `1nl7w3Vfm1Wgv2ih5xKcPdLaIwfxv-ArWztVUSBlPnKY` |

---

## 1.5、X2 表 id_col + QA 页签速查（换皮脚本用）

> 2026拓荒节换皮踩坑后整理。脚本读行/分配 ID 时必须用正确的 id_col。

| 编号 | id_col | X2 QA/写入页签 | 备注 |
|------|--------|---------------|------|
| 1111 | 1 | item | |
| 2011 | 1 | iap_config_x2qa | |
| 2013 | 1 | iap_template_x2（qa）| |
| 2112 | 1 | activity_config_QA | |
| 2115 | **2** | activity_task_master（线上）| col[0]=p2_title, col[1]=group, **col[2]=id** |
| 2116 | **2** | activity_item_exchange（线上版本）| 同2115，col[2]=id |
| 2118 | **3** | activity_rank_rewards | col[1]=group, col[2]=comment, **col[3]=id** |
| 2121 | 1 | activity_special | |
| 2122 | **2** | activity_rank_rule（QA）| 同2115，col[2]=id |
| 2124 | 1 | activity_drop | |
| 2130 | 1 | activity_battle_pass（24新格式-dev）| |
| 2131 | 1 | ActivityBattlePassLevel（master）| |
| 2135 | 1 | activity_event_pkg（qa）| |
| 2137 | 1 | activity_asset_retake | |
| 1365 | 1 | march_effect | 行军特效外观表 `1euWfOkXNsn4sQwyRNaoCZ6-0_EGed9aToBUbDCOzi8w` |
| 1187 | 1 | FurnitureBuild | 家具/装饰放置表 `1lXRldN7kN_HsEYQ5FfNdawep23TD9J81Vj66yKRdjEk` |
| 2151 | 1 | activity_monopoly_gacha_map_QA | 大富翁地图 `1X9fu7V3JFd1ZKoisbLjDpR8SAfngKso6lWjZ0-eTudg` |

---

## 二、X2 SheetID 对照

> ⚠️ X2 gws CLI 无法直接访问含中文的 tab 名，需通过 gid 或 Python API
> ⚠️ X2 的 2171 是 ActivityCollaborateTask，与 P2（装饰技能）含义不同！

| 编号 | P2 SheetID | X2 SheetID |
|------|-----------|-----------|
| 配置总索引 | `1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c` | `1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc` |
| 1011 i18n | `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY` | `1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg` |
| 1011 国服 | — | `1JLYxVequku6nBW4kJUkAfnJCFv7p_M7nsANSctpXpAE` |
| 1111 item | `1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws` | `1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs` |
| 1142 avatar_frame | `1jBsZOuoMz3uwYHN-Tcotn8QPBgX5LYDpUHXVu2LzpiQ` | `1nNJqyNU1XaNnqburlcfq7x1TDjS4T4CPUao7605rQFU` |
| 1173 chat_skin | `1mKaHyDbToHVIV9iyOQPFbJ88pwnjGy5-GeiUvRZHPBg` | `1ysPLSMZ6zmDmCUcek5E5RJWlb3fAzjk_euwuJNJyjls` |
| 2011 iap_config | `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc` | `1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY` |
| 2013 iap_template | `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY` | `1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E` |
| 2111 activity_calendar | `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g` | `1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk` |
| 2112 activity_config | `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E` | `1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo` |
| 2115 activity_task | `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY` | `1rXVuN_j2C_4D1e29KhbpRt0AJOy2w681MPv_gMu3TgM` |
| 2116 activity_item_exchange | `14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY` | `1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA` |
| 2118 activity_rank_rewards | `1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M` | `1bAwu8A-N4j0Wub6wQQ2AImeB958gSaWV-XdU87k8u60` |
| 2119 activity_ui_template | `1_o6R4_vPcl9PACt_-5RZUqG5mYnWTTN7aA_sruSXGeM` | `1sjNrWq4DLGRQKvlWWgMxdJlGKd948jLPool_IjeRQBI` |
| 2120 activity_ui_module | `1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0` | `12XcfGDUEFks8FPIymhJQovpzaXoy5mivb3DQKZH2PSA` |
| 2121 activity_special | `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc` | `1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4` |
| 2122 activity_rank_rule | `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M` | `1P5bHlZdhuRlpYkJA6tvaZuK32V5RZFRvuQuuomMjiM4` |
| 2124 activity_drop | `1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA` | `11wgGaUdAG064VvyZAKZA-M6GO6WIBf2PP88yVmDlYjU` |
| 2130 activity_battle_pass | `1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M` | `1XfpgS-r7kTDk24t5mEE93uOy9u6wm_fub0txKMRDTwU` |
| 2131 activity_battle_pass_level | `1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs` | `1CFoDVfINRdcjpuGpKbNz9f3WyFxIHW5dbayQDJy5evA` |
| 2135 activity_package | `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc` | `1Agp8e-FfSz0ixLIVFwUIjvlkU69gB7D39URWnjzRvbs` |
| 2137 activity_asset_retake | `1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y` | `1vSQa-CuzSyziwTV5ynPmB8HxE2SXNnFxQ-eKQiWlNUY` |
| 2141 without_gacha_pool | `1E_T34i1eLC7F3hKlsLJVlizlu9aRhBY0vzMSNN1v5do` | `1YKhyxqfyR3ywIYM8JdeHGvJUX1iXv2nP7ZbwEluMeNI` |
| 2142 without_gacha_reward | `1vGzggIww1jifGGqDGqzB1RgittK62gL_3-j5EW3_X3I` | `1GxDhto0jjrV-WC9GCyq6jjqImkFlzKKyLm-xNRmXos0` |
| 2148 event_decoration_level | `1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw` | `1Uh29AcDPzn2e7YGg24XdaNmZwQ2tklHJEs25lmOgDOI` |
| 2154 without_gacha_floor | `1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo` | `11dwwCqEFFZ3FzG8DMoVU0oL7TXEpDzpKhE9wW9_krwY` |
| 2171 P2=event_decoration_skill | `1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4` | ⚠️ X2 尚未建装饰技能表，现有 2171 是 ActivityCollaborateTask（协作任务），用途完全不同，待 X2 建表后单独补充 |

**X2 集卡册专属（1108/1107/1123/1109）**

| 编号 | 名称 | X2 SheetID | 写入 Tab | GID |
|------|------|-----------|----------|-----|
| 1108 | CardGallaryBook | `1yeFJwufv9QZBOHAIifHTfzyYhG0Fy9SQcfDoGLrzir0` | CardGallaryGroup（注：tab名有误，内容是Book）| 65753380 |
| 1107 | CardGallaryGroup | `1w-hmQGDu86TxrHGirvhQoaoniUjJA11t1XxCPDE5ylA` | CardGallaryGroup | 887412445 |
| 1123 | CardGallary | `1Dlg3r30Q7q19NKWcTHP-orYs7UYXs2TmV_V0xHGexMc` | CardGallary | 593941196 |
| 1109 | CardGallaryStore | `1zL0xNJwVQK95r71SDkIWEvZHp8ERFghkIsyyQ92HdZY` | CardGallaryStore | 0 |

> ⚠️ 追加到1123表末尾时用 appendDimension（不用 insertDimension），避免 "startIndex must be less than grid size" 错误

---

## 三、组件路由规则（核心）

**规则：组件 ID 前4位 = 子配置表编号**

| 组件 typ | 前4位→表 | 目标表 |
|---------|---------|-------|
| task | 2115 | activity_task |
| package | 2135 | activity_package → 2011 → 2013 |
| exchange / item_exchange | 2116 | activity_item_exchange（按 group 关联）|
| rank | 2122 | activity_rank_rule → 2118 |
| drop | 2124 | activity_drop |
| special / discount / jump_link / cost / buff 等 | 2121 | activity_special |
| battle_pass | 2130 | activity_battle_pass → 2131(等级奖励) |
| cross_progress | 直接 2011 ID | iap_config |
| bp_rank_item | 直接 1111 ID | item |

### 间接引用表（不在 components 里，但换皮必须检查）

| 表 | 关联方式 | 何时需要新建 |
|---|---------|------------|
| **2141** without_gacha_pool | `activity` 字段绑 2112 活动 ID | 有 Gacha 抽奖（主城皮肤gacha等）|
| **2142** without_gacha_reward | `group` 字段被 2141.drop 引用 | 同上，注意页签可能带后缀（天赋投放活动）|
| **2024** iap_custom_chest | `template_id` 字段绑 2013 ID | 有周卡/自选礼包 |
| **2151** monopoly_gacha_map | `monopoly_gacha_map` 组件直接引用 | 有大富翁活动（可复用旧地图）|
| **1365** march_effect | 1111 行军道具的外显 ID 引用 | 有新行军特效 |
| **1187** FurnitureBuild | 1111 装饰道具的 holiday_statue 引用 | 有装饰品 |
| **2011.iap_status.drop** | 2011 行内 JSON 引用 2124 drop ID | 有随机礼包（Gacha 礼包等）|
| **1111.category_param** | 道具行内 JSON 引用 2124/2013 ID | 金蛋道具(→2124)、周卡解锁(→2013) |
| **2121.expr/status** | 组件行内 JSON 引用 2115/2124/2011 ID | wonder_egg_drop(→2124)、discount(→2011)、task_group(→2115) |
| **2122.score_rule.ids** | 排名规则引用所有节日 2011 ID | 累充排名：每新增 2011 必须加入 |
| floor_gacha | 2154 | activity_without_gacha_floor |
| battle_pass | 2130 | activity_battle_pass → 2131 |
| accumulate | 2123 | activity_accumulate |
| retake | 2137 | activity_asset_retake |
| cross_progress | **直接是 2011 ID** | iap_config（不遵循前4位规则）|
| bp_rank_item | **直接是 1111 ID** | item（不遵循前4位规则）|

---

## 四、追踪链总览

```
2112 activity_config（活动总入口）
 ├── 2111 activity_calendar（后台开启控制）
 ├── 2115 activity_task（任务）
 ├── 2116 activity_item_exchange（兑换商店，按group关联）
 ├── 2121 activity_special（特殊组件，297种type）
 │    ├── discount → 2011 → 2013（礼包链路）
 │    └── jump_link → 2121.expr → 1168 get_access_group
 ├── 2124 activity_drop（掉落）
 ├── 2135 activity_package → 2011 → 2013（礼包主链路）
 │    └── random_pkg → 2011.iap_status → 2124（随机礼包奖池）
 ├── 2130 activity_battle_pass → 2131（BP通行证）
 ├── 2122 activity_rank_rule → 2118 activity_rank_rewards（排行榜）
 ├── 2137 activity_asset_retake（道具回收）
 ├── 2119/2120 activity_ui_template/module（UI模板）
 └── 2154 activity_without_gacha_floor → 2142 → (2141)（爬塔）

1111 item（道具）
 ├── C_INT_display_key → 1511（图标资源）
 ├── A_MAP_lc_name → 1011（本地化）
 └── A_MAP_category_param.effect → 各种效果（avatar_frame/holiday_statue等）

装饰物（四表联动）
 1111(解锁道具) → 2148(升级规则) → 1118(建筑本体)
                                  ↑
                           1127(建造入口)

铭牌（四表联动）
 1511(x2) → 1111(chat_skin道具) → 1173(chat_skin配置) → 1011(i18n)

集卡册 P2（6xxx 独立表系）
 6001(Book) → 6002(Group，含卡ID列表) → 6003(Card)
 6004(Shop) → 1111(卡包道具) → category_param 指定 6001+6002

集卡册 X2（1108/1107/1123/1109，与 P2 完全不同）
 1108 CardGallaryBook（书）
   ├── GroupID → 1107 CardGallaryGroup（9组）
   │    └── CardIDs → 1123 CardGallary（每组6张，共54张）
   │         └── DisplayKey → 1511 Portrait DK
   ├── CardPackID → 1111（卡包道具 11114017/18/19）
   │    └── drop→cardquality 控制星级，random_add 指定 book ID
   ├── OpenReq → actvstart: 2112活动ID
   ├── DisplayKey/1/2/3 → 1511（书图标/主题/顶板/底板）
   └── FXDisplayKey → 1511（特效，可复用已有如圣诞 1511020681）

 1109 CardGallaryStore（商店）
   └── item → 1111卡包，购买条件 actvend，货币 rss（星尘）

 i18n → 1011：组名(9) + 卡名(54) + 卡包名/描述(各3)
 案例：X2 2026占星节，book=11081003，group=11073001–009，card=11234001–086

 ⚠️ X2 与 P2 表号完全不同（1108 vs 6001），不能复用
 ⚠️ 1108.FXDisplayKey 容易漏填，参考行必须逐列对比

掉落转付费（drop_topay，三活动联动）
 2111 activity_calendar（3条日历，分别触发3个2112）
   ├── 211110567 → 21127361 主活动
   ├── 211110568 → 21127359 掉落活动
   └── 211110569 → 21127360 礼包活动

 主活动 2112:21127361 → components:
   ├── actv_links (2121) — 关联掉落/礼包活动入口
   ├── drop_topay_show / drop_topay (2121) — 掉落转付费展示/逻辑
   ├── new_progress (2121:212100319–212100498) — 进度条
   ├── retake (2137:21371255–21371258) — 道具回收
   └── exchange (2116:21161748–21161757) — 兑换商店

 掉落活动 2112:21127359 → components.drop:
   └── 2124:21241917–21241923

 礼包活动 2112:21127360 → components.discount:
   └── 2121:212101117
        └── A_ARR_status → 2011:2011920111（⚠️不走2135，直连2011）
             ├── A_MAP_time_info.actv_id → 21127360（必须绑当前礼包活动）
             ├── A_ARR_iap_status.recharge_actv → 211200093（累充归属，必须确认）
             └── 2013:2013920111–2013920114（4档礼包模板）

 ⚠️ 关键区别：礼包不走 2135→2011，而是 2121(discount)→2011→2013 直连
 ⚠️ 2011.time_info 必须绑当前礼包活动ID，不能沿用模板
 ⚠️ 2011.iap_status.recharge_actv 必须确认归属活动，不能凭经验复用
 案例来源：X2 2026占星节 drop_topay 模块

每日Gacha礼包 / 节日付费礼包（标准2135链路 + 累充归属 + 周付费率）
 2112:21127355 → components:
   ├── package (×5) → 2135:21353117–21353121
   │    └── A_INT_iap → 2011:2011920106–2011920110
   │         ├── A_MAP_time_info.actv_id → 21127355（必须绑当前活动）
   │         ├── A_ARR_iap_status.recharge_actv → 211200213（累充归属，不是夏日节的211200093）
   │         └── 2013:2013920102–2013920106
   │              ├── A_INT_config_id → 对应 2011
   │              └── 礼包内容含当前节日道具 11119497
   ├── weekly_pay_ratio → 2121:212101116
   │    └── reward → 1111:11119553（item_select_box）
   │         └── 真实奖励 → 11119497 ×50（必须追到这层）
   └── task → 2115:211551456

 ⚠️ 2135→2011→2013 必须同时新建，不能分批，否则中间状态会走旧链路
 ⚠️ recharge_actv 容易误挂到旧节日（本次误挂夏日节 211200093），写完后搜索旧 ID 确认无残留
 ⚠️ weekly_pay_ratio 要追3层：2121→1111(select_box)→真实奖励道具
 ⚠️ 同批 2011（2011920100–110）统一修正 recharge_actv，不能只改新增行
 案例来源：X2 2026占星节 每日gacha礼包模块

限时抢购（flash_sale，2135链路 + 2121 flash_sale_* 特殊组件）
 2112:21127357 → components.package:
   └── 2135:213521205–213521213（9档）
        └── A_INT_iap → 2011:2011920112–2011920119
             ├── A_MAP_time_info.actv_base_id → 21127223（活动底座，注意是 base_id）
             ├── A_ARR_iap_status.recharge_actv → 211200213
             └── 2013:2013920115–2013920122
                  └── 节日道具替换：11119453→11119497，11119473→11119517

 2121 限时抢购特殊组件（必须同步检查，不能只看 2112.components）：
   ├── 21217033 flash_sale_gacha → 引用 2013920115–122（与礼包内容对齐）
   ├── 21217034 flash_sale_popup → 引用 2135:213521211/212（弹窗礼包）
   └── 21217035 flash_sale_raffle → 引用新 2135 礼包

 ⚠️ 2121 flash_sale_* 是隐藏引用层，只看 2112.components 会完全漏掉
 ⚠️ 节日道具区分：BP/gacha/节日专属投放道具必须换当前节日，大富翁类通用道具可保留
 ⚠️ 2013 实际到 AE 列（A_INT_country_use_type），不能只写/查到 AD
 ⚠️ 2135 中间有空行时不能用 len(values)+1 定位，必须保证 B 列 ID 连续，否则 fwcli 解析失败
 案例来源：X2 2026占星节 限时抢购模块

Wonder 砸金蛋追踪链（C2 补充）
 2112 → components:
   ├── wonder_egg_drop (2121) → expr.args 内含 7 个 2124 drop ID
   │    └── 2124 掉落配置：每级金蛋的随机/全量奖池（含节日 BP 道具）
   ├── festival_wonder (2121) → reward 含节日 BP 道具
   ├── task (2115) → 7 个金蛋任务，reward 含金蛋道具
   ├── buff (2121) × 3 → 积分翻倍
   ├── task_group (2121) → 引用 2115 任务 ID 列表
   ├── create_entity × 80+ → 怪物实体（通用，不换）
   ├── rank (2122) → 排名规则
   ├── package (2135) → 砸蛋锤礼包 → 2011 → 2013
   └── jump_link (2121) → 跳转

BP 通行证追踪链（C2 补充）
 2112 → components:
   ├── battle_pass (2130) → BP 通行证主配置
   │    ├── QualityUpItem → 1111 通行证道具（初级/高级）
   │    ├── LevelUpItem → 1111 BP 经验道具
   │    └── 2131 BP 等级奖励（25行，通过 BpID 关联）
   │         └── FreeRewards/PayRewards 含节日道具
   ├── rank (2122) → 排名规则
   │    ├── score_rule.ids → 当前节日全部 2011 ID 列表
   │    └── rank_components → 2118 排名奖励 group
   │         └── 2118 7 档排名奖励（含行军特效道具）
   ├── retake (2137) → BP 道具回收
   ├── jump_link (2121) → 跳转
   ├── bp_rank_item → 1111 行军特效道具（直接引用，不走子表）
   └── fes_module → 节日模块（通用，不换）

行军特效外观表（C3 补充）
 1365 march_effect — `1euWfOkXNsn4sQwyRNaoCZ6-0_EGed9aToBUbDCOzi8w`
   ├── 18 列：id/comment/class/DK/effect_key/order/lc/status_active/innate_effect/awards/items/npc_troop_id/show_afterimage/show_type/preview/country_use_type
   ├── items 列含行军特效道具 ID 列表（1天~永久 6 个）
   └── ⚠️ 克隆时必须全列复制，INT 列为空会导致 fwcli 报错

FurnitureBuild 家具表（C3 补充）
 1187 FurnitureBuild — `1lXRldN7kN_HsEYQ5FfNdawep23TD9J81Vj66yKRdjEk`
   ├── FurnitureIds 列含家具模型 ID（需美术提供）
   └── 拓荒节需 7 行：装饰物/地板/墙纸/墙饰×3/柜台

大富翁地图表（C3 补充）
 2151 activity_monopoly_gacha_map — `1X9fu7V3JFd1ZKoisbLjDpR8SAfngKso6lWjZ0-eTudg`
   ├── use_item 列含骰子道具
   └── dice 列含骰子配置 ID

弹珠 Gacha（noumenon_gacha，2121 special 系）
 2112 → components:
   ├── high_exchange_shop (2121 type) — 高级兑换商店参数
   ├── noumenon_gacha_exchange_map (2121 type) — 地图奖励区分
   ├── noumenon_gacha_exchange_welfare (2121 type) — 福利关参数
   ├── cost (2121 type) — 消耗配置
   ├── item_exchange → 2116 — 普通券/高级券奖励（按 group 关联）
   └── package → 2135 → 2011 → 2013 — 礼包链路
```

---

## 五、各表字段 Schema

> **重要：列位置（A/B/C）因项目（P2/X2）和版本而异，新功能会追加列。**
> **Schema 只记录字段名和语义，列位置必须运行时读表头确认。**
> 操作时先读第1行表头，按字段名定位列，不要硬编码列字母。

### 2011 iap_config — IAP 产品定义（P2/X2 字段一致）

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 产品ID `2011xxxxxx` |
| `N_STR_pkg_desc` | 注释 |
| `A_STR_function` | 客户端礼包类型，默认 `normal_pkg` |
| `A_STR_pkg_type` | 服务器类型，默认 `normal`，**需与2013一致** |
| `S_MAP_server_info` | schema分服 `{"typ":"schema","id":[1,2,...]}` |
| `A_INT_priority` | 优先级，数字越大越靠前 |
| `A_MAP_time_info` | 生效时间，常用 `{"normal":[{"actv_id":xxx}]}` |
| `S_MAP_filters` | 前置条件，`{}`=无限制 |
| `A_MAP_triggers` | 触发条件，`{}`=无限制 |
| `A_ARR_iap_status` | 礼包状态/随机礼包奖池引用 |

**价格档位标准映射（A类规则，自动推断）：**

| 价格 | CD | price_info CODE |
|------|----|----------------|
| $0.99 | 250 | 0099 |
| $4.99 | 1250 | 0499 |
| $9.99 | 2500 | 0999 |
| $19.99 | 5000 | 1999 |
| $49.99 | 12500 | 4999 |
| $99.99 | 25000 | 9999 |

> CD = VIP经验（始终1:1）。price_info 套模板：`ape_{CODE}_cd_an` 等14渠道。

---

### 2013 iap_template — IAP 道具内容/价格

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 模板ID `2013xxxxxx` |
| `A_STR_temp_type` | 类型，需与2011一致 |
| `A_INT_config_id` | 引用2011 ID |
| `A_FLT_price` | 售价（USD） |
| `A_ARR_price_info` | 各渠道product_id，由价格CODE生成 |
| `A_INT_CDs` | 光碟数量 |
| `A_ARR_other_items` | **主道具区**（核心奖励放这里） |

---

### 2112 activity_config — 活动总配置

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 活动ID `2112xxxx` |
| `S_STR_comment` | 注释（含"弃用"的不要改）|
| `A_STR_constant` | 唯一英文标识，换皮时必须新增 |
| `A_MAP_filter` | 参与条件 |
| `A_MAP_text` | i18n键集合 |
| `A_ARR_activity_components` | **子模块列表（核心）**，见组件路由规则 |
| `S_STR_banner_url` | Banner图片 |
| `A_INT_icon_displaykey` | 图标DK |
| `A_INT_show_hud` | HUD显示 |

---

### 2115 activity_task — 任务配置

| 字段名 | 说明 |
|--------|------|
| `A_INT_group` | 任务组（同活动共享）|
| `A_INT_id` | 任务ID，与2112组件id匹配 |
| `A_MAP_fincond` | 完成条件 `{"cat":xxx,"val":n,"op":"ge"}` |
| `A_ARR_reward` | 奖励 `[{"asset":{typ,id,val},"setting":{serial_number,ishighlight}}]` |
| `A_STR_task_desc` | LC key |

---

### 2116 activity_item_exchange — 兑换商店

SheetID: `14IDttHNuHx1U2I1kHinkMLIA6Q4cKmZ8MLoMkgdTGfY`

| 字段名 | 说明 |
|--------|------|
| `A_INT_group` | 分组（2112组件ID = 本表group，非id）|
| `A_INT_id` | 行ID |
| `A_ARR_item_give` | 消耗道具 |
| `A_ARR_item_get` | 获得道具 |
| `A_INT_display_order` | 显示排序 |
| `A_INT_limit_num` | 限购次数，0=不限 |

---

### 2118 activity_rank_rewards — 排名奖励

SheetID: `1Nb23s9iVOiDzWGQlpHSRW5O0gIqd1ZiYNx9kYrDps2M`

通过 `A_INT_group` 与 2122 的 `A_INT_rank_components` 绑定。每组通常12行，覆盖名次1-1到51-100。

| 字段名 | 说明 |
|--------|------|
| `A_INT_group` | 分组号 |
| `A_INT_id` | 行ID `2118xxxx` |
| `A_INT_rank_start` | 名次起始 |
| `A_INT_rank_end` | 名次结束 |
| `A_ARR_reward` | 奖励（通用奖励格式）|

---

### 2121 activity_special — 特殊组件万能表

SheetID: `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc`，3291条，297种type。

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 唯一ID |
| `A_STR_type` | 组件类型（核心），决定其他字段含义 |
| `A_ARR_reward` / `A_ARR_reward_expr` | 奖励 |
| `A_MAP_expr` | 参数（含义随type变化）|
| `A_ARR_status` | 状态/关联配置 |

高频type：`progress`/`new_progress`/`jump_link`/`discount`/`cost`/`buff`

---

### 2122 activity_rank_rule — 排行榜规则

SheetID: `1zziy6nMR1DlhCykKBndwk6d6KNRrzj1PsOsFGbLYR4M`

| 字段名 | 说明 |
|--------|------|
| `A_INT_group` | 分组，与2112组件rank ID配合 |
| `A_INT_rank_components` | → 2118的group（排名奖励）|
| `A_INT_rank_unit` | 排名单位：1=个人/2=联盟/4=服务器/5=服务器组 |
| `A_INT_rank_scope` | 排名范围（必须>rank_unit）|

---

### 2124 activity_drop — 掉落配置

SheetID: `1V7xDriTe0hGW3SF7ZPtk71-sFGyzpbbO47V6gLoBqVA`

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | ID `2124xxxx` |
| `A_STR_action` | 动作标识 |
| `A_MAP_drop` | 掉落内容（核心）|

**drop 类型：**
- `single_random`：按wgt权重随机（最常用）
- `single_all`：全部给予
- `noreturn_random`：不放回随机

**args字段：** `typ`/`id`/`num`（数量，非val！）/`wgt`（权重，非weight！）

---

### 2135 activity_package — 活动礼包桥接表

SheetID: `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc`

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 礼包ID `2135xxxx` |
| `N_STR_comment` | 注释 |
| `A_INT_iap` | **引用2011 ID（核心关联）**|

---

### 2141 activity_without_gacha_pool — 无底Gacha奖池

| 字段名 | 说明 |
|--------|------|
| `S_ARR_drop` | 掉落组 `[{"group":n,"wgt":n}]` |
| `S_ARR_use_item` | 每抽消耗 |
| `A_INT_activity` | 关联2112活动ID |

---

### 2142 activity_without_gacha_reward — 无底Gacha奖励

| 字段名 | 说明 |
|--------|------|
| `A_INT_group` | 奖励组（被2141/2154引用）|
| `A_MAP_asset` | 奖励 `{"typ":"item","id":xxx,"val":n}` |
| `A_INT_probability` | 权重 |
| `A_INT_max` | 最大产出次数 |

---

### 2148 event_decoration_level — 装饰升级配置

SheetID: `1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw`

| 字段名 | 说明 |
|--------|------|
| `A_INT_group_id` | 装饰分组（同一装饰各星级共享）|
| `A_INT_building` | → 1118的A_INT_building_id（家族ID）|
| `A_INT_unlock_item` | → 1111解锁道具ID |
| `A_ARR_BUFF` | **全部buff权威来源**（citybeauty + 属性buff）|
| `A_ARR_upgrade_cost` | 升级到下一星的消耗 |
| `A_INT_paint` | 1=支持涂饰 |
| `A_INT_decroation_paint_skill` | → 2171技能ID |

> ⚠️ buff只写2148，1118.A_ARR_status只放citybeauty，两者citybeauty值必须同步。

---

### 2154 activity_without_gacha_floor — 爬塔层配置

| 字段名 | 说明 |
|--------|------|
| `S_ARR_drop` | `[{"grouplist":[xxx],"wgt":300},{"group":xxx,"wgt":9700}]` |
| `S_ARR_use_item` | 每层消耗 |
| `A_INT_floor` | 层级序号 |
| `S_INT_gacha_minimum` | 保底抽数 |

---

### 1111 item — 道具表

| 字段名 | 说明 |
|--------|------|
| `A_STR_class` | 道具大类（item_general/avatar_frame/chat_skin/stat ue_decorate等）|
| `C_INT_display_key` | 图标→1511 |
| `A_MAP_lc_name` | 名称→1011 |
| `C_ARR_display_labels` | 背包分类（控制背包显示）|
| `A_ARR_use_labels` | 使用标签（也控制背包显示）|
| `S_INT_use_now` | 1=获得即用 |
| `A_MAP_category_param` | 道具效果参数 |

> ⚠️ 道具不进背包：同时清空 display_labels 和 use_labels 中的 bag 相关值。

---

### 1011 i18n — 本地化

文档ID: `11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY`，无主页签，按类别分页签。

| 页签 | 用途 | LC前缀 |
|--------|------|--------|
| IAP | 礼包名称/描述 | `LC_IAP_` |
| EVENT | 活动文本 | `LC_EVENT_` |
| ITEM | 道具名称/描述 | `LC_ITEM_` |
| MAIL | 邮件 | `LC_MAIL_` |

表结构：A=ID_int，B=ID(key)，C~T=18语言（cn/en/fr/de/po/zh/id/th/sp/ru/tr/vi/it/pl/ar/jp/kr/cns）

---

### 1168 get_access_group — 获取途径组合

⚠️ **共7列，读参考行必须用 A:H，用 A:F 会漏最后一列。**

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | `1168xxxx` |
| `C_STR_item_label` | 道具标识 |
| `C_ARR_access_group` | 获取途径，引用1153跳转ID |
| `C_MAP_lc_name` | 固定 `{"typ":"lc","txt":"LC_ITEM_item_cap"}` |
| `C_MAP_label_name` | 固定 `{}` |

---

### 1118 building — 建筑/装饰升级表

SheetID: `1ES3syKlMbqqmZezWFCzwL0elIdrgvisiUTnBwJNRHrk`，tab 名含「不要直接修改」（X2 含「严禁手改」）。

| col | 字段名 | 说明 |
|-----|--------|------|
| [0] | `A_INT_id` | 行 ID = 组ID × 100 + 星级（如 111821901 = 1118219 组的 ★1）|
| [1] | `A_INT_building_id` | 建筑/装饰组 ID（如 1118219）|
| [6] | `C_INT_display_key` | 每星外观 DK → 1511 |
| [7] | `A_MAP_lc_name` | 建筑名 LC key |
| [11] | `A_INT_lvl` | 当前星级 |
| [12] | `A_INT_max_lvl` | 最大星级（扩星时必改，如 3→10）|
| [14] | `A_ARR_cost_asset` | 升级消耗道具 |
| [15] | `A_ARR_add_asset` | 升级获得 |
| [17] | `A_ARR_status` | citybeauty 值（装饰物只写 citybeauty，属性 buff 写 2148）|

**ID 编排：** 组 ID = `1118xxx`；行 ID = 组ID × 100 + 星级

---

### 1127 building_build — 建筑/装饰放置解锁

SheetID: `1Dlyk6JRGOYoVsSohfwXzbwN8wUvwlk1fGgBTzaDKtNw`

| col | 字段名 | 典型值 / 说明 |
|-----|--------|-------------|
| [0] | `p2_title` | （空）|
| [1] | `A_INT_id` | 行 ID，如 `11271111` |
| [2] | `C_STR_comment` | 注释 |
| [3] | （空）| — |
| [4] | `A_ARR_building_ids` | → 1118 组 ID，如 `[1118219]` |
| [5] | `C_INT_display_order` | 展示排序 |
| [6] | `C_INT_continuous_construct` | `0` |
| [7] | `A_INT_count` | `1` |
| [8] | `A_INT_count_max` | `1` |
| [9] | `C_ARR_display_labels` | `["decoration"]` |
| [10] | `A_MAP_requirement` | `{}` |
| [11] | `A_ARR_unlock_cost` | `[{"typ":"item","id":主道具ID,"val":1}]` |
| [12] | `C_ARR_unlock_desc` | `[{"typ":"lc","txt":"LC_EVENT_xxx_get_tips"}]` |
| [13] | `C_MAP_show_requirement` | `{}` |
| [14] | `A_INT_redoverlap` | `0` |
| [15] | `C_INT_subtab` | `4`（装饰固定值）|
| [16] | `A_INT_country_use_type` | `0` |

> 新装饰必须加一行（subtab=4）；旧装饰扩星不需要加。

---

### 1511 display_key — 美术资源 DK

SheetID: `1Oks7yHCxYnWxo1QiNdO5EYNET68l_aCzZU-58zATlLY`

DK 表是 Unity .asset 文件，结构特殊（非普通 Sheet），核心是 **DK ID → 美术资源路径** 的映射。

| 字段 | 说明 |
|------|------|
| `A_INT_id` | DK ID，P2 节日常见段 `15110xxxx`、`15112xxxx` |
| `A_STR_asset_path` | 美术资源路径（Atlas + Sprite 或模型路径）|

> ⚠️ DK 的录入和诊断操作见 `x2-dk-manager` skill。
> ⚠️ 新建道具/装饰时，DK 从 `.meta` 文件读取 GUID，不能凭空分配。

---

### 2111 activity_calendar — 活动日历

SheetID: `1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g`

> **控制活动的后台开关**。2112 定义活动内容，2111 控制何时开/关。一个 2112 对应一条 2111 日历记录。

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 日历 ID，`211100xxx` |
| `A_INT_activity` | → 2112 活动 ID（一对一绑定）|
| `A_MAP_time` | 活动开关时间 `{"start":xxx,"end":xxx}` |
| `A_STR_schema` | 分服方案（schema 分服时填）|

---

### 2119 activity_ui_template — 活动 UI 模板

SheetID: `1_o6R4_vPcl9PACt_-5RZUqG5mYnWTTN7aA_sruSXGeM`

定义活动界面的 UI 框架模板（背景、按钮样式等）。通常同类型活动可复用同一 2119 ID，不需要每次新建。

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 模板 ID，`2119xxxx` |
| `A_STR_type` | UI 类型 |

> 同类活动可复用，换皮时通常不改 2112 的 `ui_template` 字段。

---

### 2120 activity_ui_module — 活动 UI 模块

SheetID: `1b8aDEJWh4cmWKqrrg_5ZAkk3VdTj9k_6SBFbEt0P9-0`

定义 UI 模块的具体元素（图标、颜色、背景图等）。与 2119 配合使用。

---

### 2123 activity_popwindow — 弹窗配置

SheetID: `1Kanf7FuYHMzV0jTX6xBaG49H0svCOLaiJCtMrs1afO8`

> ⚠️ **2123 是 popwindow（弹窗）不是 cumulate（累计）**，两者容易混淆！

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 弹窗 ID |
| `A_STR_type` | 弹窗类型 |
| `A_MAP_content` | 弹窗内容配置 |

---

### 2130 activity_battle_pass — BP 通行证总配置

SheetID: `1qe9RsX7P5bl_O2iLwh_eCJ62KtUkn_RaJiJ4uTRQS8M`

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | BP 配置 ID |
| `A_INT_activity` | → 2112 活动 ID |
| `A_INT_max_level` | 最高等级 |
| `A_INT_buy_exp` | 购买 BP 后获得的初始 exp |
| `A_ARR_price_info` | 购买 BP 的价格（IAP 产品）|
| `A_INT_pre_season_id` | 上期 BP ID（跨季续集）|

---

### 2131 activity_battle_pass_level — BP 等级奖励

SheetID: `1sbMG-3NHEGUgmpW5-kEzwnCkWoi94aeNSk50Zsu_Dcs`

| 字段名 | 说明 |
|--------|------|
| `A_INT_battle_pass` | → 2130 BP 配置 ID |
| `A_INT_level` | 等级序号 |
| `A_INT_exp` | 达到该等级所需 exp |
| `A_ARR_reward` | 免费奖励（所有玩家）|
| `A_ARR_reward_pay` | 付费奖励（购买 BP 后可领）|

---

### 2137 activity_asset_retake — 活动道具回收

SheetID: `1ctEGsAU053iaCCTJeIU1qnp9zfyuURt7k8EzHkKzv2Y`

活动结束后，玩家未使用完的活动货币/道具可回收置换为通用资源。

| 字段名 | 说明 |
|--------|------|
| `A_INT_id` | 回收行 ID，`2137xxxx` |
| `A_ARR_give` | 回收哪些道具（活动货币等）|
| `A_ARR_get` | 回收后获得什么（金币/加速等）|
| `A_INT_need_actv_star` | 是否需要满星才能回收（通常 0）|

---

### 2171 event_decoration_skill — 装饰涂饰技能

SheetID: `1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4`

> ⚠️ **X2 的 2171 是 ActivityCollaborateTask（协作任务），与 P2 完全不同！**

| col | 字段名 | 说明 |
|-----|--------|------|
| [0] | `A_INT_id` | 行 ID = 组ID × 10 + 级别（如 21710171 = 2171017 组的 Lv1）|
| [1] | `A_INT_group` | 技能组 ID（如 2171017）|
| [5] | `C_MAP_lc_name` | 技能名 LC key |
| [8] | `A_INT_lv` | 技能等级（对应装饰星级）|
| [9] | `A_INT_max_lv` | 最大等级（与装饰最大星级一致）|
| [12] | `A_ARR_status` | 技能效果（BUFF 数组）|

**ID 编排：** 组 ID = `2171xxx`；行 ID = 组ID × 10 + 级别

---

### 1173 chat_skin — 聊天铭牌

文档ID: `1mKaHyDbToHVIV9iyOQPFbJ88pwnjGy5-GeiUvRZHPBg`，tab: `chat_skin`

| 字段名 | 说明 |
|--------|------|
| `C_INT_display_key_chat` | 聊天框主体→1511 |
| `C_INT_display_key_show` | 道具图标→1511 |
| `A_ARR_items` | 关联1111道具ID |
| `C_STR_color_*` | 5个颜色字段（HEX） |

**新增铭牌流程：** 1511(×2) → 1111(chat_skin道具) → 1173 → 1011(i18n)

---

## 六、集卡册专属字段（6xxx）

### 6001 card_gallary_book

| 字段名 | 说明 |
|--------|------|
| `A_ARR_group_id` | 8个组ID `[60021317,...,60021324]` |
| `C_INT_display_key` | Book主封面→1511 |
| `C_INT_display_key_sub_menu` | 子菜单图→1511 |
| `C_INT_display_key_card` | 卡片区图→1511（不用填0）|
| `A_ARR_rewards` | Book集满奖励 |
| `A_INT_fes_card_gallary_book` | 1=节日卡册 |

### 6002 card_gallary_group

| 字段名 | 说明 |
|--------|------|
| `A_ARR_card_id` | 该组9张卡ID列表 |
| `C_INT_display_key` | 组封面→1511 |
| `A_ARR_rewards` | 组完成奖励 |
| `A_MAP_unlock` | `{"stars":[N],"need_num":0}`，N=该组最高星级 |

### 6003 card_gallary_card

| 字段名 | 说明 |
|--------|------|
| `A_INT_star` | 星级 1-5 |
| `A_INT_special_card` | 0=普通 |
| `C_INT_display_key` | 卡面图→1511 |
| `C_INT_display_bg_key` | 卡背景（填0）|
| `A_INT_honor_coin` | 集卡荣誉值（1-3★=300，4★=600，5★=800）|
| `A_INT_recycle` | 回收值（1-3★=5，4★=10，5★=50）|
| `A_INT_effectid` | 特效：0=无，15121045=多张5★特效 |
| `A_INT_fes_recycle_id` | 节日货币ID（所有星级均填）|

### 6004 card_gallary_store

| 字段名 | 说明 |
|--------|------|
| `S_MAP_goods_id` | 道具 `{"typ":"item","id":1111xxx,"val":1}` |
| `S_ARR_price` | 价格 `[{"typ":"rss","id":货币ID,"val":金额}]` |
| `A_MAP_buy_limit` | `{"limit_type":"weekly","limit_cnt":5}` |
| `A_INT_fes_card_gallary_book` | 1=节日卡册商店 |

**卡包1111 ID规范（节日固定）：**

| 道具类型 | display_key | 说明 |
|---------|-------------|------|
| 白色保底 | 151104506 | 1-5★全书，不投商店 |
| 绿色保底 | 151104507 | 2-5★，商店第1档 |
| 蓝色保底 | 151104508 | 3-5★ |
| 紫色保底 | 151104509 | 4-5★ |
| 橙色保底 | 151104510 | 5★ |
| 自选包 | 151104511 | card_select_box |
| 主题包 | 查换皮知识库 | 按游戏类型复用或新建 |

---

## 七、机甲皮肤（4010/4011）

- 皮肤ID编码：`401 0 [mech_num] [group] 01`
- 颜色ID编码：`401 1 [mech_num] [group] 01`
- URL字段在4011：`gacha_banner_url`[21] / `gacha_reward_url`[22] / `gacha_select_url`[23]
- 模型DK：4010 col[3][5] + 4011 col[5]；图标DK：4010 col[11] + 4011 col[14] + 1111 col[6]

---

## 八、挖矿系统（35xx metro_minigame）

核心链：`3510 activity_group → 3517 level_group → 3516 level`

| 表 | SheetID |
|----|---------|
| 3510 | `1E-h-mktZ291LuyPHuwYPLYiW3XfmsyNaq819wilHYk4` |
| 3516 | `1jKEzkMLphbaNK1QOwZ4Qhu3cbUPGsunm4WBxSi51UD4` |
| 3517 | `1x4aOdaHemkGlrLpemjblJP8lmGrv4xNgDpoF9zfT4C4` |
| 3518 | `1jcj0FN1V04whz386qBaunEyPkfhHFNty-6R6b1GeiBw` |
| 3525 | `119EoiprKhK1jn5SmnyCPtN1_uR9AEs_iDVgTr5GvZQo` |

---

## 九、踩坑记录

| 表 | 坑 | 正确做法 |
|----|-----|---------|
| 1168 | 读A:F漏G列 | 始终用A:H以上 |
| 2124 drop | args用val/weight | 必须用num/wgt |
| 2148 buff | 属性buff写进1118 | 只写2148，1118只放citybeauty |
| 集卡册bg_key | 以为需要独立bg | 填0即可 |
| 卡包1111 | 白色包投商店 | 白色不投，商店从绿色起 |
| JSON写入 | 默认有空格 | separators=(',',':') |
| 2112 constant | 换皮复用constant | 必须新增，不能复用 |

---

## 十、查找未知表

```bash
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c","range":"fw_gsheet_config!A1:F300"}'
```
