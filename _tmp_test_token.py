# -*- coding: utf-8 -*-
"""测试 session token 是否能访问 datain-server"""
import requests, json

TOKEN = "838f778b-d8c1-43b5-ac3a-71fc49bcfa85"
SERVER = "https://datain-server.tap4fun.com"

headers_variants = [
    {"Authorization": f"Bearer {TOKEN}"},
    {"Authorization": TOKEN},
    {"token": TOKEN},
    {"x-token": TOKEN},
    {"Cookie": f"token={TOKEN}"},
]

# 先试一个轻量接口
test_paths = [
    "api/user/info",
    "api/chart/list",
    "api/dashboard/list",
    "api/common/indicator/list",
]

print("=== 测试不同 Header 方式 ===")
for h in headers_variants:
    try:
        r = requests.get(f"{SERVER}/api/user/info", headers=h, timeout=8)
        body = r.text[:200]
        print(f"Header {list(h.keys())[0]:25s}  → {r.status_code}  {body[:100]}")
    except Exception as e:
        print(f"Header {list(h.keys())[0]:25s}  → ERROR: {e}")

print("\n=== 尝试执行图表9 SQL（control_id=%2112%，科技节）===")
# 图表 9：节日活动各礼包付费情况（chart ID: 66e25e77be17ff5999d52b86）
chart_id = "66e25e77be17ff5999d52b86"
params_payload = {
    "report_date": {"start": "2026-03-13", "end": "2026-04-02"},
    "control_id": "%2112%",
    "server_id": "all",
    "schema": "1,2,3,4,5,6",
}

for h in [{"Authorization": f"Bearer {TOKEN}"}, {"token": TOKEN}]:
    try:
        r = requests.post(
            f"{SERVER}/api/chart/query",
            headers={**h, "Content-Type": "application/json"},
            json={"chartId": chart_id, "params": params_payload},
            timeout=15,
        )
        print(f"\nPOST chart/query ({list(h.keys())[0]}) → {r.status_code}")
        print(r.text[:300])
    except Exception as e:
        print(f"ERROR: {e}")
