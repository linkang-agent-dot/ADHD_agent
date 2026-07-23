# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql
def q(s): return execute_sql(s, datasource="TRINO_HF")["data"]
# 签到精确探：activityCfgID 精确 101406 / 1406 / 20260... ; type=0 的 actvType 分布
for pat in ['"activityCfgID":101406','"activityCfgID":1406']:
    try:
        r=q(f"""SELECT activity_type, count(1) n, count(distinct user_id) u FROM v1090.ods_user_activity
            WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND attribute1 LIKE '%{pat}%'
            GROUP BY activity_type ORDER BY n DESC LIMIT 6""")
        print(f"[{pat}] -> {[(x['activity_type'],x['n'],x['u']) for x in r]}")
    except Exception as e: print(pat,"ERR",str(e)[:120])
# type=0 里 actvType 分布(看签到是不是某个actvType)
try:
    r=q("""SELECT regexp_extract(attribute1,'"actvType":(\d+)',1) at, count(distinct activity_cfg) FROM
        (SELECT attribute1, regexp_extract(attribute1,'"activityCfgID":(\d+)',1) activity_cfg FROM v1090.ods_user_activity
         WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND activity_type=0) GROUP BY 1 ORDER BY 1 LIMIT 30""")
    print("type=0 actvType 分布:", [(x['at']) for x in r])
except Exception as e: print("actvType ERR", str(e)[:150])
# 签到=Type14, 探 type=0 actvType:14 的 cfg 列表
try:
    r=q("""SELECT regexp_extract(attribute1,'"activityCfgID":(\d+)',1) cfg, count(distinct user_id) u FROM v1090.ods_user_activity
        WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-16' AND activity_type=0 AND attribute1 LIKE '%"actvType":14%'
        GROUP BY 1 ORDER BY u DESC LIMIT 15""")
    print("actvType:14(签到) 各cfg人数:", [(x['cfg'],x['u']) for x in r])
except Exception as e: print("t14 ERR", str(e)[:150])
