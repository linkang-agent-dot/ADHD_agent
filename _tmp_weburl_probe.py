# -*- coding: utf-8 -*-
"""对所有 /all 端点加 webUrl 参数重试，并找 game_cd 路径"""
import requests, json

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
SERVER = "https://datain-server.tap4fun.com"
DASHBOARD_ID = "66ab4f762a840a587f0d8fd4"
WEB_URL = f"https://datain.tap4fun.com/dashboard/{DASHBOARD_ID}"

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
    "referrer-policy": "origin",
}

def get(path, params=None):
    r = requests.get(f"{SERVER}/{path}", headers=H, params=params or {}, timeout=12)
    return r.status_code, r.json() if r.status_code == 200 else r.text[:200]

# 加 webUrl 重试之前权限不足的端点
print("=== /all 端点加 webUrl 重试 ===")
for path in ["api/indicator/all", "api/dimension/all", "api/indicator/list",
             "api/dimension/list", "api/game/all", "api/tag/all"]:
    code, data = get(path, {"webUrl": WEB_URL})
    if code == 200 and isinstance(data, dict):
        ok = data.get("success")
        msg = data.get("message","")
        items = data.get("data")
        if ok:
            count = len(items) if isinstance(items, list) else "?"
            print(f"*** {path} → OK  count={count}")
            if isinstance(items, list) and items:
                print(f"    first: {json.dumps(items[0], ensure_ascii=False)[:100]}")
        else:
            print(f"    {path} → {code} msg={msg}")
    else:
        print(f"    {path} → {code}")

# 尝试 game_cd 端点（从截图 name 列）
print("\n=== 找 game_cd 端点 ===")
for path in [
    "api/game/game_cd", "api/game-cd", "api/game_cd",
    "api/dashboard/game_cd", "api/dashboard/game-cd",
    "api/chart/game_cd",
]:
    code, data = get(path, {"dashboardId": DASHBOARD_ID, "webUrl": WEB_URL})
    if str(code) != "404":
        print(f"*** {path} → {code}  {str(data)[:150]}")
    else:
        print(f"    {path} → 404")

# 找 SQL/Trino 执行端点 - 用不同的 base path 前缀
print("\n=== SQL 执行 (不同前缀)  ===")
sql = """select iap_id, count(distinct user_id) as cnt, sum(pay_price) as rev
from v1041.ods_user_order
where partition_date between '2026-03-12' and '2026-04-02'
and pay_status = 1
and iap_id in (select iap_id from dim.iap where game_cd=1041 and iap_type='混合-节日活动')
limit 10"""

for path in [
    "api/trino/sql", "api/trino/execute", "api/trino/query",
    "api/custom/sql", "api/custom/query",
    "api/sql", "trino/query", "sql/execute",
    "api/analysis/trino", "api/report/sql",
]:
    r = requests.post(f"{SERVER}/{path}", headers={**H, "Content-Type":"application/json"},
                     json={"sql": sql, "gameCd": 1041, "type": "trino"}, timeout=8)
    if r.status_code not in [404]:
        print(f"*** POST {path} → {r.status_code}  {r.text[:120]}")
    else:
        print(f"    POST {path} → 404")
