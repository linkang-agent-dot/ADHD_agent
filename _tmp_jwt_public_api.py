# -*- coding: utf-8 -*-
"""用 JWT token 尝试 datain-api.tap4fun.com 的端点"""
import requests, json, os

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
API_KEY = os.getenv("DATAIN_API_KEY", "")
PUBLIC = "https://datain-api.tap4fun.com"
DASHBOARD_ID = "66ab4f762a840a587f0d8fd4"

# 用 JWT 作为 Authorization 头访问 public_api
H_JWT = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
}

print("=== 用 JWT 访问 datain-api.tap4fun.com ===")

# 截图里的路径名（带 dashboardId）
for path, params in [
    ("public_api/game_cd", {"dashboardId": DASHBOARD_ID}),
    ("public_api/dimensions", {"dashboardId": DASHBOARD_ID}),
    ("public_api/indicators", {"dashboardId": DASHBOARD_ID}),
    ("public_api/types", {"dashboardId": DASHBOARD_ID}),
    ("game_cd", {"dashboardId": DASHBOARD_ID}),
    ("dimensions", {"dashboardId": DASHBOARD_ID}),
    ("indicators", {"dashboardId": DASHBOARD_ID}),
    ("types", {"dashboardId": DASHBOARD_ID}),
]:
    r = requests.get(f"{PUBLIC}/{path}", headers=H_JWT, params=params, timeout=8)
    if r.status_code not in [404]:
        print(f"*** GET /{path} → {r.status_code}  {r.text[:150]}")
    else:
        print(f"    GET /{path} → 404")

# 尝试 dashboard 相关的 chart 数据查询
print("\n=== JWT + dashboard chart 数据 ===")
chart9 = "66e25e77be17ff5999d52b86"
chart5 = "66b03f3a7f0b225af663fbb5"

# 用 JWT 访问 dashboard 里的 chart 查询
for path, body in [
    ("public_api/api/game/data/query", {
        "algorithmId": "user_id",
        "gameCds": [1041],
        "startAt": "2026-03-13",
        "endAt": "2026-04-02",
        "indicators": [{"id": "60d412c3e862647e69cfe707", "name": "revenue"}],
        "chartId": chart9,
    }),
]:
    r = requests.post(f"{PUBLIC}/{path}", headers=H_JWT, json=body, timeout=15)
    print(f"POST /{path} → {r.status_code}  {r.text[:200]}")

# 最重要：尝试 dashboard 数据刷新接口
print("\n=== Dashboard 数据刷新 ===")
for path in [
    "public_api/dashboard/query",
    "public_api/dashboard/refresh",
    "public_api/dashboard/data",
    "dashboard/data",
    "dashboard/query",
]:
    r = requests.post(f"{PUBLIC}/{path}", headers=H_JWT,
                     json={"dashboardId": DASHBOARD_ID,
                           "startTime": "2026-03-13", "endTime": "2026-04-02",
                           "variables": {"control_id": "%2112%"}},
                     timeout=10)
    if r.status_code not in [404]:
        print(f"*** POST /{path} → {r.status_code}  {r.text[:200]}")
    else:
        print(f"    POST /{path} → 404")

# 用 JWT 替换 api_key 参数直接执行 game/data/query
print("\n=== JWT 替换 api_key 参数 ===")
body = {
    "algorithmId": "user_id",
    "gameCds": [1041],
    "startAt": "2026-03-13",
    "endAt": "2026-04-02",
    "indicators": [{"id": "60d412c3e862647e69cfe707", "name": "revenue"}],
}
# 方式1: JWT 作为 api_key 查询参数
r1 = requests.post(f"{PUBLIC}/public_api/api/game/data/query",
                   params={"api_key": TOKEN}, json=body, timeout=10)
print(f"api_key=JWT → {r1.status_code}  {r1.text[:150]}")

# 方式2: 同时带 api_key 和 Authorization
r2 = requests.post(f"{PUBLIC}/public_api/api/game/data/query",
                   headers={**H_JWT, "Content-Type": "application/json"},
                   params={"api_key": API_KEY}, json=body, timeout=10)
print(f"api_key+JWT → {r2.status_code}  {r2.text[:150]}")
