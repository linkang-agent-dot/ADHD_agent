import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 连接 MediaCrawler MCP
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        break
r.close()
print(f"endpoint: {endpoint}")

# 从 endpoint 提取 session_id
session_id = endpoint.split('session_id=')[1] if 'session_id=' in endpoint else ''
print(f"session_id: {session_id}")

full_url = f'http://127.0.0.1:18080{endpoint}'
hdrs_json = {'Content-Type': 'application/json'}

def mcpcall(tool, args, call_id=10):
    resp = requests.post(full_url, json={
        'jsonrpc': '2.0', 'id': call_id, 'method': 'tools/call',
        'params': {'name': tool, 'arguments': args}
    }, headers=hdrs_json, timeout=60)
    return resp

# 初始化
resp = mcpcall('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1.0'}}, 1)
print("init:", resp.status_code)

# 微博搜索
print("搜索微博...")
resp = mcpcall('crawl_search', {
    'platform': 'wb',
    'store_type': 'json',
    'keywords': '旅游攻略 春季出行'
}, 2)
print(f"wb search status: {resp.status_code}")
print(resp.text[:2000])
