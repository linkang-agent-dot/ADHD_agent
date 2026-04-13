# -*- coding: utf-8 -*-
"""全面探测 Datain Public API 可用端点"""
import os, requests, json

API_KEY = os.getenv("DATAIN_API_KEY", "")
BASE = "https://datain-api.tap4fun.com/public_api"

def probe(path, method="GET", body=None):
    try:
        if method == "GET":
            r = requests.get(f"{BASE}/{path}", params={"api_key": API_KEY}, timeout=8)
        else:
            r = requests.post(f"{BASE}/{path}", params={"api_key": API_KEY}, json=body or {}, timeout=8)
        code = r.status_code
        text = r.text[:200].replace("\n", " ")
        return code, text
    except Exception as e:
        return "ERR", str(e)[:80]

# 从 query_game.py 里推断已知可用路径
known = [
    ("common/game/list", "GET"),
    ("common/indicator/list", "GET"),
    ("common/dimension/list", "GET"),
    ("common/tag/list", "GET"),
    ("game/query", "POST"),
    ("game/query/dimension/values", "GET"),
    ("material/query", "POST"),
]

print("=== 已知可用路径 ===")
for path, m in known:
    code, text = probe(path, m)
    print(f"{m:4} /{path:40s} → {code}")

# 探索可能的 AI-to-SQL 或自定义 SQL 路径
print("\n=== 探索 AI/SQL 相关路径 ===")
candidates = [
    ("ai/query", "POST"),
    ("ai/sql", "POST"),
    ("custom/sql", "POST"),
    ("custom/query", "POST"),
    ("trino/query", "POST"),
    ("chart/execute", "POST"),
    ("analysis/query", "POST"),
    ("game/sql", "POST"),
    ("adhoc/query", "POST"),
    ("nlp/query", "POST"),
    ("query/ai", "POST"),
    ("game/analyze", "POST"),
    ("analyze", "POST"),
    # 尝试 swagger/openapi 文档
    ("swagger-ui.html", "GET"),
    ("v3/api-docs", "GET"),
    ("swagger.json", "GET"),
    ("openapi.json", "GET"),
    ("docs", "GET"),
]

for path, m in candidates:
    code, text = probe(path, m, body={"sql": "SELECT 1", "game_cd": "1041"})
    if str(code) != "404":
        print(f"*** {m:4} /{path:40s} → {code}  {text[:100]}")
    else:
        print(f"    {m:4} /{path:40s} → {code}")

# 尝试 datain.tap4fun.com 的 API (不是 datain-api)
print("\n=== 探索 datain.tap4fun.com/api/ ===")
BASE2 = "https://datain.tap4fun.com"
paths2 = [
    "api/ai/sql",
    "api/ai/query",
    "api/nl2sql",
    "api/nlsql",
    "api/custom/sql",
    "api/adhoc",
]
for path in paths2:
    try:
        r = requests.post(f"{BASE2}/{path}",
                         headers={"Authorization": f"Bearer {API_KEY}"},
                         json={"question": "test", "game_cd": "1041"},
                         timeout=6)
        print(f"POST /{path:35s} → {r.status_code}  {r.text[:80]}")
    except Exception as e:
        print(f"POST /{path:35s} → ERR: {str(e)[:60]}")
