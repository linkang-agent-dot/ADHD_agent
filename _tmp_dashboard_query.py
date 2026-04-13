# -*- coding: utf-8 -*-
"""用 api_key 调用 dashboard 相关端点，获取图表数据"""
import requests, json, os

API_KEY = os.getenv("DATAIN_API_KEY", "")
PUBLIC = "https://datain-api.tap4fun.com"
DASHBOARD_ID = "66ab4f762a840a587f0d8fd4"  # P2节日活动付费数据

H = {"Content-Type": "application/json", "Accept": "application/json"}
P = {"api_key": API_KEY}

def get(path, params=None):
    p = {**P, **(params or {})}
    r = requests.get(f"{PUBLIC}/{path}", headers=H, params=p, timeout=15)
    return r.status_code, r.json() if "json" in r.headers.get("content-type","") else r.text

def post(path, body=None, params=None):
    p = {**P, **(params or {})}
    r = requests.post(f"{PUBLIC}/{path}", headers=H, params=p, json=body or {}, timeout=30)
    return r.status_code, r.json() if "json" in r.headers.get("content-type","") else r.text

# 1. 探索截图中的路径
print("=== 截图路径 + api_key ===")
for path, params in [
    ("public_api/game_cd", {"dashboardId": DASHBOARD_ID}),
    ("public_api/dimensions", {"dashboardId": DASHBOARD_ID}),
    ("public_api/indicators", {"dashboardId": DASHBOARD_ID}),
    ("public_api/types", {"dashboardId": DASHBOARD_ID}),
]:
    code, data = get(path, params)
    if code == 200 and isinstance(data, dict) and data.get("success"):
        d = data.get("data")
        count = len(d) if isinstance(d, list) else "?"
        print(f"*** {path} → OK  count={count}")
        if isinstance(d, list) and d:
            print(f"    first: {json.dumps(d[0], ensure_ascii=False)[:120]}")
        elif isinstance(d, dict):
            print(f"    data: {json.dumps(d, ensure_ascii=False)[:120]}")
    else:
        msg = data.get("message","") if isinstance(data, dict) else str(data)[:80]
        print(f"    {path} → {code} {msg}")

# 2. Dashboard query/data 端点
print("\n=== Dashboard Query 端点 ===")
bodies = [
    ("dashboard/query", {
        "dashboardId": DASHBOARD_ID,
        "startTime": "2026-03-13", "endTime": "2026-04-02",
    }),
    ("dashboard/data", {
        "dashboardId": DASHBOARD_ID,
        "startTime": "2026-03-13", "endTime": "2026-04-02",
    }),
    ("dashboard/refresh", {
        "dashboardId": DASHBOARD_ID,
    }),
]
for path, body in bodies:
    code, data = post(f"public_api/{path}", body)
    print(f"  POST {path} → {code}")
    if code == 200:
        print(f"  data: {json.dumps(data, ensure_ascii=False)[:300]}")
    else:
        print(f"  msg: {str(data)[:150]}")

# 3. 直接用 chartId 查询各图表
print("\n=== 按 chartId 查询图表数据 ===")
chart_ids = {
    "chart5_整体付费": "66b03f3a7f0b225af663fbb5",
    "chart9_各礼包分id": "66e25e77be17ff5999d52b86",
}
for name, chart_id in chart_ids.items():
    print(f"\n--- {name} ---")
    for path in ["public_api/chart/data", "public_api/chart/query-data",
                 "public_api/chart/result"]:
        code, data = get(path, {
            "chartId": chart_id,
            "dashboardId": DASHBOARD_ID,
            "startTime": "2026-03-13",
            "endTime": "2026-04-02",
        })
        if code == 200 and isinstance(data, dict) and data.get("success"):
            print(f"  *** GET {path} → OK  {str(data.get('data'))[:200]}")
        elif code != 404:
            print(f"      GET {path} → {code}  {str(data)[:100]}")

    code, data = post("public_api/chart/data", {
        "chartId": chart_id,
        "dashboardId": DASHBOARD_ID,
        "startTime": "2026-03-13", "endTime": "2026-04-02",
        "variables": {"report_date": {"start": "2026-03-13", "end": "2026-04-02"},
                      "control_id": "%2112%", "server_id": "all"},
    })
    if code == 200 and isinstance(data, dict) and data.get("success"):
        print(f"  *** POST chart/data → OK  {str(data.get('data'))[:200]}")
    elif code != 404:
        print(f"      POST chart/data → {code}  {str(data)[:100]}")
