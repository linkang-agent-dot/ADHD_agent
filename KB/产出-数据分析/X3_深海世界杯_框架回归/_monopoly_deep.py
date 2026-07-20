# -*- coding: utf-8 -*-
"""
深海大富翁族 深度下钻（交接包待做②③ + 05章铺开数据层）
① 进度停留曲线：玩家累计掷骰次数(Item_1057普通+Item_1058精准, change_type=2) survival
   分桶对齐阶段奖档 OtherReward组100（抽20/50/100/150/250/350/500/700）
   三条线：全量掷骰玩家 / 大富翁族付费玩家 / 未付费(纯白嫖)玩家
② 新老服拆分：大富翁族买家按服段（成熟老服1170-1870 vs 年轻服1880-2010）拆付费率/ARPPU
③ 族扩张历史坐标：深海四件套 vs 老版航海之路(纯连锁207xxx)按月
产出 _monopoly_deep.json
口径铁律见 交接_深海大富翁回归.md 第五节
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-16"
S = "2026-07-03"
HERE = os.path.dirname(os.path.abspath(__file__))
USD = "CASE WHEN currency_type='usd' THEN actual_charge ELSE pay_price END"
SRV59 = ",".join(f"'{x}'" for x in [1170,1270,1310,1350,1390,1400,1420,1440,1460,1510,1530,1540,1550,1560,1570,1580,1590,1600,1610,1620,1630,1640,1650,1660,1670,1680,1690,1700,1710,1720,1730,1740,1750,1760,1770,1780,1790,1800,1810,1820,1830,1840,1850,1860,1870,1880,1890,1900,1910,1920,1930,1940,1950,1960,1970,1980,1990,2000,2010])
# 大富翁族付费包
FAMILY = [f"280100{i}" for i in range(1,10)] + ["2801010","2801011"] + [str(x) for x in range(207104,207113)] + ["280001","130036","130037"]
FAM_IDS = ",".join(f"'{x}'" for x in FAMILY)

def q(sql):
    return execute_sql(sql, datasource="TRINO_HF")["data"]

out = {"END": END, "window": [S, END]}

# ========== ① 进度停留曲线 ==========
# 每玩家累计掷骰次数（普通1057+精准1058消耗）
dice_cte = f"""SELECT user_id, sum(TRY_CAST(change_count AS double)) rolls
  FROM v1090.ods_user_asset
  WHERE partition_date BETWEEN '{S}' AND '{END}' AND change_type='2'
    AND asset_id IN ('Item_1057','Item_1058') AND server_id IN ({SRV59})
  GROUP BY user_id"""
# 大富翁族付费玩家集合
payer_cte = f"""SELECT DISTINCT user_id FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{END}'
    AND server_id IN ({SRV59}) AND iap_id IN ({FAM_IDS})"""

THRESH = [1,20,50,100,150,250,350,500,700]
surv = {"all": {}, "payer": {}, "free": {}}
base = q(f"""WITH d AS ({dice_cte}), p AS ({payer_cte})
  SELECT count(1) all_n,
    count_if(p.user_id IS NOT NULL) pay_n,
    count_if(p.user_id IS NULL) free_n,
    round(sum(d.rolls),0) all_rolls
  FROM d LEFT JOIN p ON d.user_id=p.user_id""")[0]
out["dice_total_players"] = base["all_n"]
out["dice_payers"] = base["pay_n"]
out["dice_free"] = base["free_n"]
out["dice_total_rolls"] = float(base["all_rolls"])
for t in THRESH:
    r = q(f"""WITH d AS ({dice_cte}), p AS ({payer_cte})
      SELECT count_if(d.rolls>={t}) a,
        count_if(d.rolls>={t} AND p.user_id IS NOT NULL) pa,
        count_if(d.rolls>={t} AND p.user_id IS NULL) fa
      FROM d LEFT JOIN p ON d.user_id=p.user_id""")[0]
    surv["all"][t] = r["a"]; surv["payer"][t] = r["pa"]; surv["free"][t] = r["fa"]
out["survival"] = surv
# 掷骰次数分位数（全量 / 付费）
for lab, extra in [("all",""), ("payer"," AND p.user_id IS NOT NULL")]:
    d = q(f"""WITH d AS ({dice_cte}), p AS ({payer_cte})
      SELECT approx_percentile(d.rolls, ARRAY[0.5,0.75,0.9,0.95,0.99]) qs, round(max(d.rolls),0) mx
      FROM d LEFT JOIN p ON d.user_id=p.user_id WHERE 1=1{extra}""")[0]
    qs = d["qs"] if isinstance(d["qs"], list) else json.loads(str(d["qs"]))
    out[f"dice_pct_{lab}"] = dict(p50=float(qs[0]),p75=float(qs[1]),p90=float(qs[2]),p95=float(qs[3]),p99=float(qs[4]),mx=float(d["mx"]))
print(f"① 掷骰玩家 全量{base['all_n']:,} / 族付费{base['pay_n']:,} / 白嫖{base['free_n']:,} · 总掷骰{float(base['all_rolls']):,.0f}次")
for t in THRESH:
    print(f"   ≥{t:>4}次: 全量{surv['all'][t]:>5} 付费{surv['payer'][t]:>5} 白嫖{surv['free'][t]:>5}")
print(f"   分位 全量 p50/{out['dice_pct_all']['p50']:.0f} p90/{out['dice_pct_all']['p90']:.0f} p99/{out['dice_pct_all']['p99']:.0f} max{out['dice_pct_all']['mx']:.0f}")
print(f"   分位 付费 p50/{out['dice_pct_payer']['p50']:.0f} p90/{out['dice_pct_payer']['p90']:.0f} p99/{out['dice_pct_payer']['p99']:.0f} max{out['dice_pct_payer']['mx']:.0f}")

# ========== ② 新老服拆分 ==========
# 大富翁族买家 按服段
seg_sql = f"""SELECT CASE WHEN CAST(server_id AS integer)<1880 THEN 'mature' ELSE 'young' END seg,
    count(distinct user_id) buyers, round(sum({USD}),0) rev
  FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{END}'
    AND server_id IN ({SRV59}) AND iap_id IN ({FAM_IDS})
  GROUP BY 1"""
# 各段总付费人数（分母）
den_sql = f"""SELECT CASE WHEN CAST(server_id AS integer)<1880 THEN 'mature' ELSE 'young' END seg,
    count(distinct user_id) payers FROM v1090.ods_user_order
  WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{END}' AND server_id IN ({SRV59}) GROUP BY 1"""
den = {r["seg"]: r["payers"] for r in q(den_sql)}
out["server_seg"] = {}
for r in q(seg_sql):
    seg = r["seg"]; b=r["buyers"]; rev=float(r["rev"])
    out["server_seg"][seg] = dict(buyers=b, rev=rev, payers=den.get(seg,0),
        payrate=b/den[seg]*100 if den.get(seg) else 0, arppu=rev/b if b else 0)
print("\n② 新老服拆分（大富翁族）")
for seg in ["mature","young"]:
    s=out["server_seg"].get(seg,{})
    if s: print(f"   {seg}: 买家{s['buyers']} 收入${s['rev']:,.0f} 付费率{s['payrate']:.1f}%(分母{s['payers']:,}) ARPPU${s['arppu']:.1f}")

# ========== ③ 族扩张 历史坐标（老版航海之路纯连锁 按月 vs 深海族分件） ==========
# 老版连锁族(207102-207113付费+13017-020锚点) 按月
hist_sql = f"""SELECT substr(partition_date,1,7) m, count(distinct user_id) buyers, round(sum({USD}),0) rev
  FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date >= '2026-01-01'
  AND iap_id IN ({",".join(chr(39)+str(x)+chr(39) for x in list(range(207102,207114))+[13017,13018,13019,13020])})
  GROUP BY 1 ORDER BY 1"""
out["chain_by_month"] = [dict(m=r["m"],buyers=r["buyers"],rev=float(r["rev"])) for r in q(hist_sql)]
print("\n③ 老版航海之路连锁族 按月")
for r in out["chain_by_month"]:
    print(f"   {r['m']}: 买家{r['buyers']} ${r['rev']:,.0f}")

# 深海族分件（59服窗内）——复用L1口径，这里独立再算含max/复购
COMP = {
  "成就礼包": [f"280100{i}" for i in range(1,10)]+["2801010","2801011"],
  "罗盘连锁": [str(x) for x in range(207104,207113)],
  "存钱罐": ["280001"],
  "BP大富翁线": ["130036","130037"],
}
out["deepsea_components"] = {}
for name, plist in COMP.items():
    idset = ",".join(f"'{x}'" for x in plist)
    d = q(f"""SELECT count(distinct user_id) buyers, round(sum({USD}),0) rev, count(1) orders
      FROM v1090.ods_user_order WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{END}'
      AND server_id IN ({SRV59}) AND iap_id IN ({idset})""")[0]
    mx = q(f"""SELECT round(max(tot),0) mx FROM (SELECT user_id,sum({USD}) tot FROM v1090.ods_user_order
      WHERE pay_status=1 AND partition_date BETWEEN '{S}' AND '{END}' AND server_id IN ({SRV59})
      AND iap_id IN ({idset}) GROUP BY user_id) t""")[0]
    b=d["buyers"]; rev=float(d["rev"] or 0); o=d["orders"] or 0
    out["deepsea_components"][name] = dict(buyers=b,rev=rev,orders=o,max=float(mx["mx"] or 0),
        arppu=rev/b if b else 0, opb=o/b if b else 0)
print("\n③b 深海族分件（59服窗内）")
for name,m in out["deepsea_components"].items():
    print(f"   {name}: ${m['rev']:,.0f} 买家{m['buyers']} ARPPU${m['arppu']:.1f} 复购{m['opb']:.1f}单 max${m['max']:,.0f}")

json.dump(out, open(os.path.join(HERE,"_monopoly_deep.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nsaved _monopoly_deep.json")
