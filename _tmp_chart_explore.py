# -*- coding: utf-8 -*-
"""根据截图中看到的路径名，探索 datain-server 的 chart 数据查询接口"""
import requests, json

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
SERVER = "https://datain-server.tap4fun.com"
DASHBOARD_ID = "66ab4f762a840a587f0d8fd4"  # P2节日活动付费数据
WEB_URL = f"https://datain.tap4fun.com/dashboard/{DASHBOARD_ID}"

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
    "referrer-policy": "origin",
}

def get(path, params=None):
    r = requests.get(f"{SERVER}/{path}", headers=H, params=params or {}, timeout=10)
    return r.status_code, r

def post(path, body=None, params=None):
    r = requests.post(f"{SERVER}/{path}", headers=H, json=body or {}, params=params or {}, timeout=30)
    return r.status_code, r

# 1. 截图里见到的路径名
print("=== 截图路径名探索 ===")
for path, p in [
    ("api/game_cd", {"dashboardId": DASHBOARD_ID, "webUrl": WEB_URL}),
    ("api/dimensions", {"dashboardId": DASHBOARD_ID, "webUrl": WEB_URL}),
    ("api/indicators", {"dashboardId": DASHBOARD_ID, "webUrl": WEB_URL}),
    ("api/types", {"dashboardId": DASHBOARD_ID, "webUrl": WEB_URL}),
    ("api/dashboard/game_cd", {"dashboardId": DASHBOARD_ID}),
    ("api/dashboard/dimensions", {"dashboardId": DASHBOARD_ID}),
    ("api/dashboard/indicators", {"dashboardId": DASHBOARD_ID}),
    ("api/dashboard/types", {"dashboardId": DASHBOARD_ID}),
]:
    code, r = get(path, p)
    if code == 200:
        print(f"*** GET {path} → 200  {str(r.json())[:150]}")
    else:
        print(f"    GET {path} → {code}")

# 2. 用 derived-column/all 的路径模式推断相邻端点
print("\n=== derived-column 相关端点 ===")
for path in ["api/derived-column/list", "api/derived-column/query",
             "api/indicator/all", "api/dimension/all", "api/chart/all",
             "api/indicator/list", "api/dimension/list"]:
    code, r = get(path, {"webUrl": WEB_URL})
    if code == 200:
        print(f"*** GET {path} → 200  {str(r.json())[:150]}")
    else:
        print(f"    GET {path} → {code}")

# 3. 找 chart data 端点 - 用 chart ID 当参数
print("\n=== Chart 数据获取（用 chartId 参数）===")
chart9 = "66e25e77be17ff5999d52b86"
for path in ["api/chart/data", "api/chart/result", "api/data/chart",
             "api/query/chart", "api/chart/config", "api/chart/info"]:
    code, r = get(path, {"chartId": chart9, "webUrl": WEB_URL, "dashboardId": DASHBOARD_ID})
    if code not in [404]:
        print(f"*** GET {path} → {code}  {r.text[:150]}")
    else:
        print(f"    GET {path} → 404")

# 4. 用 dashboardId 参数找 dashboard 信息
print("\n=== Dashboard 信息 ===")
for path in ["api/dashboard", "api/dashboard/config", "api/dashboard/charts",
             "api/dashboard/view", "api/view"]:
    code, r = get(path, {"id": DASHBOARD_ID, "webUrl": WEB_URL})
    if code not in [404]:
        print(f"*** GET {path} → {code}  {r.text[:200]}")
    else:
        print(f"    GET {path} → 404")

# 5. 试 POST 各种可能的数据查询端点
print("\n=== POST 数据查询变体 ===")
query_body = {
    "dashboardId": DASHBOARD_ID,
    "chartId": chart9,
    "webUrl": WEB_URL,
    "startTime": "2026-03-13",
    "endTime": "2026-04-02",
    "variables": {"report_date": {"start": "2026-03-13", "end": "2026-04-02"}, "control_id": "%2112%"},
}
for path in ["api/query", "api/data", "api/execute", "api/render",
             "api/dashboard/query", "api/dashboard/data"]:
    code, r = post(path, query_body)
    if code not in [404]:
        print(f"*** POST {path} → {code}  {r.text[:150]}")
    else:
        print(f"    POST {path} → 404")
