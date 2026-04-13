# -*- coding: utf-8 -*-
"""用 JWT token 访问 datain-server，执行图表5和图表9的查询"""
import requests, json

TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyNzciLCJpYXQiOjE3NzMxMTEzNzIsImV4cCI6MTc4MDg4NzM3Mn0.aQnLq62fs1ZhB1njB8kPEEe6zL7Hngk6oKvqiPz9hlj9btOwJxGuW6TPVgePydQwV_4KMsGs6O4ayFe64DGhaw"
SERVER = "https://datain-server.tap4fun.com"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://datain.tap4fun.com",
    "Referer": "https://datain.tap4fun.com/",
    "referrer-policy": "origin",
}

# 1. 验证 token
print("=== 1. 验证 token ===")
r = requests.get(f"{SERVER}/api/derived-column/all",
                 params={"webUrl": "https://datain.tap4fun.com/dashboard/66ab4f762a840a587f0d8fd4"},
                 headers=HEADERS, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("Token OK!")
    data = r.json()
    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
else:
    print(r.text[:200])

# 2. 探索 AI-to-SQL 接口
print("\n=== 2. 探索 AI-to-SQL ===")
ai_paths = [
    ("api/ai/text2sql", {"question": "查询2026年3月13日到4月2日，control_id like 2112的节日礼包付费情况，按iap_id分组", "gameId": 1041}),
    ("api/ai/nl2sql", {"question": "查科技节礼包付费", "gameId": 1041}),
    ("api/ai/query", {"question": "科技节付费数据", "gameCd": "1041"}),
    ("api/chat/query", {"message": "查询科技节付费数据", "gameCd": "1041"}),
]
for path, body in ai_paths:
    r = requests.post(f"{SERVER}/{path}", headers=HEADERS, json=body, timeout=10)
    print(f"POST /{path} → {r.status_code}  {r.text[:150]}")

# 3. 直接执行 chart query（图表5：节日整体付费；图表9：各礼包分id）
print("\n=== 3. Chart Query 图表5（节日整体付费）===")
chart5_id = "66b03f3a7f0b225af663fbb5"
body5 = {
    "chartId": chart5_id,
    "params": {
        "report_date": {"start": "2026-03-13", "end": "2026-04-02"},
        "control_id": "%2112%",
        "server_id": "all",
        "schema": "1,2,3,4,5,6",
    }
}
r5 = requests.post(f"{SERVER}/api/chart/query", headers=HEADERS, json=body5, timeout=30)
print(f"Status: {r5.status_code}")
if r5.status_code == 200:
    d = r5.json()
    print(json.dumps(d, ensure_ascii=False, indent=2)[:800])
else:
    print(r5.text[:400])

print("\n=== 4. Chart Query 图表9（各礼包分id）===")
chart9_id = "66e25e77be17ff5999d52b86"
body9 = {
    "chartId": chart9_id,
    "params": {
        "report_date": {"start": "2026-03-13", "end": "2026-04-02"},
        "control_id": "%2112%",
        "server_id": "all",
        "schema": "1,2,3,4,5,6",
    }
}
r9 = requests.post(f"{SERVER}/api/chart/query", headers=HEADERS, json=body9, timeout=30)
print(f"Status: {r9.status_code}")
if r9.status_code == 200:
    d = r9.json()
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1500])
else:
    print(r9.text[:400])
