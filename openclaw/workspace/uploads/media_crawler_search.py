import requests, json, time

# 1. 连接 SSE 获取 session_id
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8', errors='ignore')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        break
r.close()

print(f"Endpoint: {endpoint}")

if not endpoint:
    print("SSE连接失败")
    exit()

time.sleep(0.5)

# 2. 搜索小红书五一出游攻略
resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
    'params': {'name': 'crawl_search', 'arguments': {
        'platform': 'xhs',
        'store_type': 'json',
        'keywords': '五一机票好价 往返直飞'
    }}
}, timeout=60)

print(resp.text[:5000])
