# -*- coding: utf-8 -*-
"""单卡等级修正版：每人每张卡的消耗→该卡等级（曲线按卡所属组）。"""
import sys, json, subprocess
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
SC = r'C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\4320db8b-832c-417d-98a5-f5ada22cbf14\scratchpad'
from collections import defaultdict

REPO = r"C:\x3" + "\\" + "gdconfig"
def gitshow(path):
    return subprocess.run(["git","-C",REPO,"show",f"origin/dev:{path}"],capture_output=True).stdout.decode("utf-8",errors="replace")

need = defaultdict(dict)
for ln in gitshow("tsv/MemorialCard__MemorialCardLevel.tsv").split("\n")[5:]:
    c = ln.split("\t")
    if len(c) > 4 and c[2].strip().isdigit() and c[3].strip().isdigit():
        need[c[2].strip()][int(c[3])] = int(c[4])
cum = {}
for g, m in need.items():
    acc = 0; lst = []
    for lv in sorted(m): acc += m[lv]; lst.append((lv, acc))
    cum[g] = lst

card2g = {}; cardname = {}
for ln in gitshow("tsv/MemorialCard__MemorialCard.tsv").split("\n")[6:]:
    c = ln.split("\t")
    if len(c) > 9 and c[0].strip().isdigit() and c[9].strip().isdigit():
        iid = str(180000 + int(c[0].strip()))
        card2g[iid] = c[9].strip(); cardname[iid] = c[2].strip()

def lvl_case(g):
    return "CASE " + " ".join(f"WHEN c >= {acc} THEN {lv}" for lv, acc in reversed(cum[g])) + " ELSE 0 END"
gcase = "CASE " + " ".join(
    f"WHEN asset_id IN ({','.join(chr(39)+'Item_'+cid+chr(39) for cid,gg in card2g.items() if gg==g)}) THEN ({lvl_case(g)})"
    for g in sorted(set(card2g.values()))) + " ELSE 0 END"
ALL = ",".join(f"'Item_{c}'" for c in card2g)

base = f"""
WITH cons AS (
  SELECT user_id, asset_id, count(1) c
  FROM v1090.ods_user_asset
  WHERE asset_id IN ({ALL}) AND change_type='2'
    AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 2010
  GROUP BY 1,2),
lv AS (SELECT user_id, asset_id, {gcase} lvl FROM cons)
"""
qa = base + """
SELECT asset_id, CASE WHEN lvl=0 THEN '0' WHEN lvl<=2 THEN '1-2' WHEN lvl<=4 THEN '3-4'
  WHEN lvl<=6 THEN '5-6' WHEN lvl<=9 THEN '7-9' WHEN lvl<=14 THEN '10-14' ELSE '15+' END band, count(1) users
FROM lv GROUP BY 1,2"""
ra = execute_sql(qa, datasource="TRINO_HF", limit=800)["data"]
qb = base + """
, u AS (SELECT user_id, max(lvl) ml FROM lv GROUP BY 1)
, p AS (SELECT DISTINCT user_id FROM v1090.ods_user_order WHERE pay_status=1)
SELECT u.ml lvl, CASE WHEN p.user_id IS NOT NULL THEN 'payer' ELSE 'free' END pf, count(1) users
FROM u LEFT JOIN p ON u.user_id=p.user_id GROUP BY 1,2 ORDER BY 1,2"""
rb = execute_sql(qb, datasource="TRINO_HF", limit=200)["data"]

json.dump({"per_card": ra, "maxlvl_pay": rb, "cardname": cardname}, open(SC+r'\card_levels_single.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

BANDS = ["1-2","3-4","5-6","7-9","10-14","15+"]
tbl = defaultdict(dict)
for r in ra: tbl[r["asset_id"]][r["band"]] = r["users"]
def owners(a): return sum(v for k,v in tbl[a].items() if k!="0")
tops = sorted(tbl, key=owners, reverse=True)
FOCUS = ["Item_180077","Item_180078","Item_180079","Item_180080","Item_180041","Item_180005"]
print("=== 单卡等级分布（节日卡+常驻头部）===")
print(f"{'卡':<26}{'升过级人数':>9}{'1-2级':>8}{'3-4':>7}{'5-6':>7}{'7-9':>7}{'10-14':>7}{'15+':>6}")
for a in FOCUS + [t for t in tops[:8] if t not in FOCUS]:
    nm = cardname.get(a.replace("Item_",""), a)
    row = tbl.get(a, {})
    print(f"{nm:<28}{owners(a):>8,}" + "".join(f"{row.get(b,0):>7,}" for b in BANDS))
print("\n=== 玩家最高单卡等级 × 付费 ===")
agg = defaultdict(lambda: {"payer":0,"free":0})
for r in rb: agg[int(r["lvl"])][r["pf"]] = r["users"]
for lvl in sorted(agg):
    if lvl == 0: continue
    v=agg[lvl]; print(f"  Lv{lvl:>2}: payer {v['payer']:>7,}  free {v['free']:>8,}")
