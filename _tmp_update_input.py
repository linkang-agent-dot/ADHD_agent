# -*- coding: utf-8 -*-
"""把图表9的49条礼包数据写入_tech_fest_input.json的activity_ranking"""
import sys, json, math
sys.stdout.reconfigure(encoding='utf-8')

# 图表9查询结果（完整49条）
raw_data = [
    {"iap_id_name": "挖孔小游戏礼包",              "pay_user_cnt": 2710, "buy_times": 11693, "revenue": 206191.07},
    {"iap_id_name": "2026科技节弹珠GACHA",          "pay_user_cnt": 1170, "buy_times": 6466,  "revenue": 129800.34},
    {"iap_id_name": "推币机礼包",                  "pay_user_cnt": 1110, "buy_times": 4326,  "revenue": 64041.74},
    {"iap_id_name": "挖矿小游戏活动",              "pay_user_cnt": 1176, "buy_times": 10988, "revenue": 60391.12},
    {"iap_id_name": "推币机随机GACHA礼包",          "pay_user_cnt": 458,  "buy_times": 1559,  "revenue": 56054.41},
    {"iap_id_name": "2025复活节大富翁礼包",         "pay_user_cnt": 1542, "buy_times": 4911,  "revenue": 47420.89},
    {"iap_id_name": "限时抢购",                    "pay_user_cnt": 447,  "buy_times": 1240,  "revenue": 45857.60},
    {"iap_id_name": "科技节高级通行证_2025",         "pay_user_cnt": 1180, "buy_times": 1180,  "revenue": 23588.20},
    {"iap_id_name": "节日大富翁礼包",              "pay_user_cnt": 161,  "buy_times": 216,   "revenue": 18297.84},
    {"iap_id_name": "周年庆预购连锁_schema6",        "pay_user_cnt": 180,  "buy_times": 180,   "revenue": 17998.20},
    {"iap_id_name": "2025深海节-节日礼包团购",       "pay_user_cnt": 1224, "buy_times": 2627,  "revenue": 17944.73},
    {"iap_id_name": "万圣节小连锁随机礼包",          "pay_user_cnt": 1430, "buy_times": 3378,  "revenue": 15811.22},
    {"iap_id_name": "科技节初级通行证_2025",         "pay_user_cnt": 2010, "buy_times": 2010,  "revenue": 14049.90},
    {"iap_id_name": "2026复活节-行军特效",           "pay_user_cnt": 663,  "buy_times": 663,   "revenue": 13253.37},
    {"iap_id_name": "节日大富翁",                   "pay_user_cnt": 2191, "buy_times": 2422,  "revenue": 12726.78},
    {"iap_id_name": "2026科技节-行军表情",           "pay_user_cnt": 2255, "buy_times": 2255,  "revenue": 11252.45},
    {"iap_id_name": "情人节BP",                    "pay_user_cnt": 709,  "buy_times": 1148,  "revenue": 10918.52},
    {"iap_id_name": "25感恩节每日补给升级礼包",       "pay_user_cnt": 1787, "buy_times": 4709,  "revenue": 9370.91},
    {"iap_id_name": "对对碰",                      "pay_user_cnt": 510,  "buy_times": 868,   "revenue": 7695.32},
    {"iap_id_name": "2026科技节集结奖励解锁礼包",     "pay_user_cnt": 1279, "buy_times": 1280,  "revenue": 6387.20},
    {"iap_id_name": "掉落转付费礼包",               "pay_user_cnt": 820,  "buy_times": 974,   "revenue": 6030.26},
    {"iap_id_name": "2025深海节累充服务器礼包",       "pay_user_cnt": 502,  "buy_times": 502,   "revenue": 5784.98},
    {"iap_id_name": "2025复活节-强消耗抽奖券礼包",    "pay_user_cnt": 280,  "buy_times": 389,   "revenue": 5466.11},
    {"iap_id_name": "科技节自选周卡",               "pay_user_cnt": 120,  "buy_times": 121,   "revenue": 5183.79},
    {"iap_id_name": "节日大富翁组队礼包",            "pay_user_cnt": 279,  "buy_times": 439,   "revenue": 4385.61},
    {"iap_id_name": "kvk基因高级bp通行证",           "pay_user_cnt": 37,   "buy_times": 37,    "revenue": 3699.63},
    {"iap_id_name": "kvk基因bp通行证",              "pay_user_cnt": 244,  "buy_times": 245,   "revenue": 3672.55},
    {"iap_id_name": "2023装饰兑换券礼包",            "pay_user_cnt": 81,   "buy_times": 132,   "revenue": 3653.68},
    {"iap_id_name": "节日挖矿-砍价礼包-折扣5",        "pay_user_cnt": 954,  "buy_times": 1709,  "revenue": 3400.91},
    {"iap_id_name": "改造猴特权-节日版",             "pay_user_cnt": 310,  "buy_times": 310,   "revenue": 3096.90},
    {"iap_id_name": "周年庆预购连锁礼包_schema3-5",   "pay_user_cnt": 29,   "buy_times": 29,    "revenue": 2899.71},
    {"iap_id_name": "酒馆登陆bp",                   "pay_user_cnt": 87,   "buy_times": 150,   "revenue": 2128.50},
    {"iap_id_name": "2026科技节wonder巨猿砸蛋锤礼包", "pay_user_cnt": 207,  "buy_times": 207,   "revenue": 2067.93},
    {"iap_id_name": "2025周年庆累充服务器礼包",       "pay_user_cnt": 100,  "buy_times": 100,   "revenue": 2049.00},
    {"iap_id_name": "挖矿小游戏-卡包礼包-节日版本",    "pay_user_cnt": 161,  "buy_times": 400,   "revenue": 1996.00},
    {"iap_id_name": "成长线1+1礼包",               "pay_user_cnt": 154,  "buy_times": 184,   "revenue": 1618.38},
    {"iap_id_name": "情人节bingo活动宝箱礼包",        "pay_user_cnt": 301,  "buy_times": 301,   "revenue": 1501.99},
    {"iap_id_name": "2025复活节强消耗触发礼包",       "pay_user_cnt": 390,  "buy_times": 404,   "revenue": 1332.96},
    {"iap_id_name": "挖矿小游戏",                   "pay_user_cnt": 142,  "buy_times": 219,   "revenue": 1097.81},
    {"iap_id_name": "休眠仓",                      "pay_user_cnt": 83,   "buy_times": 195,   "revenue": 973.05},
    {"iap_id_name": "kvk基因高级bp通行证-V81-kvk5",  "pay_user_cnt": 7,    "buy_times": 7,     "revenue": 699.93},
    {"iap_id_name": "节日挖矿-砍价礼包",             "pay_user_cnt": 32,   "buy_times": 41,    "revenue": 694.59},
    {"iap_id_name": "千万下载礼包",                 "pay_user_cnt": 43,   "buy_times": 77,    "revenue": 675.23},
    {"iap_id_name": "泳池派对礼包",                 "pay_user_cnt": 11,   "buy_times": 23,    "revenue": 604.77},
    {"iap_id_name": "2022幼猴节gacha礼包",           "pay_user_cnt": 8,    "buy_times": 16,    "revenue": 479.84},
    {"iap_id_name": "挖矿小游戏-产量翻倍特权",        "pay_user_cnt": 87,   "buy_times": 120,   "revenue": 358.80},
    {"iap_id_name": "基因bp通行证BP积分礼包",         "pay_user_cnt": 25,   "buy_times": 38,    "revenue": 294.62},
    {"iap_id_name": "转盘折扣小额",                 "pay_user_cnt": 11,   "buy_times": 13,    "revenue": 131.87},
    {"iap_id_name": "2023幼猴节-7日活动宝箱",         "pay_user_cnt": 18,   "buy_times": 18,    "revenue": 89.82},
]

TOTAL_REV = 855121.03

# 生成activity_ranking条目
activity_ranking = []
for row in raw_data:
    rev = row["revenue"]
    users = row["pay_user_cnt"]
    times = row["buy_times"]
    activity_ranking.append({
        "name":          row["iap_id_name"],
        "module":        "",           # 用户手动改
        "revenue":       round(rev, 2),
        "share":         round(rev / TOTAL_REV * 100, 2),
        "buy_times":     times,
        "unique_buyers": users,
        "times_arppu":   round(rev / times, 2) if times > 0 else 0,
        "event_arpu":    round(rev / users, 2) if users > 0 else 0,
        "sku_count":     0
    })

# 读入原json
with open(r'C:\ADHD_agent\_tech_fest_input.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 替换activity_ranking
data["activity_ranking"] = activity_ranking

# 写回
with open(r'C:\ADHD_agent\_tech_fest_input.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"已写入 {len(activity_ranking)} 条礼包数据到 activity_ranking")
print("前5条预览:")
for item in activity_ranking[:5]:
    print(f"  {item['name']}: rev={item['revenue']}, users={item['unique_buyers']}, arpu={item['event_arpu']}, share={item['share']}%")
