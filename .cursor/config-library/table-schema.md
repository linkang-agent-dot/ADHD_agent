# 配置表字段 Schema（P2 项目）

> 配活动时**必须参照本文件**生成配置行，保证字段顺序和 JSON 格式与线上一致。
> 每张表的列顺序即 Google Sheet 从左到右的列顺序（A, B, C, ...）。

---

## 2011 iap_config — IAP 产品定义

**SheetID**: `1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc`
**QA tab**: `iap_config_QA`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 产品 ID，如 2011500755 |
| B | `N_STR_pkg_desc` | STR | 注释 |
| C | `A_STR_function` | STR | `special` / `basic_CDs` 等 |
| D | `A_STR_pkg_type` | STR | `normal` 等 |
| E | `A_STR_paywall_tab` | STR | 通常空 |
| F | `A_BOL_pirce_display` | BOOL | `False` |
| G | `S_MAP_server_info` | MAP | schema 分服 `{"typ":"schema","id":[1,2,...]}` |
| H | `A_INT_priority` | INT | 排序，如 9991 |
| I | `A_MAP_time_info` | MAP | 时间条件，如 `{"normal":[{"actv_id":xxx,"day":1}]}` |
| J | `S_MAP_filters` | MAP | 通常 `{}` |
| K | `A_MAP_triggers` | MAP | 通常 `{}` |
| L | `A_ARR_iap_status` | ARR | 前置条件，如 `[{"typ":"recharge_actv","id":xxx,"val":1}]` |
| M | `A_INT_iap_new` | INT | 购买上限，通常 `1` |
| N | `S_MAP_group_limit` | MAP | 通常 `{}` |
| O | `A_STR_apply_scene` | STR | `common` |
| P | `A_INT_close_sell_out` | INT | `0` |
| Q | `A_STR_sub_scene` | STR | 空 |
| R | `A_INT_country_use_type` | INT | `0` |
| S | `A_STR_sub_tab` | STR | 空 |
| T | `A_INT_double_coupon` | INT | `0` |

---

## 2013 iap_template — IAP 模板（道具内容 + 价格）

**SheetID**: `1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY`
**QA tab**: `iap_template_QA`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 模板 ID，如 2013511219 |
| B | `A_STR_temp_type` | STR | `normal` |
| C | `A_INT_config_id` | INT | 引用 2011 ID |
| D | `A_INT_coeffs_id` | INT | 系数 ID，如 `2014001` |
| E | `N_STR_temp_desc` | STR | 注释 |
| F | `A_STR_pkg_title` | STR | LC key (礼包标题) |
| G | `A_STR_pkg_desc` | STR | LC key (礼包描述) |
| H | `A_FLT_price` | FLOAT | 价格，如 `4.99` |
| I | `A_ARR_price_info` | ARR | 各渠道 product_id 数组 (14渠道) |
| J | `A_MAP_limit` | MAP | `{"limit_cnt":1,"limit_type":"period"}` |
| K | `S_INT_limit_whitelist` | INT | `0` 或 `1` |
| L | `A_INT_CDs` | INT | CD值，如 `1250` |
| M | `A_INT_all_value` | INT | 总价值标记 |
| N | `A_ARR_CD_items` | ARR | CD 道具 |
| O | `A_ARR_speedup_items` | ARR | 加速道具 |
| P | `A_ARR_resource_items` | ARR | 资源道具 |
| Q | `A_ARR_pvp_items` | ARR | PVP 道具 |
| R | `A_ARR_other_items` | ARR | **主道具区** — 活动核心道具放这里 |
| S | `A_ARR_card_items` | ARR | 卡牌道具 |
| T | `A_ARR_tag_txt` | ARR | ROI 标签，如 `[{"typ":"roi","tag":2,"val":25000}]` |
| U | `A_INT_hud` | INT | `0` |
| V | `A_STR_style_url` | STR | 样式 URL |
| W | `A_STR_pop_banner_url` | STR | 弹窗 banner URL |
| X | `A_MAP_param_color` | MAP | `{}` |
| Y | `A_INT_tag` | INT | 标签类型 |
| Z | `A_STR_subscript` | STR | 空 |
| AA | `A_STR_sub_desc` | STR | 空 |
| AB | `A_STR_banner_url` | STR | 图标 URL |
| AC | `A_MAP_special_style` | MAP | `{}` |
| AD | `A_INT_country_use_type` | INT | `0` |
| AE | `A_ARR_increment_items` | ARR | 增量道具 `[]` |

### 2013 price_info 模板（14渠道，价格码按价格替换）

```json
[
  {"pay_type":"gplay","product_id":"ape_XXXX_cd_an"},
  {"pay_type":"ios","product_id":"ape_XXXX_cd_ios"},
  {"pay_type":"alipayv2","product_id":"ape_XXXX_cd_ali"},
  {"pay_type":"weixin","product_id":"ape_XXXX_cd_weixin"},
  {"pay_type":"huaweihms","product_id":"ape_XXXX_cd_huawei"},
  {"pay_type":"weixinh5","product_id":"ape_XXXX_cd_weixinh5"},
  {"pay_type":"xiaomi","product_id":"ape_XXXX_cd_xiaomi"},
  {"pay_type":"oppo","product_id":"ape_XXXX_cd_oppo"},
  {"pay_type":"ninegame","product_id":"ape_XXXX_cd_ninegame"},
  {"pay_type":"main","product_id":"ape_XXXX_cd_cn_group_main"},
  {"pay_type":"flexion","product_id":"ape_XXXX_cd_an"},
  {"pay_type":"aggregate","product_id":"ape_XXXX_cd_aggregate"},
  {"pay_type":"huaweihms_oversea","product_id":"ape_XXXX_cd_huaweihms_oversea"},
  {"pay_type":"catappult","product_id":"ape_XXXX_cd_an"}
]
```

价格码映射：`0.99→0099`, `4.99→0499`, `9.99→0999`, `19.99→1999`, `49.99→4999`, `99.99→9999`

---

## 2112 activity_config — 活动定义

**SheetID**: `1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E`
**QA tab**: `activity_config_qa`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 活动 ID |
| B | `S_STR_comment` | STR | 注释 |
| C | `A_STR_constant` | STR | 活动常量名 |
| D | `A_INT_index` | INT | 索引 |
| E | `S_INT_priority` | INT | 优先级 |
| F | `A_INT_base_activity_id` | INT | 父活动 ID |
| G | `A_MAP_filter` | MAP | 前置条件 `{"op":"ge","typ":"building","id":xxx,"val":n}` |
| H | `A_MAP_text` | MAP | LC key 集合 `{"group_label":"...","label":"...","title":"..."}` |
| I | `A_ARR_activity_components` | ARR | 组件数组 `[{"typ":"task/package/exchange/rank/...","id":xxx}]` |
| J | `A_MAP_description` | MAP | 规则描述 |
| K | `A_INT_ui_template` | INT | 引用 2119 |
| L | `S_INT_rank_group` | INT | 排行组 |
| M | `S_STR_banner_obj_url` | STR | 3D Banner |
| N | `S_STR_banner_url` | STR | Banner 图片 |
| O | `S_STR_banner_version` | STR | Banner 版本 |
| P | `A_INT_default_displaykey` | INT | 默认展示 key |
| Q | `A_INT_icon_displaykey` | INT | 图标展示 key |
| R | `A_INT_show_hud` | INT | HUD 显示 |
| S | `A_INT_calendar` | INT | 日历 |
| T | `A_ARR_calendar_reward` | ARR | 日历奖励 |
| U | `S_STR_calendar_banner_url` | STR | 日历 Banner |
| V | `A_INT_dependent` | INT | 依赖 |
| W | `S_STR_mini_banner_url` | STR | 小 Banner |
| X | `C_INT_display_flags` | INT | 显示标记 |
| Y | `A_INT_country_use_type` | INT | `0` |

### 组件类型（A_ARR_activity_components.typ）
- `task` → 2115 activity_task
- `package` → 2135 activity_package
- `exchange` → 2116 activity_item_exchange
- `rank` → 2118 activity_rank
- `drop` → 掉落
- `special` → 2121 activity_special
- `floor_gacha` → 2154 爬塔

---

## 2115 activity_task — 活动任务

**SheetID**: `1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_group` | INT | 任务组，`0` 或 `1` |
| B | `A_INT_id` | INT | 任务 ID |
| C | `N_STR_comment` | STR | 注释 |
| D | `A_MAP_showcond` | MAP | 显示条件 |
| E | `A_MAP_fincond` | MAP | 完成条件 `{"cat":xxx,"val":n,"op":"ge"}` |
| F | `A_INT_pretrace` | INT | 预追踪 |
| G | `A_ARR_reward` | ARR | 奖励 `[{"asset":{...},"setting":{...}}]` |
| H | `A_STR_task_desc` | STR | LC key |
| I | `A_MAP_task_label_1` | MAP | 标签1 |
| J | `A_MAP_task_label_2` | MAP | 标签2 |
| K | `A_INT_display_order` | INT | 显示排序 |
| L | `A_INT_displaykey` | INT | 展示 key |
| M | `A_MAP_filter` | MAP | 过滤条件 |
| N | `A_INT_daily_reset` | INT | 每日重置 |
| O | `A_STR_banner` | STR | Banner |
| P | `S_INT_redpoint_off` | INT | 红点关闭 |
| Q | `A_INT_country_use_type` | INT | `0` |
| R | `A_INT_can_ad_reward` | INT | 广告奖励 |

---

## 2116 activity_item_exchange — 兑换商店

**SheetID**: 暂无独立 SheetID，通常在 2112 的 QA 表内

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_group` | INT | 兑换组 |
| B | `A_INT_id` | INT | 兑换 ID |
| C | `N_STR_comment` | STR | 注释 |
| D | `A_ARR_item_give` | ARR | 消耗 `[{"asset":{"typ":"item","id":xxx,"val":n},"setting":{...}}]` |
| E | `A_ARR_item_get` | ARR | 获得 `[{"asset":{"typ":"item","id":xxx,"val":n},"setting":{...}}]` |
| F | `A_INT_display_order` | INT | 显示排序 |
| G | `A_INT_limit_num` | INT | 限购次数，`0`=不限 |
| H | `A_INT_if_remind` | INT | 提醒 |
| I | `A_INT_display` | INT | 显示 |
| J | `A_MAP_requirement` | MAP | 前置条件 |
| K | `S_MAP_show_requirement` | MAP | 显示条件 |
| L | `S_ARR_bargain_count` | ARR | 砍价 |
| M | `S_MAP_bargain_limit` | MAP | 砍价限制 |
| N | `C_INT_discount` | INT | 折扣 |
| O | `A_STR_pkg_title` | STR | 标题 |
| P | `C_MAP_type_title` | MAP | 类型标题 |

---

## 2121 activity_special — 活动特殊参数

**SheetID**: `1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc`

关键字段（根据 type 不同，含义不同）：
- `A_INT_id`
- `A_STR_type` — 如 `floor_gacha_upgrade_floor`, `high_exchange_shop` 等
- `A_ARR_array` — 参数数组
- `A_MAP_reward` — 奖励配置

---

## 2124 掉落表（drop）

**SheetID**: 暂未录入（2026-04-21 首次确认格式，待补 SheetID）

通用掉落配置表，行 ID 编码：`2124` + 4~5 位后缀。随机礼包是其中一种使用模块，其他模块类型待补充。

### 已知模块类型：single_random（随机礼包）

当一行配置的掉落类型为 `single_random` 时，字段格式如下：

```json
{
  "typ": "single_random",
  "num": 1,
  "args": [
    {"typ": "item", "id": 11112175, "num": 8,  "wgt": 150},
    {"typ": "item", "id": 11112175, "num": 9,  "wgt": 100},
    {"typ": "item", "id": 11112175, "num": 11, "wgt": 50},
    {"typ": "item", "id": 11112175, "num": 13, "wgt": 20},
    {"typ": "item", "id": 11112175, "num": 15, "wgt": 10},
    {"typ": "item", "id": 11112175, "num": 17, "wgt": 5},
    {"typ": "item", "id": 11112175, "num": 20, "wgt": 2},
    {"typ": "item", "id": 11112175, "num": 25, "wgt": 1}
  ]
}
```

字段说明：
- `typ: "single_random"` — 单次随机抽取
- `num: 1`（外层）— 抽取次数
- `args` — 各档位，同一行内 `typ` 和 `id` 通常相同，只有 `num` 和 `wgt` 变化
  - `num` — 道具数量（**注意：是 `num` 不是 `val`**）
  - `wgt` — 档位权重（**注意：是 `wgt` 不是 `weight` 或 `probability`**）
  - 期望计算：`E = Σ(num × wgt) / Σwgt`

⚠️ **常见错误**：生成配置时容易把字段名写成 `val`/`weight`，务必用 `num`/`wgt`。

### 案例：21127807 机甲gacha 随机礼包行

| 行 ID | 价格 | 旧期望 | 新期望（2026-04-21改） | 备注 |
|-------|------|--------|----------------------|------|
| 21241684 | $19.99 | E[5.06] | 不变 | 对锚点4tok +26.4% |
| 21241892 | $49.99 | E[9.50] | **E[11.54]** | 对锚点10tok +15.4% |
| 21241685 | $99.99 | E[18.55] | **E[20.58]** | 对锚点18tok +14.3% |

随机礼包数值原则：**期望值应比同价锚点高 10~20%**（低于锚点 = 随机礼包无购买理由）。

---

## 2135 activity_package — 活动礼包入口

**SheetID**: `1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc`
**Tab**: `activity_event_pkg`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 礼包 ID |
| B | `N_STR_comment` | STR | 注释 |
| C | `A_INT_iap` | INT | **引用 2011 ID**（关键关联） |
| D | `A_MAP_cost` | MAP | 非 IAP 购买成本 `{"typ":"vm","id":xxx,"val":n}` 或 `{}` |
| E | `A_ARR_get_items` | ARR | 购买获得道具（非 IAP 时使用） |
| F | `A_INT_cost_limit` | INT | `-1` 或 `0` |
| G | `A_STR_banner_url` | STR | Banner 图片路径 |
| H | `A_STR_cd_cost_title` | STR | LC key |
| I | `A_STR_cd_cost_text` | STR | LC key |
| J | `A_MAP_filters` | MAP | 过滤条件 `{}` |
| K | `A_INT_order` | INT | 排序 |
| L | `C_INT_all_value` | INT | 总价值（计算列） |
| M | `C_STR_tab` | STR | 分类标签（计算列） |

### 关键追踪链
```
2112.components → {"typ":"package","id":xxx}
  → 2135.A_INT_id
    → 2135.A_INT_iap → 2011.A_INT_id
      → 2013.A_INT_config_id → 2011.A_INT_id (道具/价格在2013)
```

---

## 2141 activity_without_gacha_pool — 无底 Gacha 奖池

**SheetID**: `1E_T34i1eLC7F3hKlsLJVlizlu9aRhBY0vzMSNN1v5do`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 奖池 ID |
| B | `N_STR_comment` | STR | 注释 |
| C | `S_ARR_drop` | ARR | 掉落组 `[{"group":n,"wgt":n},...]` |
| D | `S_ARR_use_item` | ARR | 消耗 `[{"typ":"item","id":xxx,"val":n}]` |
| E | `S_ARR_improve` | ARR | 保底提升 `[{"group":n,"wgt":n}]` |
| F | `S_INT_group_up_quality` | INT | 品质提升阈值 |
| G | `A_INT_interval` | INT | 间隔 |
| H | `A_STR_function` | STR | `normal` |
| I | `A_INT_activity` | INT | 关联 2112 活动 ID |

---

## 2142 activity_without_gacha_reward — 无底 Gacha 奖励定义

**SheetID**: `1vGzggIww1jifGGqDGqzB1RgittK62gL_3-j5EW3_X3I`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_group` | INT | 奖励组 ID（2141/2154 的 drop.group 引用此值） |
| B | `A_INT_id` | INT | 奖励行 ID |
| C | `N_STR_comment` | STR | 注释 |
| D | `A_MAP_asset` | MAP | 奖励 `{"typ":"item","id":xxx,"val":n}` |
| E | `A_INT_probability` | INT | 组内权重 |
| F | `A_INT_max` | INT | 最大产出次数 |
| G | `A_INT_reward_index` | INT | 奖励索引（决定显示顺序） |
| H | `A_INT_probability_show` | INT | 显示概率（千分比） |
| I | `A_INT_special_reward` | INT | 特殊奖励标记（`1`=大奖高亮） |

---

## 2154 activity_without_gacha_floor — 爬塔层配置

**SheetID**: `1XfENodZsKFH-hit2TWrxt8mmJSPqnn8qM2Cv2iIl2vo`

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | `A_INT_id` | INT | 层 ID |
| B | `N_STR_comment` | STR | 注释 |
| C | `S_ARR_drop` | ARR | 掉落配置（见下方详解） |
| D | `S_ARR_use_item` | ARR | 每抽消耗 `[{"typ":"item","id":xxx,"val":n}]` |
| E | `A_INT_activity` | INT | 关联 2112 活动 ID |
| F | `A_INT_floor` | INT | 层级序号 (1,2,3,...) |
| G | `S_INT_gacha_minimum` | INT | 保底抽数 |
| H | `S_MAP_special_group` | MAP | 特殊组配置 `{}` |

### S_ARR_drop 格式详解

```json
[
  {"grouplist":[883], "wgt":300},   // 稀有组(升层道具): 引用 2142.group，wgt=权重
  {"group":882, "wgt":9700}          // 普通组: 引用 2142.group
]
```

- `grouplist` = 多个 group 合并为一个抽取入口（抽中后在 list 内均分）
- `group` = 单个 group
- `wgt` = 权重（所有 wgt 加总为分母）
- 最终层（皮肤层）可能只有 grouplist 没有 group

### 已有机甲抽奖行（activity 21127807）

| 2154 ID | 层 | 消耗 | 稀有组 | 普通组 |
|---------|---|------|--------|--------|
| 21540458 | 1 | 1tok | grouplist:[883] wgt:300 | group:882 wgt:9700 |
| 21540459 | 2 | 2tok | grouplist:[885] wgt:300 | group:884 wgt:9700 |
| 21540460 | 3 | 5tok | grouplist:[887] wgt:300 | group:886 wgt:9700 |
| 21540461 | 4 | **10tok**（原8tok，2026-04-21改） | grouplist:[889] wgt:300 | group:888 wgt:9700 |
| 21540462 | 5 | **18tok**（原12tok，2026-04-21改） | grouplist:[891] wgt:300 | group:890 wgt:9700 |
| 21540463 | 6 | **25tok**（原16tok，2026-04-21改） | grouplist:[892] wgt:300 | (无) |

---

## 跨表追踪链总图

```
2112 (activity_config)
  └─ components:
      ├─ {"typ":"package","id":xxx} → 2135 (activity_package)
      │    └─ A_INT_iap → 2011 (iap_config)
      │         └─ 2013 (iap_template): config_id = 2011.id
      │              └─ other_items: 道具内容（固定给量礼包）
      │              └─ price_info: 渠道价格
      │              └─ [随机礼包等] drop权重 → 2124 掉落表 (single_random 等多种模块，字段格式见2124节)
      ├─ {"typ":"task","id":xxx} → 2115 (activity_task)
      │    └─ fincond.cat: 完成条件
      │    └─ reward: 任务奖励
      ├─ {"typ":"exchange","id":xxx} → 2116 (兑换商店)
      ├─ {"typ":"special","id":xxx} → 2121 (特殊参数)
      ├─ {"typ":"floor_gacha","id":xxx} → 2154 (爬塔层)
      │    └─ S_ARR_drop.group/grouplist → 2142 (奖励定义)
      └─ {"typ":"drop","id":xxx} → 2141 (奖池)
           └─ S_ARR_drop.group → 2142 (奖励定义)
```
