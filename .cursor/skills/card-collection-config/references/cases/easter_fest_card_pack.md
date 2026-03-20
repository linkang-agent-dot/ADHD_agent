# 案例：复活节节日卡册道具配置

## 任务类型
抽奖类 → 节日卡册卡包道具配置（item_card_asset）

## 关键表结构

| 表 | Sheet ID | 说明 |
|----|----------|------|
| 6001 | `1T-8EtaenFTybZzKqeRtLGWNRWlaxcPIMQScvUCTY1Dc` | 卡册 book 定义，含完成奖励和 group_id 列表 |
| 6002 | `1H1Epc0EccCDrxGpgZoIyGlpDh4WaDviOQX-r41rSvhE` | 卡册 group 定义，每组9张卡 |
| 6003 | `1TiKSm3Z6AnbclrxDS4w9O4b-Vmz6MPhQU4ll7A42z2Y` | 单张卡定义 |

## 输入 → 输出

**输入**：科技节已有卡包道具配置（11119996-111110006）+ 6001/6002 表里复活节的 group_id 和 book_id

**输出**：复活节卡包道具配置行（tab 分隔，同 1111 表格式）

## 核心 ID 映射

### 卡册 Book ID
| 节日 | Book ID |
|------|---------|
| 科技节 | `60011004` |
| 复活节 | `60011005` |

### 主题组 ID（6002 表）
| 科技节 group | 主题 | 复活节 group | 主题 | 有5星 |
|-------------|------|-------------|------|-------|
| 60021304 | 趣味骰子（大富翁） | 60021312 | 金蛋工坊 | ❌ |
| 60021305 | 矿场日常（挖矿） | 60021314 | 矿洞寻宝 | ❌ |
| 60021306 | 寻找破译器（挖孔） | 60021313 | 极速飞车 | ✅ |
| 60021307 | 快乐弹珠 | 60021315 | 彩蛋大亨 | ✅ |
| 60021308 | 推币大作战 | 60021316 | 异族探秘 | ✅ |
| 60011004（全册） | 异族大富翁特殊 | 60011005（全册） | 异族探秘大富翁特殊 | ✅保底 |

**判断有无5星的依据**：看 6002 表的 rewards 字段
- 含 `11112924` → 有5星（弹珠/彩蛋大亨类）
- 含 `11112936` → 无5星（大富翁/金蛋工坊类）
- 无特殊道具但对应推币机/飞车类 → 有5星

### 保底卡包 ID（本次复活节）
| 颜色 | 科技节 ID | 复活节 ID |
|------|----------|----------|
| 白色 | 111110002 | 111110305 |
| 绿色 | 111110003 | 111110306 |
| 蓝色 | 111110004 | 111110307 |
| 紫色 | 111110005 | 111110308 |
| 橙色 | 111110006 | 111110309 |

## 道具行格式（tab 分隔）

```
{id}	{中文名}		item_card_asset	19	{icon_id}	{display_key}	15112564	{}	{lc_name}	{lc_desc}	{}	135	999999	99999	5	["bag_other"]	["card","bag"]	{drop_json}
```

常量字段：`19`、`15112564`、`{}`、`135`、`999999`、`99999`、`5`、`["bag_other"]`、`["card","bag"]`

## Drop JSON 模板

### 有5星主题卡包（2张产出）
```json
{"drop": {"typ":"single_all","num":1,"args":[
  {"typ":"single_random","num":1,"args":[
    {"typ":"card_star","id":3,"num":1,"args":[{"id":{BOOK_ID}},{"id":{GROUP_ID}}],"wgt":8000},
    {"typ":"card_star","id":4,"num":1,"args":[{"id":{BOOK_ID}},{"id":{GROUP_ID}}],"wgt":1800},
    {"typ":"card_star","id":5,"num":1,"args":[{"id":{BOOK_ID}},{"id":{GROUP_ID}}],"wgt":200}
  ]},
  {"typ":"single_random","num":1,"args":[...同上...]}
]}}
```

### 无5星主题卡包（2张产出）
```json
{"drop":{"typ":"single_all","num":1,"args":[
  {"typ":"single_random","num":1,"args":[
    {"typ":"card_star","id":3,"num":1,"args":[{"id":{BOOK_ID}},{"id":{GROUP_ID}}],"wgt":8000},
    {"typ":"card_star","id":4,"num":1,"args":[{"id":{BOOK_ID}},{"id":{GROUP_ID}}],"wgt":1800}
  ]},
  {"typ":"single_random","num":1,"args":[...同上...]}
]}}
```

### 特殊保底包（全册任意5星）
```json
{"drop":{"typ":"single_random","num":1,"args":[
  {"typ":"card_star_missing","id":5,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":10000}
]}}
```

### 白色保底（1~5星，全册）
```json
{"drop": {"typ":"single_all","num":1,"args":[{"typ":"single_random","num":1,"args":[
  {"typ":"card_star","id":1,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":9000},
  {"typ":"card_star","id":2,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":800},
  {"typ":"card_star","id":3,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":100},
  {"typ":"card_star","id":4,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":49},
  {"typ":"card_star","id":5,"num":1,"args":[{"id":{BOOK_ID}}],"wgt":1}
]}]}}
```

### 绿色保底（2~5星）
`wgt: 8400 / 1400 / 198 / 2`

### 蓝色保底（3~5星）
`wgt: 8750 / 1240 / 10`

### 紫色保底（4~5星）
`wgt: 8750 / 1250`

### 橙色保底（5星）
`wgt: 1250`

## LC Key 命名规则
- 科技节：`LC_ITEM_tech_fest_pack_{theme}_name/desc`
- 复活节：`LC_ITEM_easter_fest_pack_{theme}_name/desc`

主题 key 对照：
| 中文名 | key |
|--------|-----|
| 极速飞车 | racing |
| 矿洞寻宝 | mine |
| 彩蛋大亨 | tycoon |
| 异族探秘 | alien |
| 金蛋工坊 | workshop |
| 白/绿/蓝/紫/橙保底 | common / excellent / rare / epic / legendary |

## 坑 / 注意事项

- `111110008`、`111110104`、`111110105` 已被占用（是卡册完成奖励道具），分配新 ID 时跳过
- 保底卡包图标固定用 `403303`，主题卡包图标各自不同
- display_key 需在已有节日值之后分配，复活节 6002 已用到 `151105050`，6001 用了 `151105051`
- 异族探秘大富翁特殊包用的是整个 book_id（`60011005`），不是某个 group_id
