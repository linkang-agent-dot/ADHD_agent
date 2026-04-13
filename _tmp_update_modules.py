# -*- coding: utf-8 -*-
"""
按情人节报告的分类规则给49条礼包归模块，并保存映射表供后续自动化。

模块规则（来自情人节Notion报告）:
  外显 - GACHA抽奖、行军特效、行军表情、装饰兑换券、皮肤类
  小游戏 - 挖孔/挖矿/推币机/对对碰/大富翁等小游戏
  混合 - BP通行证、限时抢购、连锁礼包、累充、掉落、周卡、bingo、酒馆等
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# ============ 礼包名称 → 模块 映射 ============
# 规则：先精确匹配，再关键词匹配
MODULE_EXACT = {
    "挖孔小游戏礼包":              "小游戏",
    "2026科技节弹珠GACHA":         "外显",
    "推币机礼包":                  "小游戏",
    "挖矿小游戏活动":              "小游戏",
    "推币机随机GACHA礼包":         "小游戏",
    "2025复活节大富翁礼包":        "小游戏",
    "限时抢购":                    "混合",
    "科技节高级通行证_2025":        "混合",
    "节日大富翁礼包":              "小游戏",
    "周年庆预购连锁_schema6":       "混合",
    "2025深海节-节日礼包团购":      "混合",
    "万圣节小连锁随机礼包":         "混合",
    "科技节初级通行证_2025":        "混合",
    "2026复活节-行军特效":          "外显",
    "节日大富翁":                   "小游戏",
    "2026科技节-行军表情":          "外显",
    "情人节BP":                    "混合",
    "25感恩节每日补给升级礼包":      "混合",
    "对对碰":                      "小游戏",
    "2026科技节集结奖励解锁礼包":    "混合",
    "掉落转付费礼包":               "混合",
    "2025深海节累充服务器礼包":      "混合",
    "2025复活节-强消耗抽奖券礼包":   "混合",
    "科技节自选周卡":               "混合",
    "节日大富翁组队礼包":           "小游戏",
    "kvk基因高级bp通行证":          "混合",
    "kvk基因bp通行证":              "混合",
    "2023装饰兑换券礼包":           "外显",
    "节日挖矿-砍价礼包-折扣5":      "小游戏",
    "改造猴特权-节日版":            "混合",
    "周年庆预购连锁礼包_schema3-5":  "混合",
    "酒馆登陆bp":                   "混合",
    "2026科技节wonder巨猿砸蛋锤礼包":"外显",
    "2025周年庆累充服务器礼包":      "混合",
    "挖矿小游戏-卡包礼包-节日版本":  "小游戏",
    "成长线1+1礼包":               "混合",
    "情人节bingo活动宝箱礼包":       "混合",
    "2025复活节强消耗触发礼包":      "混合",
    "挖矿小游戏":                   "小游戏",
    "休眠仓":                      "混合",
    "kvk基因高级bp通行证-V81-kvk5":  "混合",
    "节日挖矿-砍价礼包":            "小游戏",
    "千万下载礼包":                 "混合",
    "泳池派对礼包":                 "混合",
    "2022幼猴节gacha礼包":          "外显",
    "挖矿小游戏-产量翻倍特权":       "小游戏",
    "基因bp通行证BP积分礼包":        "混合",
    "转盘折扣小额":                 "混合",
    "2023幼猴节-7日活动宝箱":        "混合",
}

# 关键词规则（用于未来新礼包自动推断）
KEYWORD_RULES = [
    (["gacha", "GACHA", "抽奖"],                          "外显"),
    (["行军特效", "行军表情", "装饰兑换券", "皮肤"],        "外显"),
    (["挖孔", "挖矿", "推币机", "大富翁", "对对碰",
      "小游戏", "扭蛋机"],                                "小游戏"),
    (["通行证", "bp", "BP", "周卡", "限时抢购",
      "连锁", "累充", "掉落", "bingo", "酒馆",
      "集结", "解锁", "补给", "宝箱", "转盘"],             "混合"),
]

def infer_module(name: str) -> str:
    if name in MODULE_EXACT:
        return MODULE_EXACT[name]
    name_lower = name.lower()
    for keywords, module in KEYWORD_RULES:
        if any(k.lower() in name_lower for k in keywords):
            return module
    return "混合"  # 默认


# ============ 读入 JSON，更新 activity_ranking 的 module ============
with open(r'C:\ADHD_agent\_tech_fest_input.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data["activity_ranking"]:
    item["module"] = infer_module(item["name"])

# 写回
with open(r'C:\ADHD_agent\_tech_fest_input.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ============ 同时保存模块映射表（供后续自动化） ============
mapping_output = {
    "version": "1.0",
    "description": "节日礼包模块归类映射表（来源：情人节+科技节Notion复盘报告）",
    "exact_map": MODULE_EXACT,
    "keyword_rules": [
        {"keywords": kws, "module": mod}
        for kws, mod in KEYWORD_RULES
    ]
}
with open(r'C:\ADHD_agent\skills\generate_event_review\iap_module_map.json', 'w', encoding='utf-8') as f:
    json.dump(mapping_output, f, ensure_ascii=False, indent=2)

# ============ 打印结果 ============
print("=== 归类结果 ===")
stats = {}
for item in data["activity_ranking"]:
    m = item["module"]
    stats[m] = stats.get(m, 0) + 1
    print(f"  [{m:4s}] {item['name']}")

print()
print("=== 模块汇总 ===")
for mod, cnt in sorted(stats.items()):
    rev = sum(i["revenue"] for i in data["activity_ranking"] if i["module"] == mod)
    print(f"  {mod}: {cnt}种礼包, 总收入 ${rev:,.2f}")

print()
print("映射表已保存到: skills/generate_event_review/iap_module_map.json")
