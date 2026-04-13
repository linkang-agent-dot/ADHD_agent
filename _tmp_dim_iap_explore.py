# -*- coding: utf-8 -*-
"""
探查 dim_iap 的完整字段，以及节日活动礼包的名称/分类分布
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# 1. 看 dim_iap 全部列
print("=== dim_iap 列名 ===", flush=True)
rows = api.execute_sql("SELECT * FROM v1041.dim_iap LIMIT 1")
if rows:
    print("列:", list(rows[0].keys()))
    print("样本:", json.dumps(rows[0], ensure_ascii=False, default=str)[:500])

# 2. 查节日活动礼包的所有名称，看有没有额外分类字段
print("\n=== 节日活动礼包名称样本（取最近6个月） ===", flush=True)
SQL = """
SELECT iap_id, iap_id_name, iap_type
FROM v1041.dim_iap
WHERE iap_type = '混合-节日活动'
ORDER BY iap_id DESC
LIMIT 200
"""
rows2 = api.execute_sql(SQL)
print(f"共 {len(rows2)} 条")

# 统计关键词，找出"其他"里都是什么
known_keywords = ["挖孔", "推币", "挖矿", "大富翁", "对对碰", "弹珠", "GACHA", "gacha",
                   "头像框", "铭牌", "行军", "装饰", "皮肤", "通行证", "BP", "bp",
                   "团购", "每日补给", "限时", "预购", "连锁", "集结"]
others = []
for r in rows2:
    name = r.get('iap_id_name', '')
    matched = any(k in name for k in known_keywords)
    if not matched:
        others.append(name)

print(f"\n未匹配到已知关键词的礼包名（共 {len(others)} 条）：")
for n in sorted(set(others)):
    print(f"  {n}")
