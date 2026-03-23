import requests
import time

time.sleep(3)  # 等待服务重启

s = requests.Session()
# 1. initialize
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers={'Accept':'application/json, text/event-stream'})
print('Init:', r1.status_code)
# 2. initialized 通知
r2 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers={'Accept':'application/json, text/event-stream'})
print('Notif:', r2.status_code)
# 3. 搜索
r3 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_notes','arguments':{'keyword':'旅游攻略','limit':5}}}, headers={'Accept':'application/json, text/event-stream'})
print('Search:', r3.status_code)
print(r3.text[:2000])
