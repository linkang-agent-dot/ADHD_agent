# -*- coding: utf-8 -*-
"""探测 Datain Public API 是否有 SQL / AI-to-SQL 端点"""
import os, requests

API_KEY = os.getenv("DATAIN_API_KEY", "")
BASE = "https://datain-api.tap4fun.com/public_api"

headers = {"Authorization": f"Bearer {API_KEY}"}

# 尝试可能的 SQL/AI-to-SQL 路径
paths_to_probe = [
    "sql/execute",
    "sql/run",
    "ai/sql",
    "ai-to-sql",
    "query/sql",
    "trino/execute",
    "chart/sql",
    "analysis/sql",
    "ai/query",
    "nlp/sql",
]

print(f"Base: {BASE}")
print(f"API Key: {'OK' if API_KEY else 'MISSING'}\n")

for path in paths_to_probe:
    try:
        # 先 GET
        r = requests.get(f"{BASE}/{path}", params={"api_key": API_KEY}, timeout=5)
        print(f"GET  /{path:30s}  → {r.status_code}")
    except Exception as e:
        print(f"GET  /{path:30s}  → ERROR: {e}")

print("\n--- 探测 datain-server 是否有公开 SQL 端点 ---")
SERVER = "https://datain-server.tap4fun.com"
server_paths = [
    "api/sql/execute",
    "api/analysis/sql",
    "api/chart/sql",
    "public/sql",
]
for path in server_paths:
    try:
        r = requests.get(f"{SERVER}/{path}", timeout=5)
        print(f"GET  /{path:35s}  → {r.status_code}")
    except Exception as e:
        print(f"GET  /{path:35s}  → ERROR: {str(e)[:60]}")
