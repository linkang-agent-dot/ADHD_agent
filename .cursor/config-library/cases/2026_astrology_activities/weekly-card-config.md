# 2026 占星节周卡配置补丁

## 处理结论

- `2112` 活动行 `211201010` 复用，但 `components.package` 改成占星节专属 `213521201-213521204`。
- `2135` 新增 4 行，分别指向 `2011920102-2011920105`。
- `2011` 覆盖 `2011920102-2011920105`，把旧 `recharge_actv=211200084` 改为占星节当前礼包链路使用的 `211200093`；49.99 全包购买限制改绑新 `2013`。
- `2013` 新增 `2013920107-2013920110`。`2013920102-2013920106` 已被占星节每日礼包占用，不能用于周卡。
- `1111` 新增 3 个 `item_subscription` 道具，名称/LC/图标沿用旧周卡，仅改 `category_param.effect.id` 指向新 `2013`。
- `2024` 新增 30 行自选坑位，按旧周卡奖励表复制，仅替换节日专属奖励：`11119453 -> 11119497`、`11119473 -> 11119517`。

## 2112 activity_config 覆盖行

```tsv
	211201010	节日通用自选周卡（前期节日）	event_fes_time_card	0	49997	211201010	{"op":"ge","typ":"building","id":111811,"val":5}	{"label":"LC_EVENT_summer_time_card_title","title":"LC_EVENT_fes_time_card_title","subtitle":"LC_EVENT_summer_time_card_subtitle"}	[{"typ":"package","id":213521201},{"typ":"package","id":213521202},{"typ":"package","id":213521203},{"typ":"package","id":213521204}]	{"rule":"LC_EVENT_fes_time_card_rule"}	21191334	1	'""	assets/x2/operation/EventBanner/event_banner_0326.png	1	0	0	211201001	0	[]	'""	0	1511031034	1	'""	0
```

## 2135 activity_package 新增行

```tsv
	213521201	占星节自选周卡-29.99	2011920102	0	{}	[]	0	'""	NULL	NULL	{}	999	0	NULL	NULL	0	1
	213521202	占星节自选周卡-19.99	2011920103	0	{}	[]	0	'""	NULL	NULL	{}	998	0	NULL	NULL	0	1
	213521203	占星节自选周卡-9.99	2011920104	0	{}	[]	0	'""	NULL	NULL	{}	997	0	NULL	NULL	0	1
	213521204	占星节自选周卡-49.99	2011920105	0	{}	[]	0	'""	NULL	NULL	{}	996	0	NULL	NULL	0	1
```

## 2011 iap_config 覆盖行

```tsv
	2011920102	节日自选周卡-29.99	fes_weekly_card	fes_weekly_card		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	999	{"time_card":{"duration":604800}}	{}	{}	[{"typ":"recharge_actv","id":211200093,"arg1":1511018855,"val":1}]	1	{}	common	0	0		0
	2011920103	节日自选周卡-19.99	fes_weekly_card	fes_weekly_card		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	998	{"time_card":{"duration":604800}}	{}	{}	[{"typ":"recharge_actv","id":211200093,"arg1":1511018855,"val":1}]	1	{}	common	0	0		0
	2011920104	节日自选周卡-9.99	fes_weekly_card	fes_weekly_card		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	997	{"time_card":{"duration":604800}}	{}	{}	[{"typ":"recharge_actv","id":211200093,"arg1":1511018855,"val":1}]	1	{}	common	0	0		0
	2011920105	节日自选周卡-49.99	fes_weekly_card	fes_weekly_card		False	{"typ":"schema","id":[1,2,3,4,5,6,13,14,15,16,17,55]}	996	{"time_card":{"duration":604800}}	{"op":"and","args":[{"op":"eq","typ":"iap_purchases","id":2013920107,"val":0},{"op":"eq","typ":"iap_purchases","id":2013920108,"val":0},{"op":"eq","typ":"iap_purchases","id":2013920109,"val":0}]}	{}	[{"typ":"discount"},{"typ":"recharge_actv","id":211200093,"arg1":1511018855,"val":1}]	1	{}	common	0	0		0
```

## 2013 iap_template 新增行

```tsv
	2013920107	fes_weekly_card	2011920102	2014001	自选周卡-29.99	LC_EVENT_sci_time_card_title_2025_1		29.99	[{"pay_type":"gplay","product_id":"x2_2999_cd_an"},{"pay_type":"ios","product_id":"ape_2999_cd_ios"},{"pay_type":"aggregate","product_id":"x2_2999_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	7500	0	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11114319,"val":1},"setting":{"serial_number":100,"ishighlight":false}},{"asset":{"typ":"xp","id":11161002,"val":7500},"setting":{"serial_number":-96,"ishighlight":false}}]	[]	0	{}	1						[{"typ":"roi","tag":2,"val":168000}]	{}	0
	2013920108	fes_weekly_card	2011920103	2014001	自选周卡-19.99	LC_EVENT_sci_time_card_title_2025_2		19.99	[{"pay_type":"gplay","product_id":"x2_1999_cd_an"},{"pay_type":"ios","product_id":"ape_1999_cd_ios"},{"pay_type":"aggregate","product_id":"x2_1999_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	5000	0	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11114318,"val":1},"setting":{"serial_number":100,"ishighlight":false}},{"asset":{"typ":"xp","id":11161002,"val":5000},"setting":{"serial_number":-96,"ishighlight":false}}]	[]	0	{}	1						[{"typ":"roi","tag":2,"val":168000}]	{}	0
	2013920109	fes_weekly_card	2011920104	2014001	自选周卡-9.99	LC_EVENT_sci_time_card_title_2025_3		9.99	[{"pay_type":"gplay","product_id":"x2_0999_cd_an"},{"pay_type":"ios","product_id":"ape_0999_cd_ios"},{"pay_type":"aggregate","product_id":"x2_0999_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	2500	0	[]	[]	[]	[]	[{"asset":{"typ":"item","id":11114317,"val":1},"setting":{"serial_number":100,"ishighlight":false}},{"asset":{"typ":"xp","id":11161002,"val":2500},"setting":{"serial_number":-96,"ishighlight":false}}]	[]	0	{}	1						[{"typ":"roi","tag":2,"val":168000}]	{}	0
	2013920110	fes_weekly_card	2011920105	2014001	自选周卡-49.99	LC_IAP_sci_time_card_all_pkg	LC_IAP_fes_time_card_price_2	49.99	[{"pay_type":"gplay","product_id":"x2_4999_cd_an"},{"pay_type":"ios","product_id":"ape_4999_cd_ios"},{"pay_type":"aggregate","product_id":"x2_4999_cd_an"}]	{"limit_cnt":1,"limit_type":"period"}	1	12500	0	[]	[]	[]	[]	[{"asset":{"typ":"item","id":111111310,"val":1},"setting":{"serial_number":400,"ishighlight":false}},{"asset":{"typ":"item","id":111111311,"val":1},"setting":{"serial_number":300,"ishighlight":false}},{"asset":{"typ":"item","id":111111312,"val":1},"setting":{"serial_number":200,"ishighlight":false}},{"asset":{"typ":"item","id":11114319,"val":1},"setting":{"serial_number":100,"ishighlight":false}},{"asset":{"typ":"xp","id":11161002,"val":12500},"setting":{"serial_number":-96,"ishighlight":false}}]	[]	0	{}	1						[{"typ":"roi","tag":2,"val":168000}]	{}	0
```

## 1111 item 新增行

```tsv
	111111310	自选周卡解锁-1	item_subscription	0	404200	1511026509	1511010123	{}	{"typ":"lc","txt":"LC_EVENT_sci_time_card_title_2025_1"}	{}	{}	1000	999999999	999999999	999999999	["bag_other"]	[]	{"effect":[{"typ":"item_subscription","id":2013920107}]}	-1	1	[]	11740000	0	5	1511010005	0	0	0
	111111311	自选周卡解锁-2	item_subscription	0	404200	1511026507	1511010123	{}	{"typ":"lc","txt":"LC_EVENT_sci_time_card_title_2025_2"}	{}	{}	1000	999999999	999999999	999999999	["bag_other"]	[]	{"effect":[{"typ":"item_subscription","id":2013920108}]}	-1	1	[]	11740000	0	5	1511010005	0	0	0
	111111312	自选周卡解锁-3	item_subscription	0	404200	1511026508	1511010123	{}	{"typ":"lc","txt":"LC_EVENT_sci_time_card_title_2025_3"}	{}	{}	1000	999999999	999999999	999999999	["bag_other"]	[]	{"effect":[{"typ":"item_subscription","id":2013920109}]}	-1	1	[]	11740000	0	5	1511010005	0	0	0
```

## 2024 iap_custom_chest 新增行

```tsv
	20246031	2013920107	29.99自选周卡坑1	{"col":1,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116304,"val":3},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246032	2013920107	29.99自选周卡坑2	{"col":2,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119517,"val":12},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246033	2013920107	29.99自选周卡坑3	{"col":3,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119497,"val":24},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246034	2013920107	29.99自选周卡坑4	{"col":4,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111082,"val":6},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246035	2013920107	29.99自选周卡坑5	{"col":5,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11118501,"val":12},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246036	2013920107	29.99自选周卡坑6	{"col":6,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111083,"val":12},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246037	2013920107	29.99自选周卡坑7	{"col":7,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116604,"val":12},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246038	2013920107	29.99自选周卡坑8	{"col":8,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117069,"val":6},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246039	2013920107	29.99自选周卡坑9	{"col":9,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117068,"val":200},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246040	2013920107	29.99自选周卡坑10	{"col":10,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111105,"val":12},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246041	2013920108	19.99自选周卡坑1	{"col":1,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116304,"val":2},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246042	2013920108	19.99自选周卡坑2	{"col":2,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119517,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246043	2013920108	19.99自选周卡坑3	{"col":3,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119497,"val":16},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246044	2013920108	19.99自选周卡坑4	{"col":4,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111082,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246045	2013920108	19.99自选周卡坑5	{"col":5,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11118501,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246046	2013920108	19.99自选周卡坑6	{"col":6,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111083,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246047	2013920108	19.99自选周卡坑7	{"col":7,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116604,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246048	2013920108	19.99自选周卡坑8	{"col":8,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117069,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246049	2013920108	19.99自选周卡坑9	{"col":9,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117068,"val":120},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246050	2013920108	19.99自选周卡坑10	{"col":10,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111105,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246051	2013920109	9.99自选周卡坑1	{"col":1,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116304,"val":1},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246052	2013920109	9.99自选周卡坑2	{"col":2,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119517,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246053	2013920109	9.99自选周卡坑3	{"col":3,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11119497,"val":8},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246054	2013920109	9.99自选周卡坑4	{"col":4,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111082,"val":2},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246055	2013920109	9.99自选周卡坑5	{"col":5,"row":1}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11118501,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246056	2013920109	9.99自选周卡坑6	{"col":6,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111083,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246057	2013920109	9.99自选周卡坑7	{"col":7,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11116604,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246058	2013920109	9.99自选周卡坑8	{"col":8,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117069,"val":2},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246059	2013920109	9.99自选周卡坑9	{"col":9,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11117068,"val":60},"setting":{"serial_number":10,"ishighlight":false}}	1
	20246060	2013920109	9.99自选周卡坑10	{"col":10,"row":2}	{}	{}	{}	{}	{"asset":{"typ":"item","id":11111105,"val":4},"setting":{"serial_number":10,"ishighlight":false}}	1
```

## 导表顺序建议

1. 先粘贴新增行：`1111`、`2013`、`2024`、`2135`。
2. 再覆盖已有行：`2011`、`2112`。
3. 覆盖完成后检查 `2112 -> 2135 -> 2011 -> 2013 -> 2024/1111` 链路。
