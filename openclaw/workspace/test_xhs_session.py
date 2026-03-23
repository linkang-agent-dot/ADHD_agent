import requests

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':1,'method':'initialize',
          'params':{'protocolVersion':'2024-11-05','capabilities':{},
                    'clientInfo':{'name':'openclaw','version':'1.0'}}},
    headers=hdrs)
print('Init:', r1.status_code)

session_id = r1.headers.get('Mcp-Session-Id')
hdrs['Mcp-Session-Id'] = session_id

# 2. initialized
s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','method':'notifications/initialized'},
    headers=hdrs)

# 3. 搜索 - 直接发搜索请求
r3 = s.post('http://localhost:18060/mcp', 
    json={"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_notes","arguments":{"keyword":"旅游","limit":3}}},
    headers=hdrs)
print('Search:', r3.status_code)
print(r3.text[:3000])
