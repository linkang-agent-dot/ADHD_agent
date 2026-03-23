# 案例：2026 异族大富翁-每日礼包 (2013 表)

## 基本信息

| 字段 | 值 |
|------|---|
| 表编号 | 2013 (iap_config) |
| 行 ID 范围 | 2013511219 ~ 2013511223 |
| 活动名称 | 2026异族大富翁-每日礼包-第N天 |
| LC key | `LC_EVENT_2026monoploy_gacha` |
| 价格 | 4.99 |
| 分类 | 2014001 |
| 购买限制 | `{"limit_cnt":1,"limit_type":"period"}` |

## 5 天 ID 对照

| 天数 | 行 ID (2013) | A_STR_constant → 2011 ID | 每日特色道具 (serial_number:4) |
|:---:|-------------|--------------------------|-------------------------------|
| 第1天 | 2013511219 | 2011500755 | item `11117068` × 25 |
| 第2天 | 2013511220 | 2011500756 | item `11116402` × 2 |
| 第3天 | 2013511221 | 2011500757 | item `11117024` × 2 |
| 第4天 | 2013511222 | 2011500758 | item `11118501` × 2 |
| 第5天 | 2013511223 | 2011500759 | material `19345010` × 1 |

## 固定内容（每天相同）

```json
{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}}
{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}}
{"asset":{"typ":"xp","id":11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}
```

> ⚠️ 注意：serial_number:5 的道具在换皮时从 `11112649×8` → `11112765×16`，不是简单沿用旧值。

ROI 标签：`{"typ":"roi","tag":2,"val":25000}`

## 支付渠道（所有行一致）

产品 ID 前缀 `ape_0499_cd_`，支持渠道：
`gplay`, `ios`, `alipayv2`, `weixin`, `huaweihms`, `weixinh5`, `xiaomi`, `oppo`, `ninegame`, `main`(cn_group_main), `flexion`, `aggregate`, `huaweihms_oversea`, `catappult`

```
2013511219	normal	2011500755	2014001	2026异族大富翁-每日礼包-第1天	LC_EVENT_2026monoploy_gacha		4.99	[{"pay_type":"gplay", "product_id": "ape_0499_cd_an"},{"pay_type":"ios", "product_id": "ape_0499_cd_ios"},{"pay_type":"alipayv2", "product_id": "ape_0499_cd_ali"},{"pay_type":"weixin", "product_id": "ape_0499_cd_weixin"},{"pay_type":"huaweihms", "product_id": "ape_0499_cd_huawei"},{"pay_type":"weixinh5", "product_id": "ape_0499_cd_weixinh5"},{"pay_type":"xiaomi", "product_id": "ape_0499_cd_xiaomi"},{"pay_type":"oppo", "product_id": "ape_0499_cd_oppo"},{"pay_type":"ninegame", "product_id": "ape_0499_cd_ninegame"},{"pay_type":"main", "product_id": "ape_0499_cd_cn_group_main"},{"pay_type":"flexion", "product_id": "ape_0499_cd_an"},{"pay_type":"aggregate", "product_id": "ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea", "product_id": "ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult", "product_id": "ape_0499_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	1250	25150	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}},{"asset":{"typ":"item","id":11117068,"val":25},"setting":{"serial_number":4,"ishighlight":false}},{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}},{"asset":{"typ":"xp","id": 11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}]	[]	[{"typ":"roi","tag":2,"val":25000}]	0			{}	0				{}	0	[]
2013511220	normal	2011500756	2014001	2026异族大富翁-每日礼包-第2天	LC_EVENT_2026monoploy_gacha		4.99	[{"pay_type":"gplay", "product_id": "ape_0499_cd_an"},{"pay_type":"ios", "product_id": "ape_0499_cd_ios"},{"pay_type":"alipayv2", "product_id": "ape_0499_cd_ali"},{"pay_type":"weixin", "product_id": "ape_0499_cd_weixin"},{"pay_type":"huaweihms", "product_id": "ape_0499_cd_huawei"},{"pay_type":"weixinh5", "product_id": "ape_0499_cd_weixinh5"},{"pay_type":"xiaomi", "product_id": "ape_0499_cd_xiaomi"},{"pay_type":"oppo", "product_id": "ape_0499_cd_oppo"},{"pay_type":"ninegame", "product_id": "ape_0499_cd_ninegame"},{"pay_type":"main", "product_id": "ape_0499_cd_cn_group_main"},{"pay_type":"flexion", "product_id": "ape_0499_cd_an"},{"pay_type":"aggregate", "product_id": "ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea", "product_id": "ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult", "product_id": "ape_0499_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	1250	25150	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}},{"asset":{"typ":"item","id":11116402,"val":2},"setting":{"serial_number":4,"ishighlight":false}},{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}},{"asset":{"typ":"xp","id": 11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}]	[]	[{"typ":"roi","tag":2,"val":25000}]	0			{}	0				{}	0	[]
2013511221	normal	2011500757	2014001	2026异族大富翁-每日礼包-第3天	LC_EVENT_2026monoploy_gacha		4.99	[{"pay_type":"gplay", "product_id": "ape_0499_cd_an"},{"pay_type":"ios", "product_id": "ape_0499_cd_ios"},{"pay_type":"alipayv2", "product_id": "ape_0499_cd_ali"},{"pay_type":"weixin", "product_id": "ape_0499_cd_weixin"},{"pay_type":"huaweihms", "product_id": "ape_0499_cd_huawei"},{"pay_type":"weixinh5", "product_id": "ape_0499_cd_weixinh5"},{"pay_type":"xiaomi", "product_id": "ape_0499_cd_xiaomi"},{"pay_type":"oppo", "product_id": "ape_0499_cd_oppo"},{"pay_type":"ninegame", "product_id": "ape_0499_cd_ninegame"},{"pay_type":"main", "product_id": "ape_0499_cd_cn_group_main"},{"pay_type":"flexion", "product_id": "ape_0499_cd_an"},{"pay_type":"aggregate", "product_id": "ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea", "product_id": "ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult", "product_id": "ape_0499_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	1250	25150	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}},{"asset":{"typ":"item","id":11117024,"val":2},"setting":{"serial_number":4,"ishighlight":false}},{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}},{"asset":{"typ":"xp","id": 11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}]	[]	[{"typ":"roi","tag":2,"val":25000}]	0			{}	0				{}	0	[]
2013511222	normal	2011500758	2014001	2026异族大富翁-每日礼包-第4天	LC_EVENT_2026monoploy_gacha		4.99	[{"pay_type":"gplay", "product_id": "ape_0499_cd_an"},{"pay_type":"ios", "product_id": "ape_0499_cd_ios"},{"pay_type":"alipayv2", "product_id": "ape_0499_cd_ali"},{"pay_type":"weixin", "product_id": "ape_0499_cd_weixin"},{"pay_type":"huaweihms", "product_id": "ape_0499_cd_huawei"},{"pay_type":"weixinh5", "product_id": "ape_0499_cd_weixinh5"},{"pay_type":"xiaomi", "product_id": "ape_0499_cd_xiaomi"},{"pay_type":"oppo", "product_id": "ape_0499_cd_oppo"},{"pay_type":"ninegame", "product_id": "ape_0499_cd_ninegame"},{"pay_type":"main", "product_id": "ape_0499_cd_cn_group_main"},{"pay_type":"flexion", "product_id": "ape_0499_cd_an"},{"pay_type":"aggregate", "product_id": "ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea", "product_id": "ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult", "product_id": "ape_0499_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	1250	25150	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}},{"asset":{"typ":"item","id":11118501,"val":2},"setting":{"serial_number":4,"ishighlight":false}},{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}},{"asset":{"typ":"xp","id": 11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}]	[]	[{"typ":"roi","tag":2,"val":25000}]	0			{}	0				{}	0	[]
2013511223	normal	2011500759	2014001	2026异族大富翁-每日礼包-第5天	LC_EVENT_2026monoploy_gacha		4.99	[{"pay_type":"gplay", "product_id": "ape_0499_cd_an"},{"pay_type":"ios", "product_id": "ape_0499_cd_ios"},{"pay_type":"alipayv2", "product_id": "ape_0499_cd_ali"},{"pay_type":"weixin", "product_id": "ape_0499_cd_weixin"},{"pay_type":"huaweihms", "product_id": "ape_0499_cd_huawei"},{"pay_type":"weixinh5", "product_id": "ape_0499_cd_weixinh5"},{"pay_type":"xiaomi", "product_id": "ape_0499_cd_xiaomi"},{"pay_type":"oppo", "product_id": "ape_0499_cd_oppo"},{"pay_type":"ninegame", "product_id": "ape_0499_cd_ninegame"},{"pay_type":"main", "product_id": "ape_0499_cd_cn_group_main"},{"pay_type":"flexion", "product_id": "ape_0499_cd_an"},{"pay_type":"aggregate", "product_id": "ape_0499_cd_aggregate"},{"pay_type":"huaweihms_oversea", "product_id": "ape_0499_cd_huaweihms_oversea"},{"pay_type":"catappult", "product_id": "ape_0499_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	1250	25150	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11112765,"val":16},"setting":{"serial_number":5,"ishighlight":false}},{"asset":{"typ":"material","id":19345010,"val":1},"setting":{"serial_number":4,"ishighlight":false}},{"asset":{"typ":"item","id":11114316,"val":1},"setting":{"serial_number":2,"ishighlight":false}},{"asset":{"typ":"xp","id": 11161002,"val":1250},"setting":{"serial_number":1,"ishighlight":false}}]	[]	[{"typ":"roi","tag":2,"val":25000}]	0			{}	0				{}	0	[]
```

> ⚠️ A_STR_constant (Col3) 已确认：`2011500755~2011500759`（见下方 2011 表）。
