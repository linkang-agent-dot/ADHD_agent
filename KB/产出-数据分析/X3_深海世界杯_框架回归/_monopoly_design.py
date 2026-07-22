# -*- coding: utf-8 -*-
"""深海大富翁族 设计回溯归因数据层（07-21 用户要求补深度）：
① 堆件解剖：买家买了几件（1/2/3/4）分布 + 各件买家与"其他件"重叠率 → 验"堆买断件"到底是同一批人买多件还是各件各拉一批人
② 双周逐日曲线：族各件按日收入 → 验设计"W2 大富翁攻付费深度"实际有没有走出第二周曲线
③ SKU 档位结构：各件按 pay_price 档位 买家/单数/收入 → 验成就"后6档$99.99重复"等设计点的实际吸收
产出 _monopoly_design.json。窗口 7/3-7/16 · 59服。
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
S, E = "2026-07-03", "2026-07-16"
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
COMP = {
  "成就礼包": [f"280100{i}" for i in range(1,10)]+["2801010","2801011"],
  "罗盘连锁": [str(x) for x in range(207104,207113)],
  "存钱罐": ["280001"],
  "BP大富翁线": ["130036","130037"],
}
ALL_IDS = ",".join(f"'{x}'" for name in COMP for x in COMP[name])
CASE_COMP = "CASE " + " ".join(
    f"WHEN iap_id IN ({','.join(chr(39)+x+chr(39) for x in ids)}) THEN '{name}'" for name, ids in COMP.items()) + " END"

def q(sql):
    return execute_sql(sql, datasource="TRINO_HF")["data"]

out = {"window": [S, E]}
base = f"""FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
    AND server_id IN ({SRV59}) AND iap_id IN ({ALL_IDS})"""

# ① 买了几件 分布 + ARPPU
rows = q(f"""SELECT n_comp, count(1) buyers, round(sum(tot),0) rev, round(max(tot),0) mx
  FROM (SELECT user_id, count(distinct comp) n_comp, sum(s) tot FROM (
    SELECT user_id, {CASE_COMP} comp, sum({USD}) s {base} GROUP BY user_id, {CASE_COMP}) GROUP BY user_id)
  GROUP BY 1 ORDER BY 1""")
out["piece_count"] = [dict(n=r["n_comp"], buyers=r["buyers"], rev=float(r["rev"]),
                           arppu=float(r["rev"])/r["buyers"], mx=float(r["mx"])) for r in rows]
print("① 买几件分布:")
for r in out["piece_count"]:
    print(f"   {r['n']}件: {r['buyers']}人 ${r['rev']:,.0f} ARPPU${r['arppu']:.0f} max${r['mx']:,.0f}")

# 各件买家与其他件的重叠率
out["overlap"] = {}
for name in COMP:
    ids = ",".join(f"'{x}'" for x in COMP[name])
    d = q(f"""WITH mine AS (SELECT DISTINCT user_id {base} AND iap_id IN ({ids})),
      other AS (SELECT DISTINCT user_id {base} AND iap_id NOT IN ({ids}))
      SELECT count(1) n, count_if(o.user_id IS NOT NULL) ov
      FROM mine m LEFT JOIN other o ON m.user_id=o.user_id""")[0]
    out["overlap"][name] = dict(buyers=d["n"], with_other=d["ov"], pct=d["ov"]/d["n"]*100 if d["n"] else 0)
    print(f"   {name}: 买家{d['n']} 同时买其他件{d['ov']}({d['ov']/d['n']*100:.0f}%)")

# ② 各件逐日收入
rows = q(f"""SELECT partition_date d, {CASE_COMP} comp, round(sum({USD}),0) rev, count(distinct user_id) buyers
  {base} GROUP BY 1,2 ORDER BY 1""")
daily = {}
for r in rows:
    daily.setdefault(r["d"], {})[r["comp"]] = dict(rev=float(r["rev"]), buyers=r["buyers"])
out["daily"] = daily
print("\n② 逐日(族合计):")
for d in sorted(daily):
    tot = sum(v["rev"] for v in daily[d].values())
    print(f"   {d}: ${tot:,.0f}")

# ③ SKU 档位结构（按件×pay_price；USD口径下同价合并）
out["tiers"] = {}
for name, ids in COMP.items():
    idset = ",".join(f"'{x}'" for x in ids)
    rows = q(f"""SELECT pay_price p, count(distinct user_id) buyers, count(1) orders, round(sum({USD}),0) rev
      {base.replace(ALL_IDS, idset)} GROUP BY 1 ORDER BY 1""")
    out["tiers"][name] = [dict(price=float(r["p"]), buyers=r["buyers"], orders=r["orders"],
                               rev=float(r["rev"]), opb=r["orders"]/r["buyers"]) for r in rows]
    print(f"\n③ {name} 档位:")
    for t in out["tiers"][name]:
        print(f"   ${t['price']:>6.2f}: 买家{t['buyers']:>4} 单数{t['orders']:>5} 人均{t['opb']:.1f}单 ${t['rev']:,.0f}")

# ④ 兑换商店（大富翁集市1341 · 货币=深海宝珠 Item_1202）产出/消耗
ex = {}
for label, ct in [("produce", "1"), ("consume", "2")]:
    d = q(f"""SELECT count(distinct user_id) users, round(sum(TRY_CAST(change_count AS double)),0) amt
      FROM v1090.ods_user_asset
      WHERE partition_date BETWEEN '{S}' AND '{E}' AND asset_id='Item_1202' AND change_type='{ct}'
        AND server_id IN ({SRV59})""")[0]
    ex[label] = dict(users=d["users"], amt=float(d["amt"] or 0))
out["exchange_1202"] = ex
print(f"\n④ 宝珠1202: 产出 {ex['produce']['users']:,}人/{ex['produce']['amt']:,.0f} · 消耗 {ex['consume']['users']:,}人/{ex['consume']['amt']:,.0f} · 回收率{ex['consume']['amt']/ex['produce']['amt']*100 if ex['produce']['amt'] else 0:.0f}%")

# ⑥ 成就礼包 SKU 漏斗：各档解锁圈数→掷骰阈值→到达人数 + 按包id购买人数
# 解锁圈数（Pack__AchievePack 104 行 UnlockParameterList）；棋盘24格(Island组2)/骰1-6均值3.5 → 1圈≈6.857次
LAPS = [3, 5, 10, 20, 30, 50, 70, 100, 150, 200, 300]
ROLLS_PER_LAP = 24 / 3.5
ACH_IDS = [f"280100{i}" for i in range(1, 10)] + ["2801010", "2801011"]
dice_cte = f"""SELECT user_id, sum(TRY_CAST(change_count AS double)) rolls
  FROM v1090.ods_user_asset WHERE partition_date BETWEEN '{S}' AND '{E}' AND change_type='2'
    AND asset_id IN ('Item_1057','Item_1058') AND server_id IN ({SRV59}) GROUP BY user_id"""
# 付费玩家基底（用户07-21定：转化率类数据分母=付费玩家，免费玩家稀释无意义）：窗口内任意付费者
payer_all_cte = f"""SELECT DISTINCT user_id FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV59})"""
th_sel = ",".join(f"count_if(rolls>={int(round(l*ROLLS_PER_LAP))}) c{i},"
                  f"count_if(rolls>={int(round(l*ROLLS_PER_LAP))} AND p.user_id IS NOT NULL) p{i}"
                  for i, l in enumerate(LAPS))
reach = q(f"""WITH d AS ({dice_cte}), p AS ({payer_all_cte})
  SELECT {th_sel}, count_if(p.user_id IS NOT NULL) dice_payers_any
  FROM d LEFT JOIN p ON d.user_id=p.user_id""")[0]
out["dice_payers_any"] = reach["dice_payers_any"]
buy = {r["iap_id"]: r["b"] for r in q(f"""SELECT iap_id, count(distinct user_id) b
  {base} AND iap_id IN ({",".join(chr(39)+x+chr(39) for x in ACH_IDS)}) GROUP BY 1""")}
PRICES = [1.99, 4.99, 9.99, 19.99, 49.99] + [99.99]*6
out["achieve_funnel"] = [dict(pack=ACH_IDS[i], price=PRICES[i], laps=LAPS[i],
                              rolls=int(round(LAPS[i]*ROLLS_PER_LAP)),
                              reach=reach[f"c{i}"], reach_payer=reach[f"p{i}"],
                              buyers=buy.get(ACH_IDS[i], 0))
                         for i in range(len(LAPS))]
print(f"\n⑥ 成就礼包 SKU 漏斗（掷骰玩家中窗口付费玩家 {reach['dice_payers_any']:,}）:")
for r in out["achieve_funnel"]:
    rate = r["buyers"]/r["reach_payer"]*100 if r["reach_payer"] else 0
    print(f"   {r['pack']} ${r['price']:>6.2f} @{r['laps']:>3}圈(≈{r['rolls']:>4}次): 到达{r['reach']:>5}(付费{r['reach_payer']:>5}) 购买{r['buyers']:>4} 购买率(÷到达付费){rate:.0f}%")

# ⑦ 付费玩家单独 survival（族付费 vs 非族付费玩家，同掷骰阈值）——付费玩家放大图用
FAM_CTE = f"""SELECT DISTINCT user_id FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{E}'
    AND server_id IN ({SRV59}) AND iap_id IN ({ALL_IDS})"""
THRESH7 = [1, 20, 50, 100, 150, 250, 350, 500, 700, 1000, 1500, 2000]
sel7 = ",".join(f"count_if(rolls>={t} AND f.user_id IS NOT NULL) f{t},"
                f"count_if(rolls>={t} AND f.user_id IS NULL AND p.user_id IS NOT NULL) n{t}"
                for t in THRESH7)
r7 = q(f"""WITH d AS ({dice_cte}), p AS ({payer_all_cte}), f AS ({FAM_CTE})
  SELECT {sel7} FROM d LEFT JOIN p ON d.user_id=p.user_id LEFT JOIN f ON d.user_id=f.user_id""")[0]
out["payer_survival"] = {"thresh": THRESH7,
                         "fam": {str(t): r7[f"f{t}"] for t in THRESH7},
                         "nonfam": {str(t): r7[f"n{t}"] for t in THRESH7}}
print("\n⑦ 付费玩家掷骰 survival（族付费 / 非族付费玩家）:")
for t in THRESH7:
    print(f"   ≥{t:>5}次: 族付费{r7[f'f{t}']:>5} 非族付费{r7[f'n{t}']:>5}")

# ⑤ 触达漏斗 + 道具使用漏斗
# 顶=59服窗口活跃；触达=领到过罗盘(1057/1058产出)；参与=掷过骰(消耗)；付费=族买家
act = q(f"""SELECT count(distinct user_id) u FROM v1090.ods_user_login
  WHERE partition_date BETWEEN '{S}' AND '{E}' AND server_id IN ({SRV59})""")[0]
dice_prod = q(f"""SELECT count(distinct user_id) users, round(sum(TRY_CAST(change_count AS double)),0) amt
  FROM v1090.ods_user_asset WHERE partition_date BETWEEN '{S}' AND '{E}' AND change_type='1'
    AND asset_id IN ('Item_1057','Item_1058') AND server_id IN ({SRV59})""")[0]
out["funnel"] = dict(active=act["u"], dice_reached=dice_prod["users"],
                     dice_prod_amt=float(dice_prod["amt"] or 0))
print(f"\n⑤ 触达漏斗: 活跃{act['u']:,} → 领罗盘{dice_prod['users']:,} → 掷骰{out['dice_total_players'] if 'dice_total_players' in out else 7069:,}")
print(f"   罗盘: 发放{float(dice_prod['amt'] or 0):,.0f} vs 消耗{2138834:,.0f}")

json.dump(out, open(os.path.join(HERE, "_monopoly_design.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _monopoly_design.json")
