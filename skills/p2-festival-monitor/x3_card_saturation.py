# -*- coding: utf-8 -*-
"""单卡投放饱和度：按卡名——发放量/消耗量/持有人/人均张数/最深玩家 vs 该卡满级需求。"""
import sys, json, subprocess
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
from collections import defaultdict
SC = r'C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\4320db8b-832c-417d-98a5-f5ada22cbf14\scratchpad'
REPO = r"C:\x3" + "\\" + "gdconfig"
def gitshow(path):
    return subprocess.run(["git","-C",REPO,"show",f"origin/dev:{path}"],capture_output=True).stdout.decode("utf-8",errors="replace")

need = defaultdict(dict)
for ln in gitshow("tsv/MemorialCard__MemorialCardLevel.tsv").split("\n")[5:]:
    c = ln.split("\t")
    if len(c) > 4 and c[2].strip().isdigit() and c[3].strip().isdigit():
        need[c[2].strip()][int(c[3])] = int(c[4])
full = {g: sum(m.values()) for g, m in need.items()}   # 该卡满级累计需求

card2g = {}; cardname = {}
for ln in gitshow("tsv/MemorialCard__MemorialCard.tsv").split("\n")[6:]:
    c = ln.split("\t")
    if len(c) > 9 and c[0].strip().isdigit() and c[9].strip().isdigit():
        iid = str(180000 + int(c[0].strip()))
        card2g[iid] = c[9].strip(); cardname[iid] = c[2].strip()

# 排除建筑卡 180045-180062（剧情一次性，非投放）
cards = [c for c in card2g if not (180045 <= int(c) <= 180062)]
ALL = ",".join(f"'Item_{c}'" for c in cards)

q = f"""
WITH per AS (
  SELECT asset_id, user_id,
    sum(CASE WHEN change_type='1' THEN 1 ELSE 0 END) g
  FROM v1090.ods_user_asset
  WHERE asset_id IN ({ALL}) AND change_type IN ('1','2')
    AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 2010
  GROUP BY 1,2)
SELECT asset_id, sum(g) granted, count_if(g>0) owners,
  round(avg(CASE WHEN g>0 THEN g END),2) avg_g,
  max(g) max_g, approx_percentile(g, 0.99) p99
FROM per GROUP BY 1 ORDER BY granted DESC
"""
r = execute_sql(q, datasource="TRINO_HF", limit=200)["data"]
json.dump(r, open(SC+r'\card_saturation.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

print(f"{'卡名':<20}{'累计发放':>9}{'持有人':>8}{'人均':>7}{'最深玩家':>7}{'满级需':>7}{'人均饱和':>8}{'最深饱和':>8}")
rows = []
for row in r:
    iid = row["asset_id"].replace("Item_","")
    nm = cardname.get(iid, iid)
    fneed = full.get(card2g.get(iid,""), 465)
    sat_avg = (row["avg_g"] or 0)/fneed*100
    sat_max = (row["max_g"] or 0)/fneed*100
    rows.append((nm, row["granted"], row["owners"], row["avg_g"], row["max_g"], fneed, sat_avg, sat_max))
for nm,gr,ow,ag,mg,fn,sa,sm in rows[:22]:
    print(f"{nm:<22}{gr:>9,}{ow:>8,}{ag:>7}{mg:>7}{fn:>7}{sa:>7.1f}%{sm:>7.1f}%")
