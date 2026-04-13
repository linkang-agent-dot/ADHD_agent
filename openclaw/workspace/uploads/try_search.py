import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)

# 尝试不带过滤条件搜索
resp = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
    'params': {
        'name': 'search_feeds',
        'arguments': {'keyword': '旅游攻略'}
    }
}, headers=hdrs)
print("search_feeds:", resp.text[:3000])
