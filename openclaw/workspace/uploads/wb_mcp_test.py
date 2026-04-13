import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:4200/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs)
print(f"微博MCP init状态: {r1.status_code}")
if r1.status_code == 200:
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    s.post('http://localhost:4200/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)
    
    # 列出工具
    resp = s.post('http://localhost:4200/mcp', json={
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}
    }, headers=hdrs)
    print(resp.text[:2000])
