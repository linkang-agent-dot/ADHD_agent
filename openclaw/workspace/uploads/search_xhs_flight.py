import requests, json

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 
          'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 
                     'clientInfo': {'name': 'openclaw', 'version': '1.0'}}},
    headers=hdrs, timeout=10)

hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
print(f"Session ID: {hdrs['Mcp-Session-Id']}")

# 2. initialized 通知
r2 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc': '2.0', 'method': 'notifications/initialized'},
    headers=hdrs, timeout=10)
print(f"Initialized: {r2.status_code}")

# 3. 搜索五一直飞好价机票
resp = s.post('http://localhost:18060/mcp',
    json={'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
          'params': {'name': 'search_notes', 'arguments': {
              'keyword': '五一出游机票好价往返直飞',
              'page': 1,
              'page_size': 10
          }}},
    headers=hdrs, timeout=30)

print(resp.text[:5000])
