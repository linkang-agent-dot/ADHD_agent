import requests, json, sys

# 小红书 MCP
s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}

r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)

# 列出可用工具
resp = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}
}, headers=hdrs)
print(resp.text)
