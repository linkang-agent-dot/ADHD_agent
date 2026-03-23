# 案例：2026 异族大富翁-每日礼包 (2011 表)

## 基本信息

| 字段 | 值 |
|------|---|
| 表编号 | 2011 (iap_product / A_STR_constant) |
| 行 ID 范围 | 2011500755 ~ 2011500759 |
| 关联活动 ID | `21127718`（异族大富翁-每日礼包，2112 表） |

## 5 天 ID 对照

| 天数 | 行 ID | sort |
|:---:|-------|:----:|
| 第1天 | 2011500755 | 9991 |
| 第2天 | 2011500756 | 9992 |
| 第3天 | 2011500757 | 9993 |
| 第4天 | 2011500758 | 9994 |
| 第5天 | 2011500759 | 9995 |

## 固定字段（所有行一致）

| 字段 | 值 |
|------|---|
| type | `special` |
| sub_type | `normal` |
| is_hide | `False` |
| schema | `{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}` |
| 购买上限 | `1` |
| tag | `common` |

## 前置条件（actv_condition）

⚠️ 累充 ID 待替换，当前为占位值：

```json
[
  {"typ":"recharge_actv","id":21127573,"val":1},
  {"typ":"recharge_actv","id":21127577,"val":1},
  {"typ":"recharge_actv","id":21127658,"val":1},
  {"typ":"recharge_actv","id":21127657,"val":1},
  {"typ":"recharge_actv","id":21127344,"val":1},
  {"typ":"recharge_actv","id":21127345,"val":1},
  {"typ":"recharge_actv","id":21127563,"val":1}
]
```

## 完整配置行（累充待替换）

```
2011500755	异族大富翁GACHA-每日礼包-第1天	special	normal		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	9991	{"normal":[{"actv_id":21127718,"day":1}]}	{}	{}	[{"typ":"recharge_actv","id":21127573,"val":1},{"typ":"recharge_actv","id":21127577,"val":1},{"typ":"recharge_actv","id":21127658,"val":1},{"typ":"recharge_actv","id":21127657,"val":1},{"typ":"recharge_actv","id":21127344,"val":1},{"typ":"recharge_actv","id":21127345,"val":1},{"typ":"recharge_actv","id":21127563,"val":1}]	1	{}	common	0		0		0
2011500756	异族大富翁GACHA-每日礼包-第2天	special	normal		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	9992	{"normal":[{"actv_id":21127718,"day":2}]}	{}	{}	[{"typ":"recharge_actv","id":21127573,"val":1},{"typ":"recharge_actv","id":21127577,"val":1},{"typ":"recharge_actv","id":21127658,"val":1},{"typ":"recharge_actv","id":21127657,"val":1},{"typ":"recharge_actv","id":21127344,"val":1},{"typ":"recharge_actv","id":21127345,"val":1},{"typ":"recharge_actv","id":21127563,"val":1}]	1	{}	common	0		0		0
2011500757	异族大富翁GACHA-每日礼包-第3天	special	normal		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	9993	{"normal":[{"actv_id":21127718,"day":3}]}	{}	{}	[{"typ":"recharge_actv","id":21127573,"val":1},{"typ":"recharge_actv","id":21127577,"val":1},{"typ":"recharge_actv","id":21127658,"val":1},{"typ":"recharge_actv","id":21127657,"val":1},{"typ":"recharge_actv","id":21127344,"val":1},{"typ":"recharge_actv","id":21127345,"val":1},{"typ":"recharge_actv","id":21127563,"val":1}]	1	{}	common	0		0		0
2011500758	异族大富翁GACHA-每日礼包-第4天	special	normal		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	9994	{"normal":[{"actv_id":21127718,"day":4}]}	{}	{}	[{"typ":"recharge_actv","id":21127573,"val":1},{"typ":"recharge_actv","id":21127577,"val":1},{"typ":"recharge_actv","id":21127658,"val":1},{"typ":"recharge_actv","id":21127657,"val":1},{"typ":"recharge_actv","id":21127344,"val":1},{"typ":"recharge_actv","id":21127345,"val":1},{"typ":"recharge_actv","id":21127563,"val":1}]	1	{}	common	0		0		0
2011500759	异族大富翁GACHA-每日礼包-第5天	special	normal		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	9995	{"normal":[{"actv_id":21127718,"day":5}]}	{}	{}	[{"typ":"recharge_actv","id":21127573,"val":1},{"typ":"recharge_actv","id":21127577,"val":1},{"typ":"recharge_actv","id":21127658,"val":1},{"typ":"recharge_actv","id":21127657,"val":1},{"typ":"recharge_actv","id":21127344,"val":1},{"typ":"recharge_actv","id":21127345,"val":1},{"typ":"recharge_actv","id":21127563,"val":1}]	1	{}	common	0		0		0
```
