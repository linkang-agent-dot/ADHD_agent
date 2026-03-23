import requests
import time

time.sleep(3)

s = requests.Session()

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers={'Accept':'application/json, text/event-stream'})
print('Init:', r1.status_code, r1.text[:200])

# 2. 尝试不同的 notification 格式
r2 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized','params':{}}, headers={'Accept':'application/json, text/event-stream'})
print('Notif2:', r2.status_code, r2.text[:200])

# 3. 先列出可用工具
r_list = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':3,'method':'tools/list','params':{}}, headers={'Accept':'application/json, text/event-stream'})
print('List:', r_list.status_code)
print(r_list.text[:1000])

# 4. 再尝试搜索
r3 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'search_notes','arguments':{'keyword':'旅游','limit':3}}}, headers={'Accept':'application/json, text/event-stream'})
print('Search:', r3.status_code)
print(r3.text[:2000])
