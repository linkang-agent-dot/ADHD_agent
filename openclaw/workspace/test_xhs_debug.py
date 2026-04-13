import requests, json

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}
}, headers=hdrs, timeout=10)
print('init headers:', r1.headers)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)

# Test search_feeds
resp = s.post('http://localhost:18060/mcp', json={
    'jsonrpc':'2.0','id':2,'method':'tools/call',
    'params':{'name':'search_feeds','arguments':{'keyword':'旅游'}}
}, headers=hdrs, timeout=30)
print('status:', resp.status_code)
print('text:', resp.text[:500])
