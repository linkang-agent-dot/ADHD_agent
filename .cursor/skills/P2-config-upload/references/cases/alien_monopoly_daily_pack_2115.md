# 案例：2026 异族大富翁-每日礼包 (2115 表)

## 基本信息

| 字段 | 值 |
|------|---|
| 表编号 | 2115 (activity_task) |
| 行 ID | 211587376 |
| 任务名称 | 复活节异族每日gacha-累计购买每日礼包 |

## ⚠️ 待确认

1. **2115 task ID (`211587376`) 与 2112 引用的 task ID (`211586409`) 不一致** → 需确认 2112 是否改为 `211587376`
2. **condition 里的 2013 IDs (`2013510523~2013510527`) 与已确认的每日礼包 IDs (`2013511219~2013511223`) 不一致** → 需确认是否要替换

## 完整配置行

```
0	211587376	复活节异族每日gacha-累计购买每日礼包	{"op":"and", "args": [{"op":"ge", "typ":"actvstarttime","val":0},{"op":"ge", "typ":"building","id":111811,"val":3}]}	{"cat":101412163,"arg":{"ids":[2013510523,2013510524,2013510525,2013510526,2013510527]},"val":5,"op":"ge"}	0	[{"asset":{"typ":"item","id":11112900,"val":200},"setting":{"serial_number":5,"ishighlight":false}}]	LC_EVENT_easter_gacha_daily_pkg_tips	{"lc":"LC_IAP_gird_gacha_daily_packge","order":1}	{}	99999	0	{}	0	""	0	0	0
```
