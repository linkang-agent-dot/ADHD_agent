import requests, json, sys, time

sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}

r1 = s.post('http://localhost:18060/mcp',
    json={'jsonrpc':'2.0','id':1,'method':'initialize',
          'params':{'protocolVersion':'2024-11-05','capabilities':{},
                     'clientInfo':{'name':'openclaw','version':'1.0'}}},
    headers=hdrs, timeout=10)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
print(f"Session: {hdrs['Mcp-Session-Id']}")

s.post('http://localhost:18060/mcp',
    json={'jsonrpc':'2.0','method':'notifications/initialized'},
    headers=hdrs, timeout=10)

# 获取首页Feeds
resp = s.post('http://localhost:18060/mcp',
    json={'jsonrpc':'2.0','id':2,'method':'tools/call',
          'params':{'name':'list_feeds','arguments':{}}},
    headers=hdrs, timeout=30)
print(resp.text[:3000])
