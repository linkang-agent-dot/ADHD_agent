# -*- coding: utf-8 -*-
"""
竞猜整体分析数据：参与逐日曲线 + 按轮参与人数（ods_user_asset reason_sub_id 894% 口径）
产出 _jingcai.json
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

END = sys.argv[1] if len(sys.argv) > 1 else "2026-07-15"
HERE = os.path.dirname(os.path.abspath(__file__))
out = {"END": END}

# 参与逐日（去重按日）
rows = execute_sql(f"""SELECT partition_date d, count(distinct user_id) u
    FROM v1090.ods_user_asset WHERE partition_date BETWEEN '2026-06-26' AND '{END}'
    AND cast(reason_sub_id as varchar) LIKE '894%' GROUP BY 1 ORDER BY 1""",
    datasource="TRINO_HF")["data"]
out["daily"] = {r["d"]: r["u"] for r in rows}
print("参与逐日:", {r["d"][5:]: r["u"] for r in rows})

# 按轮参与（窗口与付费按轮一致）
ROUNDS = [("R32", "2026-06-26", "2026-07-02"), ("R16", "2026-07-03", "2026-07-08"),
          ("QF", "2026-07-09", "2026-07-12"), ("SF", "2026-07-13", END)]
out["rounds"] = {}
for rd, a, b in ROUNDS:
    d = execute_sql(f"""SELECT count(distinct user_id) u FROM v1090.ods_user_asset
        WHERE partition_date BETWEEN '{a}' AND '{b}' AND cast(reason_sub_id as varchar) LIKE '894%'""",
        datasource="TRINO_HF")["data"][0]
    out["rounds"][rd] = {"users": d["u"], "win": f"{a}~{b}"}
    print(f"{rd}: 参与 {d['u']:,} 人 ({a}~{b})")

json.dump(out, open(os.path.join(HERE, "_jingcai.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _jingcai.json")
