import requests
import json
import re

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

# 3. 列出工具
r = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':3,'method':'tools/list','params':{}},
    headers=hdrs)

# 提取所有工具名
data = json.loads(r.text)
tools = data.get('result', {}).get('tools', [])
print('Available tools:')
for t in tools:
    print(f"  - {t['name']}")
