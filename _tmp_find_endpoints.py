# -*- coding: utf-8 -*-
"""有了有效token，探索datain-server的实际可用端点"""
import requests, json

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
SERVER = "https://datain-server.tap4fun.com"
WEB_URL = "https://datain.tap4fun.com/dashboard/66ab4f762a840a587f0d8fd4"

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
    "referrer-policy": "origin",
}

def probe(path, method="GET", params=None, body=None):
    try:
        url = f"{SERVER}/{path}"
        p = params or {}
        if "webUrl" not in p:
            p["webUrl"] = WEB_URL
        if method == "GET":
            r = requests.get(url, headers=H, params=p, timeout=10)
        else:
            r = requests.post(url, headers=H, params=p, json=body or {}, timeout=10)
        code = r.status_code
        if code == 200:
            text = str(r.json())[:150]
        else:
            text = r.text[:100]
        return code, text
    except Exception as e:
        return "ERR", str(e)[:60]

# 探索 dashboard 相关的 API
print("=== Dashboard 相关端点 ===")
dashboard_paths = [
    ("api/dashboard/detail", "GET", {"dashboardId": "66ab4f762a840a587f0d8fd4"}),
    ("api/dashboard/info", "GET", {"dashboardId": "66ab4f762a840a587f0d8fd4"}),
    ("api/chart/detail", "GET", {"chartId": "66e25e77be17ff5999d52b86"}),
    ("api/chart/data", "POST", None),
    ("api/chart/execute", "POST", None),
    ("api/chart/run", "POST", None),
    ("api/data/query", "POST", None),
    ("api/report/query", "POST", None),
]
for path, method, params in dashboard_paths:
    code, text = probe(path, method, params)
    mark = "***" if code == 200 else "   "
    print(f"{mark} {method:4} /{path:35s} → {code}  {text[:100] if code==200 else ''}")

# 用 derived-column/all 返回的数据看看能引出什么端点
print("\n=== 分析 derived-column/all 响应 ===")
r = requests.get(f"{SERVER}/api/derived-column/all",
                 headers=H, params={"webUrl": WEB_URL}, timeout=10)
d = r.json()
print(json.dumps(d, ensure_ascii=False, indent=2)[:600])

# 探索 chart 相关的所有变体
print("\n=== Chart 执行端点变体 ===")
chart_body = {
    "chartId": "66e25e77be17ff5999d52b86",
    "dashboardId": "66ab4f762a840a587f0d8fd4",
    "startTime": "2026-03-13",
    "endTime": "2026-04-02",
    "params": {"report_date": {"start": "2026-03-13", "end": "2026-04-02"},
               "control_id": "%2112%", "server_id": "all"},
}
for path in ["api/chart/data", "api/chart/query-data", "api/chart/result",
             "api/chart/preview", "api/visualization/data", "api/analyze/chart",
             "api/dashboard/chart/data"]:
    code, text = probe(path, "POST", body=chart_body)
    mark = "***" if code not in [404, "ERR"] else "   "
    print(f"{mark} POST /{path:35s} → {code}  {text[:80] if code==200 else ''}")

# 探 SQL 执行
print("\n=== SQL 执行端点 ===")
sql_body = {
    "sql": "select 1 as test",
    "gameCd": 1041,
    "startTime": "2026-03-13",
    "endTime": "2026-04-02",
}
for path in ["api/sql/run", "api/sql/exec", "api/query/run", "api/trino/run",
             "api/sql/execute", "api/analysis/run", "api/adhoc/run"]:
    code, text = probe(path, "POST", body=sql_body)
    mark = "***" if code not in [404, "ERR"] else "   "
    print(f"{mark} POST /{path:35s} → {code}")
