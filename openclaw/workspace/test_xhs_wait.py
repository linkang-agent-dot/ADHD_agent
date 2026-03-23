import requests
import time

# 关键：使用同一个session对象，并且等待足够时间
s = requests.Session()

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':1,'method':'initialize',
          'params':{'protocolVersion':'2024-11-05','capabilities':{},
                    'clientInfo':{'name':'test','version':'1.0'}}},
    headers={'Accept': 'application/json, text/event-stream'})
print('Init:', r1.status_code, r1.text[:200])

# 关键：等待
time.sleep(2)

# 2. notifications/initialized
r2 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','method':'notifications/initialized'},
    headers={'Accept': 'application/json, text/event-stream'})
print('Notif:', r2.status_code)

# 再等待
time.sleep(1)

# 3. 搜索
r3 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':2,'method':'tools/call',
          'params':{'name':'search_notes','arguments':{'keyword':'旅游攻略','limit':5}}},
    headers={'Accept': 'application/json, text/event-stream'})
print('Search:', r3.status_code)
print('Result:', r3.text[:3000])
