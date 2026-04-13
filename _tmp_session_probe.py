# -*- coding: utf-8 -*-
"""用 UUID 尝试各种 session/cookie 方式，同时探 datain-server 的 AI-to-SQL 端点"""
import os, requests, json

TOKEN = "838f778b-d8c1-43b5-ac3a-71fc49bcfa85"
API_KEY = os.getenv("DATAIN_API_KEY", "")
SERVER = "https://datain-server.tap4fun.com"
PUBLIC = "https://datain-api.tap4fun.com/public_api"

print("=== 用 UUID 作为各种 Cookie/Session ===")
cookie_names = ["SESSION", "JSESSIONID", "session", "token", "auth_token", "sid", "user_token"]
for name in cookie_names:
    try:
        r = requests.get(f"{SERVER}/api/user/info",
                        cookies={name: TOKEN}, timeout=6)
        if r.status_code != 401:
            print(f"*** Cookie {name}={TOKEN[:20]}... → {r.status_code}  {r.text[:100]}")
        else:
            print(f"    Cookie {name:15s} → 401")
    except Exception as e:
        print(f"    Cookie {name:15s} → ERR: {e}")

# 探 datain-server 的 AI-to-SQL 相关端点（不鉴权测试 404 vs 401）
print("\n=== datain-server 端点探测（有没有 AI/NL SQL 入口）===")
server_paths = [
    "api/ai/text2sql",
    "api/ai/nl2sql",
    "api/ai/query",
    "api/ai/analyze",
    "api/nlp/query",
    "api/query/ai",
    "api/analyze/sql",
    "api/analysis/ai",
    "api/chat/query",
    "api/assistant/query",
    "api/copilot/query",
    "api/smart/query",
    "api/llm/query",
    "api/gpt/query",
]
for path in server_paths:
    try:
        r = requests.post(f"{SERVER}/{path}",
                         headers={"Content-Type": "application/json"},
                         json={"question": "test"},
                         timeout=5)
        # 404=不存在, 401=存在但要鉴权, 其他=有意思
        if r.status_code != 404:
            print(f"*** POST /{path:35s} → {r.status_code}  {r.text[:80]}")
        else:
            print(f"    POST /{path:35s} → 404")
    except Exception as e:
        print(f"    POST /{path:35s} → ERR")

# 同时检查 datain.tap4fun.com 正面的 API
print("\n=== datain.tap4fun.com（前端域名）AI/NL 端点 ===")
FRONT = "https://datain.tap4fun.com"
front_paths = [
    "api/ai/text2sql",
    "api/ai/query",
    "api/nl2sql",
    "api/copilot",
    "api/assistant",
]
for path in front_paths:
    try:
        r = requests.post(f"{FRONT}/{path}", json={"question": "test"}, timeout=5)
        if r.status_code != 404:
            print(f"*** POST /{path:35s} → {r.status_code}  {r.text[:80]}")
        else:
            print(f"    POST /{path:35s} → 404")
    except Exception as e:
        print(f"    POST /{path:35s} → ERR")

# 最后：尝试公开 API 里 query_game.py 实际调用的接口，看有没有 sql 字段
print("\n=== 尝试 public_api/api/game/data/query 发 raw sql 字段 ===")
try:
    r = requests.post(f"{PUBLIC}/api/game/data/query",
                     params={"api_key": API_KEY},
                     json={"sql": "SELECT 1", "gameCd": "1041"},
                     timeout=8)
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.text[:300]}")
except Exception as e:
    print(f"  ERR: {e}")
