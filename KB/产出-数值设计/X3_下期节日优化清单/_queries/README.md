# 大富翁纪念卡 数据查询脚本（2026-07-23 固化，防 scratchpad 清空丢失）

深海大富翁纪念卡（远航之歌 180080）付费×获取分析用。窗口 7/3–7/16 · 深海 59 服。
连接：`sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")` → `from query_trino import execute_sql`；`execute_sql(sql, datasource="TRINO_HF", limit=N)["data"]`。
输出 json 落在 `..\assets\`。

| 脚本 | 查什么 | 关键结论 |
|---|---|---|
| `_card_vs_spend.py` | 大富翁付费额度档 × 纪念卡180080获取(直发+实获) | 付费直发$196/张、实获blend$21.8/张 |
| `_redeem_pay.py` | 大富翁集市(1341/代币1202)各兑换品 + 兑换者付费均值 | 美人鱼梦境26%代币第一;高价外显仅13/86人100%付费 |
| `_card_dist.py` | 远航之歌兑卡张数分布(全量/付费/免费) | 免费72%只1张、付费10+张占10.2% |
| `_wheel_card.py` | 转盘集市(1340/宝珠1201/400宝珠)兑远航之歌总量 | 1978张(93.5%) vs 成就直发137张(6.5%) |
| `_token_price.py` | 代币1202经济 + 大富翁集市卡实际单价 | 3000代币≈$1.5/张(上限) |
| `_orb2.py` | 宝珠1201产出 + 转盘各模块付费 | 转盘$12558/宝珠385万→$0.00326/颗·400宝珠≈$1.3 |
| `_funnel.py` | 纪念卡兑换转化漏斗(全量vs付费) | 付费兑卡40% vs 全量24% |
| `_tail.py` | 10+张尾巴明细(每张数/付费/来源) | 深度集卡(10-46张)全靠刷集市非付费 |

⚠️ 口径坑：①ods_user_asset 无 change_reason，用 `reason_id`+`reason_sub_id`(集市兑换=`activity_exchange`/`101341_134XXX`或`101340_134002`)；②深海**两集市两货币两卡**别混（详见 memory `reference_x3_deepsea_memorial_card`）。大富翁付费口径=成就2801001-011+罗盘连锁207104-112+存钱罐280001+BP130036/037。
