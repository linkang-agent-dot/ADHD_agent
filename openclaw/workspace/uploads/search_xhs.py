import requests, json

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1,
    'method': 'initialize',
    'params': {
        'protocolVersion': '2024-11-05',
        'capabilities': {},
        'clientInfo': {'name': 'openclaw', 'version': '1.0'}
    }
}, headers=hdrs)

if r1.status_code != 200:
    print(f"初始化失败: {r1.status_code} {r1.text}")
    exit(1)

hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']

# 2. initialized 通知
s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'method': 'notifications/initialized'
}, headers=hdrs)

# 3. 搜索小红书旅游攻略
resp = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 2,
    'method': 'tools/call',
    'params': {
        'name': 'search_notes',
        'arguments': {
            'keyword': '旅游攻略',
            'limit': 10
        }
    }
}, headers=hdrs)

print(resp.text)
